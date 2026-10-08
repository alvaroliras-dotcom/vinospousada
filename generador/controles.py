# -*- coding: utf-8 -*-
"""GYF-Rayo · Controles a máquina (fase 08) sobre sitio/. Uso: python3 generador/controles.py
Sale con código 1 si hay errores. Los avisos no bloquean.

Tres listas (paso 28, v12): ERRORES (bloquean), AVISOS (cosas del código o del texto que hay que arreglar) y
PENDIENTES DE MATERIAL (lo que no depende del código: CID de la ficha, fotos provisionales o que faltan). Un pendiente
de material no es un aviso silenciado: se imprime siempre y se cierra cuando llega el material (ESTADO.md).

Controles del paso 28 que NO aplican a este tema/cliente y por qué (no se silencian: se explica aquí):
- «AVISO si una página no tiene "Lector:" y "Decide:"»: en Pousada esas líneas viven en 05-TEXTOS-NUEVOS (Merche) y
  en PROMESAS.md, no en contenido/paginas/ (importar_textos.py las quita porque no se publican). Aquí se comprueba lo
  contrario: ERROR si «Lector:», «Decide:», «Por verificar», «Cambios del», «Notas para Álvaro» o ⚑ llegan al HTML.
- «falta la imagen fija del objeto de portada»: OBJETO_PORTADA["tipo"] es None (portada con foto, sin objeto 3D), así
  que el control solo corre si hay objeto.
- «CASOS sin captura real»: CASOS = [] (sin galería de casos).
- «resenas.json de EJEMPLO»: OPINIONES_SECCION = False; el archivo está vacío a propósito (sin reseñas reales)."""
import csv, json, os, re, sys
from html.parser import HTMLParser

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DOMINIO, NEGOCIO, LEGALES
import config as CFG
SITIO = os.path.join(RAIZ, "sitio")
err, avi, pend = [], [], []


class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.h1 = 0; s.links = []; s.imgs = []; s.title = ""; s._t = False; s.meta = {}; s.ld = []; s._ld = False; s.canon = None; s.ids = set()
    def handle_starttag(s, tag, a):
        a = dict(a)
        if "id" in a: s.ids.add(a["id"])
        if tag == "h1": s.h1 += 1
        if tag == "a" and a.get("href"): s.links.append(a["href"])
        if tag == "img": s.imgs.append(a)
        if tag == "title": s._t = True
        if tag == "meta" and a.get("name"): s.meta[a["name"]] = a.get("content", "")
        if tag == "link" and a.get("rel") == "canonical": s.canon = a.get("href")
        if tag == "script" and a.get("type") == "application/ld+json": s._ld = True
    def handle_endtag(s, tag):
        if tag == "title": s._t = False
        if tag == "script": s._ld = False
    def handle_data(s, d):
        if s._t: s.title += d
        if s._ld: s.ld.append(d)


paginas = {}
for r, _, fs in os.walk(SITIO):
    for f in fs:
        if f.endswith(".html"):
            ruta = os.path.join(r, f)
            url = "/" + os.path.relpath(ruta, SITIO).replace("index.html", "").replace(os.sep, "/")
            url = url if url.endswith("/") or url.endswith(".html") else url + "/"
            paginas[url] = ruta

