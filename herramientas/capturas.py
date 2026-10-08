# -*- coding: utf-8 -*-
"""Capturas de control (paso 29) con Playwright para Python: primera pantalla y página entera a 390, 768, 1.024, 1.280 y
1.440 px, desborde horizontal (scrollWidth === innerWidth) y errores de consola. Lanza Chromium con SwiftShader.

Uso (desde la raíz, con la web servida por servir.sh):
  python3 herramientas/capturas.py [--base http://localhost:8765] [--salida capturas] [--anchos 390,768,1024,1280,1440] / /contacto/ …
  Con PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers; si hace falta otro binario, --ejecutable /ruta/a/chrome.

Dos pasadas por página y ancho:
  1. CON MOVIMIENTO (la real): primera pantalla tras 3,5 s, recorrido de arriba abajo para que salten las apariciones,
     los pines y los scrubs, y recogida de errores JS. Mide el desborde al final del recorrido.
  2. SIN MOVIMIENTO (prefers-reduced-motion: reduce) para la página ENTERA: con pin y scrub, una captura de página
     completa deja el hueco del recorrido del pin en blanco y el titular con scrub a opacidad 0 (no es un fallo de la web:
     es que la captura no hace scroll). Con movimiento reducido la web enseña su estado completo y quieto, que es lo que
     hay que revisar en una imagen. La barra fija del móvil, el botón de subir y el aviso de cookies se esconden en esta
     pasada (si no, caen a mitad de página en la imagen). Si algo se ve mal en la pasada 2 y bien en la 1, el fallo es de
     la versión sin movimiento y se arregla igual (mejora progresiva).
Sale con código 1 si hay desborde o errores JS."""
import argparse, os, re, sys
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("rutas", nargs="*", default=["/"])
ap.add_argument("--base", default="http://localhost:8765")
ap.add_argument("--salida", default="capturas")
ap.add_argument("--anchos", default="390,768,1024,1280,1440")
ap.add_argument("--solo-primera", action="store_true")
ap.add_argument("--ejecutable", default=os.environ.get("CAPTURAS_CHROMIUM", ""))
a = ap.parse_args()
os.makedirs(a.salida, exist_ok=True)
try:
    clave = re.search(r'COOKIES_CLAVE\s*=\s*"([^"]+)"', open("generador/config.py", encoding="utf-8").read()).group(1)
except Exception:
    clave = "cookies"
ALTO = {390: 844, 768: 1024, 1024: 768, 1280: 800, 1440: 900}
OCULTAR = ".barra-movil,.subir,.cookies{display:none !important}"
fallos = 0
with sync_playwright() as p:
    kw = dict(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
    if a.ejecutable:
        kw["executable_path"] = a.ejecutable
    b = p.chromium.launch(**kw)
    for ruta in a.rutas:
        nombre = ruta.strip("/").replace("/", "_") or "home"
        for w in [int(x) for x in a.anchos.split(",")]:
            movil = w < 900
            errores = []

            def contexto(reducido):
                ctx = b.new_context(viewport={"width": w, "height": ALTO.get(w, 900)}, device_scale_factor=1,
                                    is_mobile=movil, has_touch=movil, reduced_motion="reduce" if reducido else "no-preference")
                ctx.add_init_script(f"try{{localStorage.setItem('{clave}','no')}}catch(e){{}}")
                pg = ctx.new_page()
                pg.on("pageerror", lambda e: errores.append(str(e)))
                pg.on("console", lambda m: errores.append(m.text) if m.type == "error" and "maps.google" not in m.text and "net::" not in m.text else None)
                pg.goto(a.base + ruta, wait_until="load")
                return ctx, pg

            # 1 · con movimiento: primera pantalla + recorrido + desborde + errores
            ctx, pg = contexto(False)
            pg.wait_for_timeout(3500)
            pg.screenshot(path=f"{a.salida}/{nombre}-{w}.png")
            alto = pg.evaluate("document.documentElement.scrollHeight")
            for y in range(0, alto, 400):
                pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(70)
            pg.wait_for_timeout(500)
            desb = pg.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
            ancho_v = pg.evaluate("window.innerWidth")
            ctx.close()
            # 2 · sin movimiento: página entera
            desb2 = desb
            if not a.solo_primera:
                ctx, pg = contexto(True)
                pg.add_style_tag(content=OCULTAR)
                pg.wait_for_timeout(1200)
                alto = pg.evaluate("document.documentElement.scrollHeight")
                for y in range(0, alto, 600):
                    pg.evaluate(f"window.scrollTo(0,{y})"); pg.wait_for_timeout(40)
                pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(400)
                pg.screenshot(path=f"{a.salida}/{nombre}-{w}-entera.png", full_page=True)
                desb2 = pg.evaluate("Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
                ctx.close()
            peor = max(desb, desb2)
            if peor > ancho_v or errores:
                fallos += 1
            print(f"{ruta} @{w}: desborde {'SÍ (' + str(peor) + ' px)' if peor > ancho_v else 'no'} · errores JS: {'; '.join(errores) or 'ninguno'}")
    b.close()
sys.exit(1 if fallos else 0)
