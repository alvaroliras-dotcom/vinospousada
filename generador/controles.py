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
# ====================================================================================================================
# Bloque del paso 36 (arreglos de la auditoría del 08/10/2026 y cambios de David del 09/10/2026). Todo se comprueba sobre
# sitio/ (lo que se publica), no sobre el código. Cada control va en su try: si uno se rompe, avisa y no tapa a los demás.
# ====================================================================================================================
import datos as _datos
from html import escape as html_escape
_FORM = getattr(CFG, "FORMULARIO", None) or {}
_html_de = {u: open(r, encoding="utf-8").read() for u, r in sorted(paginas.items())}


def _ld_nodos(h):
    """Todos los nodos del JSON-LD de una página (aplanando @graph)."""
    out = []
    for d in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, flags=re.S):
        try:
            j = json.loads(d)
        except Exception:
            continue
        out += j.get("@graph", [j]) if isinstance(j, dict) else []
    return out


def _cadenas(x):
    """Todas las cadenas de texto de un JSON (para buscar en ellas sin que los corchetes del JSON estorben)."""
    if isinstance(x, str): yield x
    elif isinstance(x, dict):
        for v in x.values(): yield from _cadenas(v)
    elif isinstance(x, list):
        for v in x: yield from _cadenas(v)


# 1 · Medidas reales de las imágenes (Bruno A3): width/height declarados = archivo de sitio/img/ y cada descriptor «w» del
#     srcset (img y source) = ancho real de su archivo. Antes del arreglo: 91 de 201 etiquetas mal; objetivo 0.
try:
    from PIL import Image as _Im
    _med = {}

    def _medida_real(src):
        ruta = os.path.join(SITIO, src.lstrip("/").split("?")[0])
        if ruta not in _med:
            try:
                with _Im.open(ruta) as im: _med[ruta] = im.size
            except Exception: _med[ruta] = None
        return _med[ruta]

    _n_img = _n_mal = 0
    for url, h in _html_de.items():
        for m in re.finditer(r"<(img|source)\b([^>]*)>", h):
            a = dict(re.findall(r'([a-z-]+)="([^"]*)"', m.group(2)))
            src = a.get("src", "")
            if m.group(1) == "img" and src.startswith("/img/"):
                _n_img += 1
                real = _medida_real(src)
                if real:
                    try: decl = (int(a.get("width", 0)), int(a.get("height", 0)))
                    except ValueError: decl = (0, 0)
                    if decl != real:
                        _n_mal += 1; err.append(f"{url}: {src} declara {decl[0]}×{decl[1]} y el archivo mide {real[0]}×{real[1]}")
            for parte in a.get("srcset", "").split(","):
                p2 = parte.strip().split()
                if len(p2) == 2 and p2[1].endswith("w") and p2[0].startswith("/img/"):
                    r2 = _medida_real(p2[0])
                    if r2 and str(r2[0]) != p2[1][:-1]:
                        _n_mal += 1; err.append(f"{url}: srcset {p2[0]} dice {p2[1]} y el archivo mide {r2[0]} px de ancho")
    print(f"Imágenes de producto y fotos: {_n_img} etiquetas <img>, {_n_mal} con medida o srcset distintos del archivo (Bruno A3; objetivo 0)")
except ImportError:
    avi.append("control de medidas de imagen: falta Pillow")
except Exception as e:
    avi.append(f"control de medidas de imagen: no se pudo ejecutar ({e})")

# 2 · La primera imagen de la página no carga en diferido donde es el LCP: inicio, fichas, licores y /vino-turbio/ (Bruno M2)
try:
    for url, h in _html_de.items():
        if not url.endswith("/"): continue
        if _datos.tipo_de(url) in ("home", "turbio", "ficha", "licor"):
            # solo la imagen que va en la cabecera de la página (antes del primer H2 real): una ficha sin foto propia tiene su
            # primera <img> en «También le puede interesar», bajo el pliegue, y ahí el diferido es lo correcto
            cab = re.split(r"<h2\b(?![^>]*class=\"sr\")", h.split("<main", 1)[-1], 1)[0]
            m = re.search(r"<img\b[^>]*>", cab)
            if m and 'loading="lazy"' in m.group(0): err.append(f"{url}: la primera imagen carga en diferido y es el LCP (quitar loading=lazy; Bruno M2)")
except Exception as e:
    avi.append(f"control del LCP: no se pudo ejecutar ({e})")

# 3 · Marcas de botón del texto fuente («[Solicitar tarifa] [Llamar al …]») en el texto visible o en el JSON-LD (Matías L-09)
try:
    _marca = re.compile(r"\[(?!LINK )[^\]\n]{1,60}\](?!\()")
    for url, h in _html_de.items():
        vis = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S))
        m = _marca.search(vis)
        if m: err.append(f"{url}: marca de botón o corchetes sueltos en el texto «{m.group(0)}» (Matías L-09)")
        for nodo in _ld_nodos(h):
            for s in _cadenas(nodo):
                if _marca.search(s): err.append(f"{url}: marca de botón dentro del JSON-LD «{_marca.search(s).group(0)}»"); break