existe = lambda u: u in paginas or os.path.exists(os.path.join(SITIO, u.lstrip("/").split("?")[0].split("#")[0]))
titulos, metas = {}, {}
for url, ruta in sorted(paginas.items()):
    h = open(ruta, encoding="utf-8").read()
    p = P(); p.feed(h)
    idx = "noindex" not in p.meta.get("robots", "")
    if p.h1 != 1: err.append(f"{url}: {p.h1} H1")
    if re.search(r"\[LINK|🔗|🆕|\]\(/", h): err.append(f"{url}: restos de markdown o marcas del contrato")
    if "⚑" in h: err.append(f"{url}: una ⚑ ha llegado al HTML (regla 11: ninguna ⚑ llega a GitHub)")
    _txt_vis = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S))
    if re.search(r"\*\*|(^|\s)#{1,4}\s|\]\(|(^|\s)`[^`]+`", _txt_vis, re.M): err.append(f"{url}: restos de markdown en el texto (**, ##, ]( o `código`)")
    if re.search(r"\b(Lector|Decide|Por verificar|Cambios del|Notas para Álvaro)\s*:", _txt_vis): err.append(f"{url}: notas de redacción publicadas (Lector:/Decide:/Por verificar/Cambios del)")
    for l in p.links:
        if l.startswith("/") and not existe(l.split("#")[0].split("?")[0] or "/"):
            err.append(f"{url}: enlace roto {l}")
        if l.startswith("/") and not l.endswith("/") and "." not in l.split("/")[-1] and "#" not in l and "?" not in l:
            avi.append(f"{url}: enlace sin barra final {l}")
    for im in p.imgs:
        if "alt" not in im: err.append(f"{url}: imagen sin alt {im.get('src')}")
        src = im.get("src", "")
        if src.startswith("/") and not existe(src.split("?")[0]): err.append(f"{url}: imagen que no existe {src}")
    for d in p.ld:
        try: json.loads(d)
        except Exception as e: err.append(f"{url}: JSON-LD inválido ({e})")
    if idx and url.endswith("/"):
        t, m = p.title.strip(), p.meta.get("description", "")
        if not 30 <= len(t) <= 65: avi.append(f"{url}: title de {len(t)} caracteres")
        if not 120 <= len(m) <= 160: avi.append(f"{url}: meta de {len(m)} caracteres")
        if p.canon != DOMINIO + url: err.append(f"{url}: canónica {p.canon}")
        titulos.setdefault(t, []).append(url); metas.setdefault(m, []).append(url)
    if f"tel:{NEGOCIO['telefono_e164']}" not in h: err.append(f"{url}: sin enlace de llamada")
    # Promesas (paso 28, v11): ni precios ni frases de la columna «no se dice nunca» de PROMESAS.md
    cuerpo_sin_legales = h if url not in [u for _, u in LEGALES] else ""
    txt_prom = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", "", cuerpo_sin_legales, flags=re.S)))
    if re.search(r"\d[\d.,]*\s?€|\beuros?\b", txt_prom, re.I): err.append(f"{url}: precio en el texto (la web no publica precios)")
    for frase in getattr(CFG, "NO_SE_DICE", []):
        if re.search(frase, txt_prom, re.I): err.append(f"{url}: frase prohibida por PROMESAS.md («{frase}»)")
    # Pie por página: si no tiene frase propia sale la de defecto
    if url.endswith("/") and getattr(CFG, "PIE_ESTILO", "") == "oscuro" and url not in [u for _, u in LEGALES] and url != "/404.html":
        import datos
        tipo = datos.tipo_de(url)
        if not (getattr(CFG, "PIE_FRASES", {}).get(url) or getattr(CFG, "PIE_FRASES_TIPO", {}).get(tipo)): avi.append(f"{url}: pie de defecto (sin frase en PIE_FRASES)")
    # Controles de texto (auditoría v6): notas de maqueta, subtítulos vacíos, enlaces que se pierden
    cuerpo = re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S)
    sin_op = re.sub(r'<ul class="op-lista".*?</ul>', "", cuerpo, flags=re.S)  # las reseñas reales no se tocan
    txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", sin_op))
    for pat, que in [(r"\((Formulario|Widget|Foto|Imagen|Mapa|Nota)\b", "nota de maqueta entre paréntesis"),
                     (r"\ben contacta con nosotros\b", "«en contacta con nosotros»"),
                     (r"[a-záéíóúñ,] Contacta con nosotros", "«Contacta» con mayúscula a mitad de frase"),
                     (r"a la hora que sea|24 ?h(oras)?\b(?! no)", "promesa de horario que no es verdad")]:
        if re.search(pat, txt) and not (que.startswith("promesa") and url in [u for _, u in LEGALES]) and not (que.startswith("promesa") and re.search(r"no (hacemos|atendemos|damos)[^.]{0,40}24", txt)):
            err.append(f"{url}: {que}")
    if re.search(r"<p><strong>[^<]{3,40}</strong></p>\s*<p><strong>[^<]{3,40}</strong></p>", cuerpo):
        err.append(f"{url}: dos subtítulos seguidos sin contenido")
    # Restos de Markdown: tablas sin convertir y citas «>» pegadas a un párrafo
    if "|---" in cuerpo or re.search(r"\|\s*:?-{3,}:?\s*\|", cuerpo):
        err.append(f"{url}: tabla de Markdown sin convertir (|---|)")
    if re.search(r"<p\b[^>]*>(?:(?!</p>).)*&gt;", cuerpo, flags=re.S):
        err.append(f"{url}: «&gt;» dentro de un párrafo (cita de Markdown sin convertir)")
    # Declaración de ~60 palabras (el resto de la entrada baja al primer bloque)
    for d in re.findall(r'<p class="declara__txt[^"]*">(.*?)</p>', cuerpo, flags=re.S):
        w = len(re.sub(r"<[^>]+>", " ", d).split())
        if w > 70: avi.append(f"{url}: declaración de {w} palabras (máximo ~60)")
    fotos_pag = re.findall(r'<img src="/img/([a-z0-9-]+)-1600\.jpg"', cuerpo.split('<footer')[0])
    rep = {x for x in fotos_pag if fotos_pag.count(x) > 1 and 'sitem__mini' not in cuerpo}
    if rep: avi.append(f"{url}: foto repetida en la página {sorted(rep)}")

