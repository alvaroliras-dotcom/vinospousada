# -*- coding: utf-8 -*-
"""GYF-Rayo · Lee los textos (contenido/paginas/*.md) y los convierte en datos de página.
Formato de cada archivo (paso 27):
  cabecera (URL, Title, Meta description, Keyword principal, H1 y, opcionales, Etiqueta y Entrada corta)
  ---  cuerpo en markdown  ---  FAQ  ---  Notas para Álvaro (no se publica)
"""
import html, json, os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINAS = os.path.join(RAIZ, "contenido", "paginas")


def esc(t):
    return html.escape(t, quote=False)


def inline(t):
    """Markdown en línea: enlaces, negritas, marcas del contrato de enlaces."""
    t = re.sub(r"\s*(🔗|🆕)", "", t)
    out, pos = [], 0
    for m in re.finditer(r"\[(?:LINK )?([^\]]+)\]\(([^)]+)\)", t):
        out.append(esc(t[pos:m.start()]))
        texto, url = m.group(1), m.group(2)
        attrs = ""
        if url.startswith("tel:"):
            attrs = ' class="tel"'
        elif url.startswith("http"):
            attrs = ' rel="noopener" target="_blank"'
        out.append(f'<a href="{html.escape(url)}"{attrs}>{esc(texto)}</a>')
        pos = m.end()
    out.append(esc(t[pos:]))
    s = "".join(out)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    return re.sub(r"\s+$", "", s)


def bloques(md):
    """Divide markdown en bloques: ('h2'|'h3'|'p'|'ul'|'ol'|'tabla', contenido).
    Tablas (| a | b | + |---|---|) → ('tabla', (cabeceras, filas)). Citas (> …) → párrafo normal sin el «>»."""
    res, par, lista, tipo, tabla = [], [], [], None, []

    def celdas(l):
        return [c.strip() for c in l.strip().strip("|").split("|")]

    def cerrar_tabla():
        nonlocal tabla
        if tabla:
            filas = [celdas(l) for l in tabla if not re.fullmatch(r"\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?", l.strip())]
            if len(filas) >= 2:
                res.append(("tabla", (filas[0], filas[1:])))
            elif filas:
                res.append(("p", " ".join(" ".join(f) for f in filas)))
            tabla = []

    def cerrar():
        nonlocal par, lista, tipo
        if par:
            res.append(("p", " ".join(par)))
            par = []
        if lista:
            res.append((tipo, lista))
            lista, tipo = [], None

    for linea in md.split("\n"):
        l = linea.rstrip()
        if l.lstrip().startswith("|") and l.count("|") >= 2:
            cerrar(); tabla.append(l); continue
        cerrar_tabla()
        m = re.match(r"^\s*>\s?(.*)", l)
        if m:
            l = linea = m.group(1).rstrip()
        if not l.strip():
            cerrar(); continue
        m = re.match(r"^(#{2,4})\s+(.*)", l)
        if m:
            cerrar(); res.append(("h" + str(len(m.group(1))), m.group(2).strip())); continue
        m = re.match(r"^\s*[-*]\s+(?:[-*]\s+)?(.*)", l)
        if m:
            if par: res.append(("p", " ".join(par))); par = []
            if tipo not in (None, "ul"): cerrar()
            tipo = "ul"; lista.append(m.group(1)); continue
        m = re.match(r"^\s*(\d+)\.\s+(.*)", l)
        if m:
            if par: res.append(("p", " ".join(par))); par = []
            if tipo not in (None, "ol"): cerrar()
            tipo = "ol"; lista.append(m.group(2)); continue
        if lista and linea.startswith("  "):
            lista[-1] += " " + l.strip(); continue
        if lista: cerrar()
        par.append(l.strip())
    cerrar_tabla()
    cerrar()
    return res


def leer(ruta):
    txt = open(ruta, encoding="utf-8").read()
    partes = re.split(r"\n---\s*\n", txt)
    cab = {}
    for l in partes[0].split("\n"):
        if ":" in l:
            k, v = l.split(":", 1)
            cab[k.strip()] = v.strip()
    cuerpo, faq = "", []
    for p in partes[1:]:
        ps = p.strip()
        if ps.startswith("Notas para"):
            continue
        if ps.startswith("FAQ"):
            for m in re.finditer(r"\*\*(.+?)\*\*\s*(.+?)(?=\n\s*\n\*\*|\Z)", ps[3:], re.S):
                faq.append((m.group(1).strip(), " ".join(m.group(2).split())))
            continue
        if not cuerpo:
            cuerpo = p
    if cab.get("Plantilla"):
        _PLANTILLAS[cab.get("URL", "/")] = cab["Plantilla"].strip()
    b = bloques(cuerpo)
    # Si el cuerpo empieza con un H1 repetido, se quita (el H1 va en la cabecera)
    if b and b[0][0] == "h1":
        b = b[1:]
    return {
        "archivo": os.path.basename(ruta),
        "url": cab.get("URL", "/"),
        "title": cab.get("Title", ""),
        "meta": cab.get("Meta description", ""),
        "keyword": cab.get("Keyword principal", ""),
        "h1": cab.get("H1", ""),
        "etiqueta": cab.get("Etiqueta", ""),            # opcional: encima del H1 (si falta, TEXTOS["etiqueta_portada"])
        "entrada_corta": cab.get("Entrada corta", ""),  # opcional: justo bajo el H1 (si falta, TEXTOS["corta…"])
        "plantilla": cab.get("Plantilla", ""),          # opcional: tipo de página explícito (inicio, servicio, zona, empresa, contacto, catalogo, ficha-vino, hub-do, hub-turbio, hub-licores, licor)
        "ficha_cab": {k: cab[k] for k in ("D.O.", "Tipo", "Uva", "Graduación", "Foto") if k in cab},   # espejo de catalogo.json en la cabecera (controles.py comprueba que coinciden)
        "producto": cab.get("Producto", ""),            # fichas: slug del producto en contenido/catalogo.json
        "denominacion": cab.get("Denominacion", ""),    # hubs de D.O.: clave de DENOMINACIONES en config.py
        "ruta": ruta,
        "bloques": b,
        "faq": faq,
    }


