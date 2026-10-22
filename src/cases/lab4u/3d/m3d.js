/* Lab4U hero v22 — the microscope from Blender as live 3D (three.js), loaded only with ?hero=microscope.
   The page's hero loop drives it: window.__m3d(p, dt, yaw, pit) each frame, p = the scan pass 0…1.
   The model turns slowly and leans toward the pointer; the tilted nosepiece swaps objectives each pass and the working one sends
   a blue beam to one fixed point on the slide (every objective turned in aims at the same point, as on a real microscope); the slide is real glass;
   in the dark theme the body is gloss black; everything is glossy and lit like a product shot (Andrey, 18.10). Build: npm run build → cases/lab4u/3d/m3d.min.js */
import { WebGLRenderer, Scene, PerspectiveCamera, DirectionalLight, Mesh, PlaneGeometry, BoxGeometry, ShadowMaterial, PMREMGenerator, Group,
  MeshBasicMaterial, MeshPhysicalMaterial, CylinderGeometry, CircleGeometry, Color, AgXToneMapping, SRGBColorSpace, VSMShadowMap, BackSide, DoubleSide, Vector3 } from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js';

const hero = document.getElementById('hero'), cv = document.getElementById('m3d'), box = hero && hero.querySelector('.h-viz');
const rm = matchMedia('(prefers-reduced-motion:reduce)').matches;
/* no WebGL or no model → the page falls back to the sphere */
const fail = e => { if (e) console.warn('m3d:', e); window.__m3dFail = true; hero && hero.classList.remove('hv-big'); cv && cv.remove(); };
if (!cv || !box) fail(); else init().catch(fail);