for t, us in titulos.items():
    if len(us) > 1: err.append(f"title duplicado en {us}")
# Pie por URL: dos páginas con frase propia en PIE_FRASES no comparten titular (las plantillas por tipo, PIE_FRASES_TIPO,
# se repiten a propósito en las 26 fichas: el botón lleva el nombre del vino; eso no es «el mismo pie en todas»)
_tit_pie = {}
for _u, _f in getattr(CFG, "PIE_FRASES", {}).items(): _tit_pie.setdefault(_f[1], []).append(_u)
for _t, _us in _tit_pie.items():
    if len(_us) > 1: avi.append(f"pie: «{_t}» se repite en {_us} (una frase por URL, tabla de Dani)")
for _t, _us in getattr(CFG, "PIE_FRASES_TIPO", {}).items():
    if _us[1] in _tit_pie: avi.append(f"pie: la plantilla por tipo «{_t}» repite el titular «{_us[1]}» de {_tit_pie[_us[1]]}")
for m, us in metas.items():
    if len(us) > 1: err.append(f"meta duplicada en {us}")

# Contrato de enlaces (paso 23): cada enlace editorial previsto tiene que estar en su página
faltan = 0
ruta_c = os.path.join(RAIZ, "generador", "contrato_enlaces.csv")
if os.path.exists(ruta_c):
    for row in csv.DictReader(open(ruta_c, encoding="utf-8-sig"), delimiter=";"):
        o, d = row["origen"], row["destino"]
        if o in paginas and d.startswith("/"):
            if f'href="{d}"' not in open(paginas[o], encoding="utf-8").read():
                faltan += 1; avi.append(f"contrato: falta {o} → {d}")

# Sitemap
sm = open(os.path.join(SITIO, "sitemap.xml"), encoding="utf-8").read()
for u in re.findall(rf"<loc>{re.escape(DOMINIO)}([^<]+)</loc>", sm):
    if u not in paginas: err.append(f"sitemap: {u} no existe")

# Datos de ejemplo del tema que se hayan quedado sin cambiar
_r = json.load(open(os.path.join(RAIZ, "contenido", "resenas.json"), encoding="utf-8"))
if getattr(CFG, "OPINIONES_SECCION", True):
    if "_nota" in _r or not _r.get("opiniones"): avi.append("resenas.json: son los datos de EJEMPLO (sin reseñas reales)")
    if any(o.get("marcador") for o in _r.get("opiniones", [])): avi.append("resenas.json: hay opiniones MARCADOR (sustituir por las reales de la ficha)")
