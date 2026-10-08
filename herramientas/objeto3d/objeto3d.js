/* GYF-Rayo · Objeto de portada en 3D (módulo diferido).
   Extruye el SVG del símbolo del cliente (solo trazados rellenos), lo pinta en laca con reflejos de estudio,
   gira despacio y sigue al ratón. Lo carga main.js SOLO en ordenador, sin movimiento reducido, con WebGL y
   cuando la portada ya ha pintado: la imagen fija de debajo es el LCP y el respaldo.
   Se compila con herramientas/objeto3d/construir.sh → cliente/js/vendor/objeto3d.min.js (IIFE, window.Objeto3D). */
import { WebGLRenderer, Scene, PerspectiveCamera, Group, Mesh, MeshPhysicalMaterial, ExtrudeGeometry, Box3, Vector3,
  DirectionalLight, PMREMGenerator, ACESFilmicToneMapping, SRGBColorSpace, Color } from "three";
import { SVGLoader } from "three/examples/jsm/loaders/SVGLoader.js";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

export function soporta() {
  try { const c = document.createElement("canvas"); return !!(window.WebGLRenderingContext && (c.getContext("webgl2") || c.getContext("webgl"))); }
  catch (e) { return false; }
}

/* opts: { svg: url o texto del SVG, color: "#hex" (si se da, pinta todo de ese color), quieto: bool,
           giro: [x, y] (pose fija para la foto), listo: fn } */
export async function montar(caja, opts) {
  opts = opts || {};
  const txt = /^\s*</.test(opts.svg) ? opts.svg : await (await fetch(opts.svg)).text();
  const W = () => caja.clientWidth || 300, H = () => caja.clientHeight || 300;
  const r = new WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: !!opts.quieto, powerPreference: "low-power" });
  r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  r.setSize(W(), H());
  r.setClearColor(0x000000, 0);
  r.toneMapping = ACESFilmicToneMapping; r.outputColorSpace = SRGBColorSpace;
  r.domElement.setAttribute("aria-hidden", "true");
  caja.appendChild(r.domElement);
  const sc = new Scene();
  const pm = new PMREMGenerator(r);
  sc.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
  const cam = new PerspectiveCamera(30, W() / H(), 1, 4000);

  const datos = new SVGLoader().parse(txt);
  const g = new Group(), mats = {};
  const caja0 = new Box3();
  datos.paths.forEach(p => SVGLoader.createShapes(p).forEach(sh => {
    const tmp = new ExtrudeGeometry(sh, { depth: 1, bevelEnabled: false }); tmp.computeBoundingBox(); caja0.union(tmp.boundingBox); tmp.dispose();
  }));
  const tam = new Vector3(); caja0.getSize(tam);
  const m = Math.max(tam.x, tam.y) || 100;
  datos.paths.forEach(p => {
    const col = opts.color || ("#" + p.color.getHexString());
    const mat = mats[col] || (mats[col] = new MeshPhysicalMaterial({ color: new Color(col), roughness: .18, metalness: 0, clearcoat: 1, clearcoatRoughness: .05 }));
    SVGLoader.createShapes(p).forEach(sh => {
      g.add(new Mesh(new ExtrudeGeometry(sh, { depth: m * .1, bevelEnabled: true, bevelThickness: m * .03, bevelSize: m * .02,
        bevelSegments: 10, curveSegments: 48 }), mat));
    });
  });
  const b = new Box3().setFromObject(g), c = b.getCenter(new Vector3());
  g.children.forEach(x => x.geometry.translate(-c.x, -c.y, -c.z));
  g.scale.set(100 / m, -100 / m, 100 / m);
  const piv = new Group(); piv.add(g); sc.add(piv);
  const luz = new DirectionalLight(0xffffff, 1.4); luz.position.set(-120, 160, 200); sc.add(luz);
  const encuadra = () => { cam.aspect = W() / H(); cam.position.set(0, 0, 100 / (2 * Math.tan(15 * Math.PI / 180)) * 1.5); cam.updateProjectionMatrix(); };
  encuadra();

  let mx = 0, my = 0, vivo = true, visible = true, raf = 0;
  const alMover = e => { mx = e.clientX / innerWidth - .5; my = e.clientY / innerHeight - .5; };
  const alCambiar = () => { r.setSize(W(), H()); encuadra(); if (opts.quieto) pinta(0); };
  addEventListener("pointermove", alMover, { passive: true });
  addEventListener("resize", alCambiar);
  const io = "IntersectionObserver" in window ? new IntersectionObserver(e => { visible = e[e.length - 1].isIntersecting; if (visible && vivo) bucle(); }) : null;
  if (io) io.observe(caja);
  const t0 = performance.now();
  function pinta(t) {
    if (opts.quieto) { piv.rotation.set((opts.giro || [-.12, .45])[0], (opts.giro || [-.12, .45])[1], 0); }
    else { const g0 = opts.giro || [-.12, .45]; piv.rotation.y = g0[1] + Math.sin(t * .55) * .55 + mx * .5; piv.rotation.x = g0[0] + Math.sin(t * .8) * .1 + my * .3; piv.position.y = Math.sin(t * 1.1) * 3; }
    r.render(sc, cam);
  }
  function bucle() {
    cancelAnimationFrame(raf);
    if (!vivo || !visible || document.hidden || opts.quieto) return;
    raf = requestAnimationFrame(() => { pinta((performance.now() - t0) / 1000); bucle(); });
  }
  document.addEventListener("visibilitychange", bucle);
  pinta(0);
  if (!opts.quieto) bucle();
  if (opts.listo) opts.listo(r.domElement);
  return {
    lienzo: r.domElement,
    parar() { vivo = false; cancelAnimationFrame(raf); removeEventListener("pointermove", alMover); removeEventListener("resize", alCambiar); if (io) io.disconnect(); r.dispose(); }
  };
}
