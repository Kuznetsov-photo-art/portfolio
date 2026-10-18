/* Lab4U hero v21 — the microscope from Blender as live 3D (three.js), loaded only with ?hero=microscope.
   The page's hero loop drives it: window.__m3d(p, dt, yaw, pit) each frame, p = the scan pass 0…1.
   The model turns slowly and leans toward the pointer, the beam from the working objective walks across the slide
   and lights the sample points, the nosepiece swaps objectives each pass. Build: npm run build → cases/lab4u/3d/m3d.min.js */
import { WebGLRenderer, Scene, PerspectiveCamera, DirectionalLight, HemisphereLight, Mesh, PlaneGeometry, ShadowMaterial, PMREMGenerator, Group,
  CylinderGeometry, MeshBasicMaterial, Color, AgXToneMapping, SRGBColorSpace, PCFShadowMap, AdditiveBlending, Vector3 } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';

const hero = document.getElementById('hero'), cv = document.getElementById('m3d'), box = hero && hero.querySelector('.h-viz');
const rm = matchMedia('(prefers-reduced-motion:reduce)').matches;
/* no WebGL or no model → the page falls back to the sphere */
const fail = e => { if (e) console.warn('m3d:', e); window.__m3dFail = true; hero && hero.classList.remove('hv-big'); cv && cv.remove(); };
if (!cv || !box) fail(); else init().catch(fail);