elif "_nota" in _r: avi.append("resenas.json: son los datos de EJEMPLO")
from config import CASOS, OBJETO_PORTADA
_sin = [c[0] for c in CASOS if not c[2]]
if _sin: avi.append(f"CASOS sin captura real (sale el marcador de maqueta): {', '.join(_sin)}")
if OBJETO_PORTADA.get("imagen") and not os.path.exists(os.path.join(SITIO, "img", OBJETO_PORTADA["imagen"].rsplit(".", 1)[0] + "-840.webp")): err.append("falta la imagen fija del objeto de portada")
for k, v in [("DOMINIO", DOMINIO), ("teléfono", NEGOCIO["telefono_e164"])]:
    if "ejemplo" in v or "600000000" in v or set(v) <= {"0"}: avi.append(f"config.py: {k} sigue siendo el de EJEMPLO")
if NEGOCIO["cid"] in ("0", ""): pend.append("config.py: CID de la ficha de Google pendiente (paso 3): sin mapa ni enlace a la ficha")
# Fotos: ninguna por debajo de 800 px de ancho; la de portada (a sangre en móvil) ≥ 1.600 (v11)
try:
    from PIL import Image
    for carpeta in ("fotos", "producto"):
        d = os.path.join(RAIZ, "recursos", carpeta)
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            with Image.open(os.path.join(d, f)) as im:
                minimo = 400 if carpeta == "producto" else 800
                lado = max(im.width, im.height) if carpeta == "producto" else im.width   # las botellas recortadas son altas y estrechas
                if lado < minimo: err.append(f"recursos/{carpeta}/{f}: {lado} px (mínimo {minimo})")
                if "PROVISIONAL" in f: pend.append(f"recursos/{carpeta}/{f}: foto PROVISIONAL")
    PO = getattr(CFG, "PORTADA", {})
    if PO.get("foto"):
        with Image.open(os.path.join(RAIZ, "recursos", "fotos", PO["foto"])) as im:
            if im.width < 1600: err.append(f"portada: {PO['foto']} tiene {im.width} px (a sangre: mínimo 1.600)")
except ImportError:
    pass
# Catálogo: productos sin foto (sale la pieza tipográfica) y fotos provisionales
try:
    import datos
    _cat = datos.catalogo()
    _sinf = [p["nombre"] for p in _cat if not p.get("foto")]
    if _sinf: pend.append(f"catálogo sin foto (pieza tipográfica): {', '.join(_sinf)}")
    _prov = [p["nombre"] for p in _cat if p.get("provisional")]
    if _prov: pend.append(f"catálogo con foto PROVISIONAL (recorte del catálogo en PDF): {len(_prov)} referencias")
    # Cabecera de cada ficha (D.O., Tipo, Uva, Graduación, Foto) = espejo de catalogo.json: si se descuadran, ERROR
    for pg in datos.todas():
        if pg.get("producto") and pg.get("ficha_cab"):
            pr = datos.producto(pg["producto"]); c = pg["ficha_cab"]
            esperado = {"D.O.": pr["do"] or "—", "Tipo": pr["tipo"], "Uva": pr["uva"] or "—", "Graduación": pr["graduacion"], "Foto": pr["foto"] or "— (pieza tipográfica)"}
            for k, v in esperado.items():
                if k in c and c[k] != v: err.append(f"{pg['url']}: la cabecera dice «{k}: {c[k]}» y catalogo.json «{v}»")
except Exception as e:
    avi.append(f"catálogo: no se pudo leer ({e})")
print(f"Páginas HTML: {len(paginas)}")
print(f"ERRORES: {len(err)}"); [print("  ✗", e) for e in err[:80]]
print(f"AVISOS: {len(avi)}"); [print("  ·", a) for a in avi[:80]]
print(f"PENDIENTES DE MATERIAL (no bloquean; se cierran cuando llega el material): {len(pend)}"); [print("  ○", a) for a in pend]
print("No aplican (ver cabecera del archivo): Lector:/Decide: en el texto · objeto 3D · casos · reseñas de ejemplo")
sys.exit(1 if err else 0)