except Exception as e:
    avi.append(f"control de marcas de botón: no se pudo ejecutar ({e})")

# 4 · PROMESAS.md del 09/10/2026: ni «David» ni «más de 200 restaurantes» en nada que se publique (HTML entero, llms.txt,
#     enviar.php, JS). Y los marcadores {n_vinos}/{n_licores} tienen que haberse rellenado.
try:
    _publicos = dict(_html_de)
    for f in ("llms.txt", "enviar.php", "robots.txt", os.path.join("js", "main.js"), os.path.join("js", "tema.js")):
        r = os.path.join(SITIO, f)
        if os.path.exists(r): _publicos["/" + f.replace(os.sep, "/")] = open(r, encoding="utf-8", errors="replace").read()
    for url, h in _publicos.items():
        if re.search(r"\bDavid\b", h): err.append(f"{url}: aparece «David» (PROMESAS 09/10/2026: el nombre no sale en ninguna página, formulario, JSON-LD ni llms.txt)")
        if re.search(r"más de 200|200 restaurantes|doscientos restaurantes", h, re.I): err.append(f"{url}: «200 restaurantes» (PROMESAS 09/10/2026: ahora es «más de 100 restaurantes en Madrid»)")
        if "{n_vinos}" in h or "{n_licores}" in h: err.append(f"{url}: marcador {{n_vinos}}/{{n_licores}} sin rellenar")
        # (la cifra de vinos/licores ya la cuenta el generador con {n_vinos}/{n_licores} — build.py, cifras_marca();
        #  no se compara aquí contra un número literal porque hoy coincide con el real y daría falsos positivos.
        #  Si cambia el número de fichas publicadas sin que el texto se mueva, lo delata el propio build al no
        #  encontrar el marcador. «Gama de siete/seis» sí es un resto fijo de redacción, no una cifra calculada:
        if re.search(r"\bgama de (siete|seis)\b", h, re.I):
            err.append(f"{url}: «gama de siete/seis» como cifra fija de redacción (David 09/10/2026: no se cuenta a mano)")
except Exception as e:
    avi.append(f"control de PROMESAS 09/10: no se pudo ejecutar ({e})")

# 4b · Más del 09/10/2026: padre/abuelo/generaciones solo en /nosotros/ (y ahí sin nombres propios de personas); «foto
#     provisional» fuera de la vista pública; restos de trabajo que delatan la fuente del texto («según el catálogo»,
#     «la web vieja lo presentaba», «no las inventamos», «Álvaro confirma»).
try:
    _NOMBRES_PROPIOS = ("David",)   # el único nombre propio que podría colarse en «Nosotros»
    for url, h in _html_de.items():
        vis = re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", h, flags=re.S))
        if url != "/nosotros/" and re.search(r"\bpadre\b|\babuelo\b|\bgeneraci[oó]n", vis, re.I):
            err.append(f"{url}: «padre»/«abuelo»/«generación» fuera de /nosotros/ (PROMESAS 09/10/2026)")
        if url == "/nosotros/":
            for nom in _NOMBRES_PROPIOS:
                if re.search(rf"\b{nom}\b", vis): err.append(f"{url}: nombre propio «{nom}» en Nosotros (David 09/10/2026: sin nombres, aunque sí la historia familiar)")
        if re.search(r"foto provisional", vis, re.I):
            err.append(f"{url}: «foto provisional» en la vista pública (David 09/10/2026: se quita hasta que lleguen las fotos)")
        for frase in (r"según el catálogo", r"la web vieja lo presentaba", r"no las inventamos",
                      r"Álvaro confirma", r"nosotros no la elaboramos"):
            if re.search(frase, vis, re.I): err.append(f"{url}: resto de trabajo «{frase}» (auditoría 08/10/2026, hallazgo ALTA 1)")
except Exception as e:
    avi.append(f"control de restos y generaciones (09/10/2026): no se pudo ejecutar ({e})")