def todas():
    return [leer(os.path.join(PAGINAS, f)) for f in sorted(os.listdir(PAGINAS)) if f.endswith(".md")]


_PLANTILLAS = {}   # url → valor del campo «Plantilla:» de su cabecera (si lo lleva)
PLANTILLA_A_TIPO = {"inicio": "home", "servicio": "servicio", "zona": "municipio", "empresa": "empresa", "contacto": "contacto",
                    "catalogo": "catalogo", "ficha-vino": "ficha", "hub-do": "denominacion", "hub-turbio": "turbio",
                    "hub-licores": "licores", "licor": "licor", "legal": "legal"}


def tipo_de(url):
    """Tipo de página. Manda el campo «Plantilla:» de la cabecera del texto si lo lleva (inicio · servicio · zona · empresa ·
    contacto · catalogo · ficha-vino · hub-do · hub-turbio · hub-licores · licor); si no, se deduce de la URL: los de Rayo
    (home, municipio, empresa, contacto, zona, marca, servicio) más los del catálogo (010-Jesper): catalogo (rejilla
    filtrable), ficha (/comprar/<slug>/), denominacion (hub de D.O.), turbio (hub con la banda oscura), licores (hub) y
    licor (/licores/<slug>/)."""
    from config import URLS as U
    if not _PLANTILLAS and os.path.isdir(PAGINAS):
        for f in os.listdir(PAGINAS):
            if f.endswith(".md"):
                for l in open(os.path.join(PAGINAS, f), encoding="utf-8").read().split("\n---", 1)[0].split("\n"):
                    if l.startswith("Plantilla:"):
                        _PLANTILLAS.setdefault("__leido__", True)
                        u = [x for x in open(os.path.join(PAGINAS, f), encoding="utf-8").read().split("\n---", 1)[0].split("\n") if x.startswith("URL:")]
                        if u: _PLANTILLAS[u[0].split(":", 1)[1].strip()] = l.split(":", 1)[1].strip()
        _PLANTILLAS.setdefault("__leido__", True)
    if url in _PLANTILLAS:
        return PLANTILLA_A_TIPO.get(_PLANTILLAS[url], _PLANTILLAS[url])
    if url == "/":
        return "home"
    if U.get("municipio") and url.startswith(U["municipio"]):
        return "municipio"
    if url == U["empresa"]:
        return "empresa"
    if url == U["contacto"]:
        return "contacto"
    if U.get("hub") and url == U["hub"]:
        return "zona"
    if U.get("marca") and url.startswith(U["marca"]):
        return "marca"
    if U.get("catalogo") and url == U["catalogo"]:
        return "catalogo"
    if U.get("ficha") and url.startswith(U["ficha"]):
        return "ficha"
    if U.get("denominacion") and url.startswith(U["denominacion"]):
        return "denominacion"
    if U.get("turbio") and url == U["turbio"]:
        return "turbio"
    if U.get("licores") and url == U["licores"]:
        return "licores"
    if U.get("licores") and url.startswith(U["licores"]):
        return "licor"
    return "servicio"


_CAT = None


def catalogo():
    """Productos de contenido/catalogo.json (lista de dicts), con su slug. Vacío si el cliente no tiene catálogo."""
    global _CAT
    if _CAT is None:
        ruta = os.path.join(RAIZ, "contenido", "catalogo.json")
        _CAT = json.load(open(ruta, encoding="utf-8"))["productos"] if os.path.exists(ruta) else []
        for p in _CAT:
            p["slug"] = p["url"].strip("/").split("/")[-1]
    return _CAT


def producto(slug_o_url):
    for p in catalogo():
        if p["slug"] == slug_o_url or p["url"] == slug_o_url:
            return p
    return None


def fotos_por_url():
    ruta = os.path.join(RAIZ, "generador", "fotos_plan.json")
    if not os.path.exists(ruta):
        return {}
    plan = json.load(open(ruta, encoding="utf-8"))["rows"]
    from config import ALT_CORREGIDO
    d = {}
    for r in plan:
        n, archivo, url, alt = r[0], r[1], r[2], r[3]
        alt = ALT_CORREGIDO.get(archivo, alt)
        d.setdefault(url, []).append({"archivo": archivo, "alt": alt})
    return d