async function init() {
  const R = new WebGLRenderer({ canvas: cv, alpha: true, antialias: true, powerPreference: 'high-performance' });
  R.toneMapping = AgXToneMapping; R.outputColorSpace = SRGBColorSpace; R.shadowMap.enabled = true; R.shadowMap.type = VSMShadowMap; /* soft, well-diffused shadows */
  const S = new Scene(), pm = new PMREMGenerator(R);
  /* a photo studio for the reflections: a dark (or light grey) room with softboxes — gloss shows as crisp highlights, not a grey film */
  const studio = (light, room) => { const e = new Scene();
    e.add(new Mesh(new BoxGeometry(40, 24, 40), new MeshBasicMaterial({ color: room ?? (light ? 0x8d9095 : 0x1c1d21), side: BackSide })));
    const box = (w, h, c, k, pos) => { const m = new Mesh(new PlaneGeometry(w, h), new MeshBasicMaterial({ color: new Color(c).multiplyScalar(k), side: DoubleSide }));
      m.position.set(...pos); m.lookAt(0, 2, 0); e.add(m); };
    box(12, 5, 0xffffff, light ? 3 : 4, [0, 11, 1]);         /* the big top softbox */
    box(2.2, 11, 0xffffff, light ? 2 : 3.2, [-11, 5, 5]);    /* a strip on the key side */
    box(2.2, 11, 0xd2ecff, light ? 1.6 : 3, [11, 5, -7]);    /* a cool rim strip behind */
    box(10, 2, 0xffffff, light ? 1 : .7, [2, 1.5, 13]);      /* a low fill in front */
    box(16, 3.5, 0xffffff, light ? 2.6 : 1.3, [0, 2.5, -14]);  /* a wide strip behind, low: horizontal surfaces (base, stage) catch it */
    return pm.fromScene(e, .02).texture; };
  const ENV = { light: studio(true), dark: studio(false), chrome: studio(false, 0x5a5d63) }; /* chrome: a mid-grey room with the bright softboxes — silver with contrast */

  /* light as in the Blender scene: a key from the upper left, a cool rim from behind, a soft fill */
  const key = new DirectionalLight(0xffffff, 2.6); key.position.set(-5, 7, 6); key.castShadow = true; key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -3.2, right: 3.2, top: 3.2, bottom: -3.2, near: 2, far: 22 }); key.shadow.radius = 18; key.shadow.blurSamples = 24; key.shadow.bias = -.0006; key.shadow.normalBias = .03;
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
  const BLACK = new Color(0x0e0f11), WHITE = new Color(0xf3f4f5); let themeDark = null; /* light theme: a white microscope (Andrey, 18.10) */ /* a lifted black: the lacquer must read lighter than the #0A0A0A page (Andrey, 18.10) */
  /* light theme: the dark parts stay black (no metal, little of the light studio in them), the lamp a saturated blue, not a pale glow (Andrey, 22.10) */
  const DARK = [...made.values()].filter(m => /^(Anodized|Band)/.test(m.name)).map(m => ({ m, c: m.color.clone(), mt: m.metalness, cc: m.clearcoat, r: m.roughness })), INK = new Color(0x060708);
  const LAMP = [...made.values()].filter(m => m.name === 'Lamp').map(m => ({ m, c: m.color.clone(), e: m.emissive.clone(), k: m.emissiveIntensity }));
  const LAMP_C = new Color(0x006ea8), LAMP_E = new Color(0x0090d0);
  /* chrome in the light theme mirrors its own studio: polished metal needs dark and bright in its reflections, the light grey room left it flat (Andrey, 22.10) */
  const CHROME = [...made.values()].filter(m => m.name === 'Chrome');
  const theme = dark => { themeDark = dark; EN.forEach(e => e.m.color.copy(dark ? BLACK : WHITE)); beamM.color.set(dark ? 0x19c6e2 : 0x00a0c4); spotM.color.copy(beamM.color);
    DARK.forEach(d => { d.m.color.copy(dark ? d.c : INK); d.m.metalness = dark ? d.mt : 0; d.m.clearcoat = dark ? d.cc : .35; d.m.roughness = dark ? d.r : .38;
      d.m.specularIntensity = dark ? 1 : .45; d.m.envMapIntensity = dark ? 1 : .22; });
    bands.forEach(b => { if (b) { b.metalness = dark ? LOOK[b.name].metalness : 0; b.envMapIntensity = dark ? 1 : .22; } });
    LAMP.forEach(l => { l.m.color.copy(dark ? l.c : LAMP_C); l.m.emissive.copy(dark ? l.e : LAMP_E); l.m.emissiveIntensity = dark ? l.k : .16; l.m.envMapIntensity = dark ? 1 : .25; });
    CHROME.forEach(m => { m.envMap = dark ? null : ENV.chrome; m.envMapIntensity = dark ? 1 : 1.1; m.needsUpdate = true; });
    S.environment = dark ? ENV.dark : ENV.light; S.environmentIntensity = 1;
    R.toneMappingExposure = dark ? 1.3 : 1.32; rim.intensity = dark ? 3 : 1.4; key.intensity = dark ? 2.6 : 2.3; fill.intensity = dark ? .6 : 1.1; floorM.opacity = dark ? .45 : .11;
    if ('intensity' in key.shadow) key.shadow.intensity = dark ? .75 : .55; };
  const spin = new Group(); spin.add(M); S.add(spin);

  /* the nosepiece turns round its own axis; each objective's band is lit by how close it is to the working position */
  const nose = M.getObjectByName('NosepieceSpin');
  /* the beam: from the working objective's tip straight down to one point on the slide (F); a soft spot where it lands.
     Tip height = apex 2.75 − seat distance .681 / cos 20° − objective length (4×/10×/40×: .5, .42, .56 — as built in microscope.py) */
  const F = new Vector3(0, 1.247, .2), LO = [.5, .42, .56];
  const beamM = new MeshBasicMaterial({ color: 0x19c6e2, transparent: true, depthWrite: false }), glowM = beamM.clone(), spotM = beamM.clone();
  const rod = new CylinderGeometry(1, 1, 1, 20, 1, true); rod.translate(0, .5, 0);
  const beam = new Mesh(rod, beamM), glow = new Mesh(rod, glowM), spot = new Mesh(new CircleGeometry(1, 40), spotM), core = new Mesh(new CircleGeometry(1, 32), beamM);
  for (const m of [spot, core]) { m.rotation.x = -Math.PI / 2; m.position.copy(F); m.position.y += .002; }
  spot.scale.setScalar(.075); core.scale.setScalar(.022); beam.position.copy(F); glow.position.copy(F); M.add(beam, glow, spot, core);
  const CY = new Color(0x00b6d3), DK = new Color(0x0b0c0d);
  const bands = [1, 2, 3].map(i => { let b = null; const o = M.getObjectByName('Objective' + i);
    o && o.traverse(m => { if (m.isMesh && /^Band/.test(m.material.name)) { m.material = m.material.clone(); b = m.material; } }); return b; });

  const D = 11.2, cam = new PerspectiveCamera(22, 1, .5, 60), T = new Vector3(0, 1.78, 0);
  /* the canvas covers the whole hero (nothing gets cut); the projection centre sits on the right column (cx, cy), ppu = pixels per model unit */
  const fit = () => { const hr = hero.getBoundingClientRect(), r = box.getBoundingClientRect(), m = innerWidth <= 860, W = hero.clientWidth, H = hero.clientHeight;
    const cx = r.left - hr.left + r.width * (m ? .5 : .47), cy = m ? r.top - hr.top + r.height * .47 : H * .465, ppu = m ? r.height * .27 : H * .185;
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
    let wi = 0; bands.forEach((b, i) => { const a = act(i); if (a > act(wi)) wi = i; if (!b) return; b.color.copy(DK).lerp(CY, a); b.emissive.copy(CY).multiplyScalar(a * .35); });
    /* the beam shows only while an objective stands in place; it goes out while the nosepiece turns */
    const on = Math.max(0, Math.min(1, (act(wi) - .85) / .15)), L = 2.75 - .681 / Math.cos(.349066) - LO[wi] - F.y, pl = .8 + .2 * Math.sin(t * 5);
    beam.scale.set(.007, L, .007); glow.scale.set(.03, L, .03);
    beamM.opacity = .95 * on; glowM.opacity = .22 * on * pl; spotM.opacity = .35 * on * pl; for (const m of [beam, glow, spot, core]) m.visible = on > .01;
    R.render(S, cam);
    if (!cv.classList.contains('on')) cv.classList.add('on'); };

  window.__m3d = frame;
  new ResizeObserver(() => { fit(); frame(...args); }).observe(hero);
  if (rm) frame(1, 0, 0, 0);
}