# 5 · JSON-LD (Bruno A2, Matías L-04/L-07/L-08, Turing A2/M2): sin Product ni FAQPage; sin Person si NEGOCIO["persona"] es None;
#     sin geo/hasMap/sameAs de la ficha mientras el CID sea 0 o las coordenadas sean aproximadas; areaServed siempre con la
#     provincia (AdministrativeArea), nunca solo la sede.
try:
    _geo_ok = NEGOCIO.get("cid") not in ("0", "", None) and not NEGOCIO.get("geo_aproximado")
    _zona = NEGOCIO.get("zona_servida") or NEGOCIO["provincia"]
    for url, h in _html_de.items():
        nodos = _ld_nodos(h)
        tipos = {n.get("@type") for n in nodos}
        if "Product" in tipos: err.append(f"{url}: JSON-LD con Product sin oferta (Bruno A2: fuera hasta que haya precios o reseñas)")
        if "FAQPage" in tipos: err.append(f"{url}: JSON-LD con FAQPage (Matías L-07: fuera; las preguntas siguen en la página)")
        for n in nodos:
            if n.get("@type") == NEGOCIO["schema_tipo"]:
                if not _geo_ok and ("geo" in n or "hasMap" in n): err.append(f"{url}: geo/hasMap publicados con CID 0 o coordenadas aproximadas (Matías L-04, Turing A2)")
                if not NEGOCIO.get("persona") and any(isinstance(v, dict) and v.get("@type") == "Person" for v in n.values()):
                    err.append(f"{url}: Person en el JSON-LD sin persona confirmada en config.py (Turing A2)")
            if "areaServed" in n:
                a = n["areaServed"] if isinstance(n["areaServed"], list) else [n["areaServed"]]
                if not any(isinstance(x, dict) and x.get("@type") == "AdministrativeArea" and x.get("name") == _zona for x in a):
                    err.append(f"{url}: areaServed de {n.get('@type')} sin la provincia «{_zona}» (Matías L-08, Turing M2)")
except Exception as e:
    avi.append(f"control del JSON-LD: no se pudo ejecutar ({e})")

# 6 · Medición (Dani C-01): un solo nombre por evento, en castellano; clic_cta_tarifa existe; el envío cuenta una vez;
#     data-gtm igual en todas las páginas y al de config.py (vacío = no carga nada; pendiente de dato).
try:
    _js = {f: open(os.path.join(SITIO, "js", f), encoding="utf-8").read() for f in ("main.js", "tema.js") if os.path.exists(os.path.join(SITIO, "js", f))}
    _todo_js = "\n".join(_js.values())
    for f, j in _js.items():
        for viejo in re.findall(r'event:\s*"(click_[a-z_]+|envio_formulario|solicitud_llamada|form_error)"', j):
            err.append(f"js/{f}: evento con nombre viejo «{viejo}» (tabla de Dani: clic_llamar, clic_whatsapp, clic_cta_tarifa, formulario_enviado, formulario_error, filtro_catalogo)")
    if 'event: "clic_cta_tarifa"' not in _todo_js: err.append("js/main.js: falta el evento clic_cta_tarifa del botón «Solicitar tarifa» (Dani C-01)")
    for ev in ("clic_llamar", "clic_whatsapp", "formulario_error", "filtro_catalogo"):
        if f'"{ev}"' not in _todo_js: err.append(f"js: falta el evento {ev} (Dani C-01)")
    _n_env = len(re.findall(r'event:\s*"formulario_enviado"', _todo_js))
    if _n_env != 1: err.append(f"js: formulario_enviado se empuja {_n_env} veces (tiene que ser 1: antes contaba doble)")
    _gtms = {re.search(r'<html[^>]*data-gtm="([^"]*)"', h).group(1) for h in _html_de.values() if re.search(r'<html[^>]*data-gtm="([^"]*)"', h)}
    if _gtms != {CFG.GTM_ID}: err.append(f"data-gtm en las páginas {sorted(_gtms)} ≠ GTM_ID de config.py «{CFG.GTM_ID}»")
    if not CFG.GTM_ID: pend.append("config.py: GTM_ID vacío (paso 7/45): el código mide (dataLayer) pero no carga ningún contenedor; falta el ID de Álvaro/Iñaki")
except Exception as e:
    avi.append(f"control de medición: no se pudo ejecutar ({e})")

