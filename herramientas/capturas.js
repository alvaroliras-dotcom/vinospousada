// Capturas de control (paso 29 del protocolo): primera pantalla del móvil y del ordenador,
// página entera y aviso de desborde horizontal y errores de consola.
//
// Se lanza desde la raíz del repositorio del cliente (lee generador/config.py).
// Uso:  NODE_PATH=$(npm root -g) node capturas.js http://localhost:8765 / /contacto/ /otra-pagina/
// Salida: carpeta ./capturas/ con <pagina>-movil.png, <pagina>-movil-entera.png y <pagina>-escritorio.png
// Requiere Playwright (en el entorno de Claude: Chromium en /opt/pw-browsers; si no, quita executablePath).
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const [base, ...rutas] = process.argv.slice(2);
  if (!base) { console.log('Uso: node capturas.js <url-base> <ruta> [<ruta>...]'); process.exit(1); }
  const paginas = rutas.length ? rutas : ['/'];
  fs.mkdirSync('capturas', { recursive: true });
  const opts = {};
  const exe = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
  if (fs.existsSync(exe)) opts.executablePath = exe;
  const b = await chromium.launch(opts);
  // La clave del aviso de cookies se lee de generador/config.py (COOKIES_CLAVE), para que el aviso no tape la captura
  let clave = 'cookies';
  try { clave = fs.readFileSync('generador/config.py', 'utf8').match(/COOKIES_CLAVE\s*=\s*"([^"]+)"/)[1]; } catch (e) {}
  const sinCookies = (k) => { try { localStorage.setItem(k, 'no'); } catch (e) {} };

  for (const ruta of paginas) {
    const nombre = ruta.replace(/\//g, '_').replace(/^_|_$/g, '') || 'home';
    // Móvil (390 x 844, como un iPhone normal)
    const m = await b.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
    await m.addInitScript(sinCookies, clave);
    const pm = await m.newPage(); const errores = [];
    pm.on('pageerror', e => errores.push(e.message));
    await pm.goto(base + ruta, { waitUntil: 'load' }); await pm.waitForTimeout(2000);
    await pm.screenshot({ path: `capturas/${nombre}-movil.png` });
    const alto = await pm.evaluate(() => document.body.scrollHeight);
    for (let y = 0; y < alto; y += 700) { await pm.evaluate(y => window.scrollTo(0, y), y); await pm.waitForTimeout(100); }
    await pm.evaluate(() => window.scrollTo(0, 0)); await pm.waitForTimeout(500);
    await pm.screenshot({ path: `capturas/${nombre}-movil-entera.png`, fullPage: true });
    const ancho = await pm.evaluate(() => document.documentElement.scrollWidth);
    // ¿Qué hay en la primera pantalla? (la foto, la nota y el botón de llamar deberían estar)
    const primera = await pm.evaluate(() => {
      const ve = sel => { const e = document.querySelector(sel); if (!e) return false; const r = e.getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; };
      return { foto: ve('.portada__fondo, .portada__foto'), nota: ve('.portada__nota'), llamar: ve('.portada .tel') };
    });
    await m.close();
    // Ordenador (1440 x 900)
    const d = await b.newContext({ viewport: { width: 1440, height: 900 } });
    await d.addInitScript(sinCookies, clave);
    const pd = await d.newPage();
    await pd.goto(base + ruta, { waitUntil: 'load' }); await pd.waitForTimeout(2000);
    await pd.screenshot({ path: `capturas/${nombre}-escritorio.png` });
    await d.close();
    console.log(`${ruta}  desborde: ${ancho > 390 ? 'SÍ (' + ancho + ' px)' : 'no'}  · primera pantalla móvil: foto ${primera.foto ? 'sí' : 'NO'}, nota ${primera.nota ? 'sí' : 'NO'}, llamar ${primera.llamar ? 'sí' : 'NO'}  · errores JS: ${errores.length ? errores.join(' | ') : 'ninguno'}`);
  }
  await b.close();
})();
