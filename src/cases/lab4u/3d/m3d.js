/* Lab4U hero v22 — the microscope from Blender as live 3D (three.js), loaded only with ?hero=microscope.
   The page's hero loop drives it: window.__m3d(p, dt, yaw, pit) each frame, p = the scan pass 0…1.
   The model turns slowly and leans toward the pointer, the nosepiece swaps objectives each pass; the slide is real glass;
   in the dark theme the body is gloss black; everything is glossy and lit like a product shot (Andrey, 18.10). Build: npm run build → cases/lab4u/3d/m3d.min.js */
import { WebGLRenderer, Scene, PerspectiveCamera, DirectionalLight, Mesh, PlaneGeometry, BoxGeometry, ShadowMaterial, PMREMGenerator, Group,
  MeshBasicMaterial, MeshPhysicalMaterial, Color, AgXToneMapping, SRGBColorSpace, PCFShadowMap, BackSide, DoubleSide, Vector3 } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
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
  /* a photo studio for the reflections: a dark (or light grey) room with softboxes — gloss shows as crisp highlights, not a grey film */
  const studio = light => { const e = new Scene();
    e.add(new Mesh(new BoxGeometry(40, 24, 40), new MeshBasicMaterial({ color: light ? 0x4a4d52 : 0x1c1d21, side: BackSide })));
    const box = (w, h, c, k, pos) => { const m = new Mesh(new PlaneGeometry(w, h), new MeshBasicMaterial({ color: new Color(c).multiplyScalar(k), side: DoubleSide }));
      m.position.set(...pos); m.lookAt(0, 2, 0); e.add(m); };
    box(12, 5, 0xffffff, light ? 3 : 4, [0, 11, 1]);         /* the big top softbox */
    box(2.2, 11, 0xffffff, light ? 2 : 3.2, [-11, 5, 5]);    /* a strip on the key side */
    box(2.2, 11, 0xd2ecff, light ? 1.6 : 3, [11, 5, -7]);    /* a cool rim strip behind */
    box(10, 2, 0xffffff, light ? 1 : .7, [2, 1.5, 13]);      /* a low fill in front */
    box(16, 3.5, 0xffffff, light ? 2.6 : 1.3, [0, 2.5, -14]);  /* a wide strip behind, low: horizontal surfaces (base, stage) catch it */
    return pm.fromScene(e, .02).texture; };
  const ENV = { light: studio(true), dark: studio(false) };

  /* light as in the Blender scene: a key from the upper left, a cool rim from behind, a soft fill */
  const key = new DirectionalLight(0xffffff, 2.6); key.position.set(-5, 7, 6); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -3.2, right: 3.2, top: 3.2, bottom: -3.2, near: 2, far: 22 }); key.shadow.radius = 7; key.shadow.bias = -.0004; key.shadow.normalBias = .02;
  const rim = new DirectionalLight(0xbfe5ff, 2); rim.position.set(5, 5, -6);
  const fill = new DirectionalLight(0xffffff, .5); fill.position.set(7, 1.5, 3);
  S.add(key, rim, fill);
  /* a floor that only shows the shadow */
  const floorM = new ShadowMaterial({ opacity: .5 }), floor = new Mesh(new PlaneGeometry(16, 16), floorM);
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; S.add(floor);

  const ld = new GLTFLoader(); ld.setMeshoptDecoder(MeshoptDecoder);
  const M = (await ld.loadAsync(cv.dataset.src)).scene;
  /* materials, made glossy and real: lacquered body, polished chrome, anodised metal under a clear coat; the slide is real glass
     (clear, refracting, a faint green in its thickness like soda-lime glass) */
  const glass = new MeshPhysicalMaterial({ name: 'Slide', color: 0xffffff, metalness: 0, roughness: .02, transmission: 1, thickness: .06, ior: 1.52,
    attenuationColor: new Color(0xb9e6d2), attenuationDistance: .35, specularIntensity: 1, envMapIntensity: 1.5 });
  const LOOK = { Enamel: { roughness: .14, metalness: 0, clearcoat: 1, clearcoatRoughness: .02 }, Anodized: { roughness: .2, metalness: .55, clearcoat: .8, clearcoatRoughness: .04 },
    Chrome: { roughness: .03, metalness: 1 }, Band: { roughness: .14, metalness: .4, clearcoat: 1, clearcoatRoughness: .03 }, BandActive: { roughness: .14, metalness: .2, clearcoat: 1, clearcoatRoughness: .03 } };
  const made = new Map(), phys = m => { if (m.name === 'Slide') return glass; if (made.has(m)) return made.get(m);
    const n = new MeshPhysicalMaterial({ name: m.name, color: m.color, metalness: m.metalness, roughness: m.roughness, emissive: m.emissive, emissiveIntensity: m.emissiveIntensity, ...(LOOK[m.name] || {}) });
    made.set(m, n); return n; };
  M.traverse(o => { if (!o.isMesh) return; o.castShadow = o.material.name !== 'Slide'; o.receiveShadow = true; o.material = phys(o.material); });
  /* body colour by theme: light grey lacquer in the light theme, gloss black in the dark one */
  const EN = [...made.values()].filter(m => m.name === 'Enamel').map(m => ({ m, c: m.color.clone() }));
  const BLACK = new Color(0x0e0f11); let themeDark = null; /* a lifted black: the lacquer must read lighter than the #0A0A0A page (Andrey, 18.10) */
  const theme = dark => { themeDark = dark; EN.forEach(e => e.m.color.copy(dark ? BLACK : e.c));
    S.environment = dark ? ENV.dark : ENV.light; S.environmentIntensity = 1;
    R.toneMappingExposure = dark ? 1.3 : 1.12; rim.intensity = dark ? 3 : 1.4; key.intensity = dark ? 2.6 : 2.3; fill.intensity = dark ? .6 : .5; floorM.opacity = dark ? .6 : .2; };
  const spin = new Group(); spin.add(M); S.add(spin);

  /* the nosepiece turns round its own axis; each objective's band is lit by how close it is to the working position */
  const nose = M.getObjectByName('Nosepiece');
  const CY = new Color(0x00b6d3), DK = new Color(0x0b0c0d);
  const bands = [1, 2, 3].map(i => { let b = null; const o = M.getObjectByName('Objective' + i);
    o && o.traverse(m => { if (m.isMesh && /^Band/.test(m.material.name)) { m.material = m.material.clone(); b = m.material; } }); return b; });

  const D = 11.2, cam = new PerspectiveCamera(22, 1, .5, 60), T = new Vector3(0, 1.78, 0);
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
    const dark = document.body.classList.contains('dark'); if (dark !== themeDark) theme(dark);
    bands.forEach((b, i) => { if (!b) return; const a = act(i); b.color.copy(DK).lerp(CY, a); b.emissive.copy(CY).multiplyScalar(a * .35); });
    R.render(S, cam);
    if (!cv.classList.contains('on')) cv.classList.add('on'); };

  window.__m3d = frame;
  new ResizeObserver(() => { fit(); frame(...args); }).observe(hero);
  if (rm) frame(1, 0, 0, 0);
}