# 7 · Formulario (Dani C-02, C-03, C-16): patrón del teléfono de config con su title, campo trampa con nombre sin sentido,
#     textos de error por motivo, confirmación sin plazo que PROMESAS no respalde; enviar.php sin marcadores y con la misma trampa.
try:
    _trampa = _FORM.get("trampa") or "contacto_alt"
    _patron = _FORM.get("telefono_patron")
    for url, h in _html_de.items():
        if '<form class="formulario' not in h: continue
        tel = re.search(r'<input type="tel"[^>]*>', h)
        if not tel: err.append(f"{url}: formulario sin campo de teléfono"); continue
        if _patron and f'pattern="{html_escape(_patron)}"' not in tel.group(0): err.append(f"{url}: el patrón del teléfono no es el de config.py (Dani C-03)")
        if 'title="' not in tel.group(0): err.append(f"{url}: el teléfono no lleva title con el ejemplo de formato (Dani C-03)")
        if f'name="{_trampa}"' not in h: err.append(f"{url}: falta el campo trampa «{_trampa}» (Dani C-02)")
        if 'name="web"' in h: err.append(f"{url}: el campo trampa sigue llamándose «web» (los gestores de contraseñas lo rellenan; Dani C-02)")
        if "data-motivos=" not in h: err.append(f"{url}: el aviso de error no lleva los textos por motivo (data-motivos; Dani C-03)")
        ok = re.search(r'<div class="aviso aviso--ok"[^>]*>(.*?)</div>', h, flags=re.S)
        if ok and re.search(r"\b(24|48)\s*h|hoy mismo|mañana|en menos de", ok.group(1), re.I): err.append(f"{url}: la confirmación promete un plazo que PROMESAS.md no respalda (Dani C-16)")
    _php = open(os.path.join(SITIO, "enviar.php"), encoding="utf-8").read() if os.path.exists(os.path.join(SITIO, "enviar.php")) else ""
    if not _php: err.append("sitio/enviar.php no existe")
    else:
        _sin = sorted(set(re.findall(r"__[A-Z_]+__", _php)) - {"__DIR__", "__FILE__", "__LINE__"})   # constantes mágicas de PHP, no marcadores
        if _sin: err.append(f"enviar.php: marcadores sin rellenar {_sin}")
        if f"$_POST['{_trampa}']" not in _php: err.append(f"enviar.php: no lee el campo trampa «{_trampa}» que escribe el formulario")
        if "motivo=" not in _php: err.append("enviar.php: no devuelve el motivo del rechazo (Dani C-02: ningún descarte silencioso)")
    if not NEGOCIO.get("email_aviso"): pend.append("config.py: NEGOCIO[\"email_aviso\"] vacío: sin aviso corto a un segundo buzón (el de Álvaro el primer mes; Dani C-02)")
    pend.append(f"formulario: buzón de destino {_FORM.get('buzon') or NEGOCIO['email']} por confirmar y envío real por probar en el hosting (paso 44; Dani C-02)")
except Exception as e:
    avi.append(f"control del formulario: no se pudo ejecutar ({e})")

# 8 · Archivos de servidor y públicos (Bruno A4/M6, Turing M1): .htaccess con las redirecciones de config, sin X-Robots-Tag,
#     negando vercel.json y comprimiendo text/javascript; resenas.json sin claves internas; robots.txt con la decisión sobre IA.
try:
    _ht = open(os.path.join(SITIO, ".htaccess"), encoding="utf-8").read() if os.path.exists(os.path.join(SITIO, ".htaccess")) else ""
    if not _ht: err.append("sitio/.htaccess no existe (sin él, las 29 URLs viejas dan 404 el día de publicar; Bruno A4)")
    else:
        for v, n in getattr(CFG, "REDIRECCIONES", []):
            if f" {n} [L,R=301]" not in _ht: err.append(f".htaccess: falta la redirección {v} → {n}")
        if "X-Robots-Tag" in _ht: err.append(".htaccess: lleva X-Robots-Tag (el noindex es solo de la vista previa, vercel.json; Turing M1)")
        if '<Files "vercel.json">' not in _ht: err.append(".htaccess: no niega vercel.json (Bruno M6)")
        if "text/javascript" not in _ht: err.append(".htaccess: la compresión y la caché no cubren text/javascript (Bruno M6)")
    _rj = os.path.join(SITIO, "resenas.json")
    if os.path.exists(_rj):
        _claves = [k for k in json.load(open(_rj, encoding="utf-8")) if str(k).startswith("_")]
        if _claves: err.append(f"resenas.json público con claves internas {_claves} (Bruno M6)")
    _rb = open(os.path.join(SITIO, "robots.txt"), encoding="utf-8").read() if os.path.exists(os.path.join(SITIO, "robots.txt")) else ""
    if "Rastreadores de IA" not in _rb: err.append("robots.txt: falta el comentario con la decisión sobre rastreadores de IA y su fecha (Turing M1)")
    if "Disallow: /enviar.php" not in _rb: err.append("robots.txt: enviar.php sin Disallow")
    if not os.path.exists(os.path.join(RAIZ, "herramientas", "PUBLICAR.md")): avi.append("falta herramientas/PUBLICAR.md (lista del día de publicar; Bruno A4)")
except Exception as e:
    avi.append(f"control de archivos de servidor: no se pudo ejecutar ({e})")

print(f"Páginas HTML: {len(paginas)}")
print(f"ERRORES: {len(err)}"); [print("  ✗", e) for e in err[:80]]
print(f"AVISOS: {len(avi)}"); [print("  ·", a) for a in avi[:80]]
print(f"PENDIENTES DE MATERIAL (no bloquean; se cierran cuando llega el material): {len(pend)}"); [print("  ○", a) for a in pend]
print("No aplican (ver cabecera del archivo): Lector:/Decide: en el texto · objeto 3D · casos · reseñas de ejemplo")
sys.exit(1 if err else 0)