async function init() {
  const R = new WebGLRenderer({ canvas: cv, alpha: true, antialias: true, powerPreference: 'high-performance' });
  R.toneMapping = AgXToneMapping; R.outputColorSpace = SRGBColorSpace; R.shadowMap.enabled = true; R.shadowMap.type = PCFShadowMap;
  const S = new Scene(), pm = new PMREMGenerator(R);
  S.environment = pm.fromScene(new RoomEnvironment(), .04).texture; S.environmentIntensity = .55; /* reflections for the chrome and the coat */

  /* light as in the Blender scene: a key from the upper left, a cool rim from behind, a soft fill */
  const key = new DirectionalLight(0xffffff, 2.6); key.position.set(-5, 7, 6); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -3.2, right: 3.2, top: 3.2, bottom: -3.2, near: 2, far: 22 }); key.shadow.radius = 7; key.shadow.bias = -.0004; key.shadow.normalBias = .02;
  const rim = new DirectionalLight(0xbfe5ff, 2); rim.position.set(5, 5, -6);
  const fill = new DirectionalLight(0xffffff, .5); fill.position.set(7, 1.5, 3);
  S.add(key, rim, fill, new HemisphereLight(0xffffff, 0x1a1a1a, .35));
  /* a floor that only shows the shadow */
  const floorM = new ShadowMaterial({ opacity: .5 }), floor = new Mesh(new PlaneGeometry(16, 16), floorM);
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; S.add(floor);

  const ld = new GLTFLoader(); ld.setMeshoptDecoder(MeshoptDecoder);
  const M = (await ld.loadAsync(cv.dataset.src)).scene;
  M.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  const spin = new Group(); spin.add(M); S.add(spin);

  /* the nosepiece turns round its own axis; each objective's band is lit by how close it is to the working position */
  const nose = M.getObjectByName('Nosepiece');
  const CY = new Color(0x00b6d3), DK = new Color(0x0b0c0d);
  const bands = [1, 2, 3].map(i => { let b = null; const o = M.getObjectByName('Objective' + i);
    o && o.traverse(m => { if (m.isMesh && /^Band/.test(m.material.name)) { m.material = m.material.clone(); b = m.material; } }); return b; });

  /* the beam (a fine core and a soft glow) and the sample points sit in the model's own frame */
  const beamM = new MeshBasicMaterial({ color: 0x19c6e2, transparent: true, opacity: .95, blending: AdditiveBlending, depthWrite: false });
  const glowM = beamM.clone(); glowM.opacity = .16;
  const tube = new CylinderGeometry(1, 1, 1, 16, 1, true); tube.translate(0, .5, 0);
  const beam = new Mesh(tube, beamM), glow = new Mesh(tube, glowM); M.add(beam, glow);
  const dotG = new CylinderGeometry(.03, .03, .006, 20), dots = [];
  for (let k = 0; k < 12; k++) { const d = new Mesh(dotG, new MeshBasicMaterial({ color: 0xffffff, transparent: true }));
    d.position.set(-.4 + k * .8 / 11, 1.249, .2 + ((k % 3) - 1) * .07); M.add(d); dots.push(d); }
  const WRN = new Color(0xe58a00), ON = new Color(0x0592d2), OFF = new Color(0x5a8a94); /* read points: Lab4U blue, ferritin amber; unread: grey-teal */

  const D = 11.2, cam = new PerspectiveCamera(22, 1, .5, 60), T = new Vector3(0, 1.78, 0), up = new Vector3(0, 1, 0), dir = new Vector3();
  /* the canvas covers the whole hero (nothing gets cut); the projection centre sits on the right column (cx, cy), ppu = pixels per model unit */
  const fit = () => { const hr = hero.getBoundingClientRect(), r = box.getBoundingClientRect(), m = innerWidth <= 860, W = hero.clientWidth, H = hero.clientHeight;
    const cx = r.left - hr.left + r.width * (m ? .5 : .47), cy = m ? r.top - hr.top + r.height * .47 : H * .43, ppu = m ? r.height * .27 : H * .185;
    const FW = 2 * Math.max(cx, W - cx), FH = 2 * Math.max(cy, H - cy);
    Object.assign(cv.style, { left: 0, top: 0, width: W + 'px', height: H + 'px' });
    R.setPixelRatio(Math.min(2, devicePixelRatio || 1)); R.setSize(W, H, false);
    cam.fov = 2 * Math.atan(FH / (2 * ppu * D)) * 180 / Math.PI; cam.aspect = FW / FH; cam.setViewOffset(FW, FH, FW / 2 - cx, FH / 2 - cy, W, H); cam.updateProjectionMatrix(); };
  fit();

  let t = 0, tn = 0, tg = 0, lastP = 0, args = [1, 0, 0, 0];
  const act = i => { const a = (((tn + i * 2.0944) % 6.2832) + 6.2832) % 6.2832; return Math.max(0, 1 - Math.min(a, 6.2832 - a) / .5); };
  const frame = (p, dt, yaw, pit) => { args = [p, 0, yaw, pit]; t += dt;
    if (p < lastP - .5) tg += 2.0944; lastP = p; tn += (tg - tn) * (1 - Math.pow(.02, dt)); if (nose) nose.rotation.y = tn;
    spin.rotation.y = -1.08 + t * .22 + yaw * .6; /* starts at the Blender hero angle (the right side toward the viewer) */
    const el = .26 + pit * .35; cam.position.set(0, T.y + Math.sin(el) * D, Math.cos(el) * D); cam.lookAt(T);
    const dark = document.body.classList.contains('dark'); floorM.opacity = dark ? .6 : .2;
    let wi = 0; bands.forEach((b, i) => { if (!b) return; const a = act(i); if (a > act(wi)) wi = i; b.color.copy(DK).lerp(CY, a); b.emissive.copy(CY).multiplyScalar(a * .35); });
    /* the beam: from the working objective's tip down to the point it reads */
    const k = act(wi), tip = new Vector3(0, 1.82, .2), at = new Vector3(-.4 + .8 * p, 1.247, .2);
    dir.subVectors(tip, at); const L = dir.length(); dir.normalize();
    for (const [m, r] of [[beam, .006], [glow, .03]]) { m.position.copy(at); m.quaternion.setFromUnitVectors(up, dir); m.scale.set(r, L, r); m.visible = k > .6 && p > 0 && p < 1; }
    beamM.opacity = .95 * (.65 + .35 * Math.sin(t * 7));
    dots.forEach((d, i) => { const on = i / 11 <= p; d.material.color.copy(on ? (i === 1 ? WRN : ON) : OFF); d.material.opacity = on ? 1 : .45; });
    R.render(S, cam);
    if (!cv.classList.contains('on')) cv.classList.add('on'); };

  window.__m3d = frame;
  new ResizeObserver(() => { fit(); frame(...args); }).observe(hero);
  if (rm) frame(1, 0, 0, 0);
}
