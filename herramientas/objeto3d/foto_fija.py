# -*- coding: utf-8 -*-
"""Genera la imagen fija del objeto 3D (el LCP de la portada y el respaldo en móvil y sin WebGL):
pinta el símbolo con el mismo módulo que la web (objeto3d.min.js), en una pose fija, sobre fondo
transparente, y lo guarda en recursos/objeto/<OBJETO_PORTADA["imagen"]> (PNG 1.680 × 1.680 con alfa).
Uso (desde la raíz del tema):  python3 herramientas/objeto3d/foto_fija.py [giro_x giro_y]
Requiere Playwright con Chromium (lanza con SwiftShader: no hace falta GPU)."""
import os, sys
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "generador"))
from config import OBJETO_PORTADA as O
from playwright.sync_api import sync_playwright

giro = [float(x) for x in sys.argv[1:3]] if len(sys.argv) > 2 else [-0.12, 0.45]
svg = open(os.path.join(RAIZ, "recursos", "marca", O["svg_3d"]), encoding="utf-8").read()
color = O.get("color_3d") if O.get("color_unico") else None
salida = os.path.join(RAIZ, "recursos", "objeto", O["imagen"])
os.makedirs(os.path.dirname(salida), exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 840, "height": 840}, device_scale_factor=2)
    pg.set_content('<html><body style="margin:0;background:transparent"><div id="c" style="width:840px;height:840px"></div></body></html>')
    pg.add_script_tag(path=os.path.join(RAIZ, "cliente", "js", "vendor", "objeto3d.min.js"))
    pg.evaluate("""([svg, color, giro]) => new Promise(ok => Objeto3D.montar(document.getElementById('c'),
        {svg, color, quieto: true, giro, listo: () => setTimeout(ok, 400)}))""", [svg, color, giro])
    pg.locator("#c").screenshot(path=salida, omit_background=True)
    b.close()
from PIL import Image
im = Image.open(salida)
print(f"foto_fija: {salida} {im.size} {os.path.getsize(salida)//1024} KB")
