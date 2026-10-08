# -*- coding: utf-8 -*-
"""GYF-Rayo + 010-Jesper · Genera sitio/ entero a partir de contenido/. Orden: build.py → rematar.py → controles.py.
Uso:  python3 generador/build.py && python3 generador/rematar.py && python3 generador/controles.py

Base GYF (schema, sitemap, llms.txt, estado en vivo, FAQ, cookies y GTM) + piezas de Rayo (003) + piezas del catálogo
de Jesper (010, construidas para Pousada): portada con foto en caja, la estantería (franja clavada que avanza de lado),
bloque partido con texto que se enciende, lista con filete, cajas 2/3 + 1/3, banda oscura «el grifo del turbio», la casa
con hitos, reparto con píldoras, tarifa con formulario de cinco campos, catálogo filtrable, ficha de producto
(Product sin precio), hubs de D.O., de turbio y de licores, pie oscuro con frase por página.
Dónde está cada efecto: MAPA-DEL-TEMA.md (Rayo) y MAPA-DEL-TEMA-POUSADA.md (lo nuevo)."""
import html, json, math, os, re, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import datos
from datos import inline, esc
A = lambda x: html.escape(str(x), quote=True)
from config import (DOMINIO, NEGOCIO as N, SERVICIOS_HOME, SERVICIOS_SECCION, SERVICIOS_TITULO, SERVICIOS_TEXTO,
                    OPINIONES, URLS, PREFIJOS_MUNICIPIO, NOMBRE_CORTO, MUNICIPIOS, MUNICIPIO_ANCLA, CONTACTO_INDEXABLE,
                    LEGALES, CONTACTO_YA, BANDA_TIT, LLMS_PRINCIPALES, LLMS_MARCAS, TEXTOS, FICHA, MARCA, OBJETO_PORTADA,
                    CASOS, CASOS_VER, CINTA_PORTADA, CINTA_SECUNDARIA, CIFRAS, CIFRAS_EN, PASOS_ICONOS, ICONO_URL,
                    CTA_H2, CTA_ULTIMO, ZONA_H2, HORARIO_H2, CTA_EXTRA, texto)
import config as CFG
import plantilla as T

RAIZ = datos.RAIZ
SITIO = os.path.join(RAIZ, "sitio")
PAGINAS = datos.todas()
POR_URL = {p["url"]: p for p in PAGINAS}
CAT = datos.catalogo()
DEN = getattr(CFG, "DENOMINACIONES", {})
OPINIONES_SECCION = getattr(CFG, "OPINIONES_SECCION", True)
MAPA_SECCION = getattr(CFG, "MAPA_SECCION", True)
FORM = getattr(CFG, "FORMULARIO", None)

# ---------- Municipios: los de config (MUNICIPIOS) y, si hay hub, los enlaces del hub ----------
PUEBLO = dict(MUNICIPIOS)
_PREF = "|".join(re.escape(x) for x in PREFIJOS_MUNICIPIO) or "(?!)"
if URLS.get("hub"):
    for t, b in POR_URL.get(URLS["hub"], {"bloques": []})["bloques"]:
        if t == "ul":
            for it in b:
                m = re.match(rf"\[(?:LINK )?(?:{_PREF}) ([^\]]+)\]\(({re.escape(URLS['municipio'])}[^)]+)\)", it)
                if m:
                    PUEBLO.setdefault(m.group(2), m.group(1))
BASE = N["localidad"]
NOMBRE_CORTO = dict(NOMBRE_CORTO)
for k, (n, _, _, _) in DEN.items():
    NOMBRE_CORTO.setdefault(f"{URLS.get('denominacion', '/denominaciones/')}{k}/", n)
for pr in CAT:
    NOMBRE_CORTO.setdefault(pr["url"], pr["nombre"])
ES_CTA = re.compile(CTA_H2, re.I)
ES_WIDGET = lambda c: c.startswith("(Widget de reseñas") or c.strip() == "[[RESEÑAS]]"


def nombre(url):
    return NOMBRE_CORTO.get(url) or PUEBLO.get(url) or url.strip("/")


def migas(url):
    if url == "/":
        return []
    cad = [("/", "Inicio")]
    t = datos.tipo_de(url)
    if t == "municipio" and URLS.get("hub") and URLS["hub"] in POR_URL:
        cad.append((URLS["hub"], nombre(URLS["hub"])))
    elif t == "ficha":
        if URLS.get("catalogo") in POR_URL:
            cad.append((URLS["catalogo"], nombre(URLS["catalogo"])))
        pr = datos.producto(url)
        if pr and pr.get("familia") == "turbio" and URLS.get("turbio") in POR_URL:
            cad.append((URLS["turbio"], nombre(URLS["turbio"])))
        elif pr and pr.get("do"):
            u = f"{URLS['denominacion']}{pr['do']}/"
            if u in POR_URL:
                cad.append((u, nombre(u)))
    elif t == "denominacion" and URLS.get("catalogo") in POR_URL:
        cad.append((URLS["catalogo"], nombre(URLS["catalogo"])))
    else:
        partes = url.strip("/").split("/")
        for i in range(1, len(partes)):
            u = "/" + "/".join(partes[:i]) + "/"
            if u in POR_URL:
                cad.append((u, nombre(u)))
    cad.append((url, nombre(url)))
    return cad


def migas_html(url):
    c = migas(url)
    if not c:
        return ""
    li = [f'<li><a href="{u}">{esc(n)}</a></li>' if i < len(c) - 1 else f'<li aria-current="page">{esc(n)}</li>' for i, (u, n) in enumerate(c)]
    return f'<nav class="migas" aria-label="Migas de pan"><ol>{"".join(li)}</ol></nav>'


# ---------- Schema ----------
NEG_ID = DOMINIO + "/#negocio"


def negocio_schema():
    area = [BASE] + [v for k, v in PUEBLO.items() if v != BASE]
    d = {
        "@type": N["schema_tipo"], "@id": NEG_ID, "name": N["nombre"],
        "alternateName": N["nombre_largo"], "legalName": N["razon_social"],
        "url": DOMINIO + "/", "telephone": N["telefono_e164"], "email": N["email"],
        "logo": DOMINIO + "/marca/" + MARCA["simbolo"], "image": DOMINIO + "/og-image.jpg",
        "address": {"@type": "PostalAddress", "streetAddress": N["calle"], "postalCode": N["cp"],
                    "addressLocality": N["localidad"], "addressRegion": N["region"], "addressCountry": "ES"},
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification", "dayOfWeek": N["dias_schema"],
                                       "opens": N["abre"], "closes": N["cierra"]}],
        "areaServed": [{"@type": "AdministrativeArea" if "provincia" in a.lower() else "City", "name": a} for a in area],
        "geo": {"@type": "GeoCoordinates", "latitude": N["lat"], "longitude": N["lng"]},
        "knowsAbout": N["knows_about"],
    }
    if N.get("cid") not in ("0", "", None):
        d["hasMap"] = FICHA
        d["sameAs"] = [FICHA]
    if int(N["resenas"]) > 0:
        d["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": N["valoracion"].replace(",", "."),
                                "reviewCount": int(N["resenas"]), "bestRating": "5", "worstRating": "1"}
    if N.get("cif"):
        d["taxID"] = N["cif"]
    if N.get("precio"):
        d["priceRange"] = N["precio"]
    if N.get("pago"):
        d["paymentAccepted"] = N["pago"]
    if N.get("fundacion"):
        d["foundingDate"] = str(N["fundacion"])
    pe = N.get("persona")
    if pe:
        d["founder" if not pe.get("cargo") else "employee"] = {"@type": "Person", "@id": DOMINIO + "/#" + pe["id"], "name": pe["nombre"],
                                                                 "jobTitle": pe["cargo"], "worksFor": {"@id": NEG_ID}}
    return d


def producto_schema(p, pr):
    url = DOMINIO + p["url"]
    props = [("Denominación", DEN[pr["do"]][0] if pr.get("do") in DEN else ("Sin denominación de origen" if pr.get("familia") == "vino" else "")),
             ("Tipo", pr.get("tipo", "")), ("Uva", pr.get("uva", "")), ("Graduación", pr.get("graduacion", "")),
             ("Formato", pr.get("formato", "")), ("Temperatura de servicio", pr.get("temperatura", ""))]
    d = {"@type": "Product", "@id": url + "#producto", "name": pr["nombre"], "description": p["meta"], "url": url,
         "category": "Licores" if pr.get("familia") == "licor" else "Vino",
         "additionalProperty": [{"@type": "PropertyValue", "name": k, "value": v} for k, v in props if v],
         "manufacturer": None, "offers": None}
    d = {k: v for k, v in d.items() if v is not None}
    if pr.get("foto"):
        d["image"] = f"{DOMINIO}/img/{pr['foto'].rsplit('.', 1)[0]}-840.{'png' if pr['foto'].endswith('.png') else 'jpg'}"
    # Sin precio (la web no los publica): se declara disponibilidad por pedido al distribuidor, sin «offers»
    d["isRelatedTo"] = {"@id": NEG_ID}
    return d


def schema_de(p):
    url = DOMINIO + p["url"]
    g = [negocio_schema(),
         {"@type": "WebPage", "@id": url + "#pagina", "url": url, "name": p["title"], "description": p["meta"],
          "inLanguage": "es", "isPartOf": {"@id": DOMINIO + "/#web"}, "about": {"@id": NEG_ID},
          **({"dateModified": p["mod"]} if p.get("mod") else {})},
         {"@type": "WebSite", "@id": DOMINIO + "/#web", "url": DOMINIO + "/", "name": N["nombre"], "inLanguage": "es",
          "publisher": {"@id": NEG_ID}}]
    c = migas(p["url"])
    if c:
        g.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMINIO + u} for i, (u, n) in enumerate(c)]})
    t = datos.tipo_de(p["url"])
    if t in ("servicio", "marca", "municipio"):
        g.append({"@type": "Service", "name": p["h1"], "serviceType": N["servicio_tipo"], "provider": {"@id": NEG_ID},
                  "url": url, "areaServed": {"@type": "AdministrativeArea" if "provincia" in PUEBLO.get(p["url"], BASE).lower() else "City",
                                             "name": PUEBLO.get(p["url"], BASE)}})
    if t in ("ficha", "licor"):
        pr = datos.producto(p["url"])
        if pr:
            g.append(producto_schema(p, pr))
    if t in ("catalogo", "denominacion", "licores", "turbio"):
        lista = productos_de(t, p)
        if lista:
            g.append({"@type": "ItemList", "name": p["h1"], "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "url": DOMINIO + pr["url"], "name": pr["nombre"]} for i, pr in enumerate(lista)]})
    if p["faq"]:
        g.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", inline(a))}}
            for q, a in p["faq"]]})
    return {"@context": "https://schema.org", "@graph": g}


def productos_de(t, p):
    """Los productos que lista una página hub."""
    if t == "catalogo":
        return [pr for pr in CAT if pr["url"] in POR_URL]
    if t == "denominacion":
        return [pr for pr in CAT if pr.get("do") == p.get("denominacion") and pr["url"] in POR_URL]
    if t == "turbio":
        return [pr for pr in CAT if pr.get("familia") == "turbio" and pr["url"] in POR_URL]
    if t == "licores":
        return [pr for pr in CAT if pr.get("familia") == "licor" and pr["url"] in POR_URL]
    return []


# ---------- Utilidades de texto ----------
def plano(txt):
    return re.sub(r"<[^>]+>", "", inline(txt))


def palabras(txt):
    return len(plano(re.sub(r"\[(?:LINK )?([^\]]+)\]\([^)]+\)", r"\1", txt)).split())


def slug(t):
    import unicodedata
    s = unicodedata.normalize("NFKD", plano(t)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:48] or "seccion"


def h2_gris(t):
    """R11 · Rayo: la segunda mitad del titular va en gris y se enciende palabra a palabra con el scroll."""
    w = plano(t).split()
    if len(w) < 3:
        return esc(plano(t))
    k = max(1, math.ceil(len(w) * .5))
    return f'{esc(" ".join(w[:k]))} <span class="gris">{esc(" ".join(w[k:]))}</span>'


def h2c(t):
    return "h2 enciende" + (" h2--largo" if len(plano(t)) > 32 else "")


def secciones(bl):
    intro, secs, act = [], [], None
    for b in bl:
        if b[0] == "h2":
            act = {"h2": b[1], "bl": []}; secs.append(act)
        elif act is None:
            intro.append(b)
        else:
            act["bl"].append(b)
    return intro, secs


def empieza(sec, clave):
    v = getattr(CFG, clave, None)
    return bool(v) and plano(sec["h2"]).lower().startswith(v.lower())


# ---------- Bloques de texto → HTML ----------
SOLO_ENLACE = re.compile(r"^\s*\[(?:LINK )?[^\]]+\]\([^)]+\)\s*(🔗|🆕)?\s*$")
ENLACE_DESC = re.compile(r"^\s*\*\*\[(?:LINK )?([^\]]+)\]\(([^)]+)\)[:.]?\*\*[:.]?\s*(.*)$")   # - **[Nombre](/url/):** texto
ENLACE_DESC2 = re.compile(r"^\s*\[(?:LINK )?([^\]]+)\]\(([^)]+)\)[:.]\s*(.+)$")                # - [Nombre](/url/): texto
FILA = re.compile(r"^\*\*(.+?)\*\*\s*(.+)$")
URL_1 = re.compile(r"\]\((/[^)]*)\)")
ETQ_URL = {u: e for _, _, u, _, e, _ in SERVICIOS_HOME}


def filas_html(items, clase=""):
    """«**Título.** texto» seguidos (3 o más) → filas de Rayo con línea, icono y «/ 01» (R27: las demás se apagan)."""
    out = []
    for i, (tit, cuerpo) in enumerate(items, 1):
        m = URL_1.search(cuerpo)
        u = m.group(1) if m else None
        ic = T.ico(ICONO_URL[u]) if u in ICONO_URL else T.simbolo()
        etq = "".join(f"<li>{esc(e)}</li>" for e in ETQ_URL.get(u, []))
        out.append(f'<li class="fila rv"><span class="fila__ico">{ic}</span><h3 class="fila__tit">{inline(tit.rstrip(".:"))}</h3>'
                   f'<div class="fila__txt"><p>{inline(cuerpo)}</p></div>'
                   f'{f"<ul class=fila__etq>{etq}</ul>" if etq else ""}<span class="fila__num" aria-hidden="true">/ {i:02d}</span></li>')
    return f'<ol class="filas {clase}">{"".join(out)}</ol>'


def lista_filete(items):
    """Lista numerada 01-05 con filete y flecha (Antra .feature-item): «**Título.** texto» de una lista con viñetas."""
    out = []
    for i, it in enumerate(items, 1):
        m = FILA.match(it)
        tit, cuerpo = (m.group(1), m.group(2)) if m else (it, "")
        out.append(f'<li class="filete rv"><span class="filete__num">{i:02d}</span><div class="filete__txt"><h3>{inline(tit.rstrip(":"))}</h3>'
                   f'{f"<p>{inline(cuerpo)}</p>" if cuerpo else ""}</div><span class="filete__flecha" aria-hidden="true">{T.ico("flecha-diagonal")}</span></li>')
    return f'<ol class="lista-filete">{"".join(out)}</ol>'


def pasos_html(items):
    out = []
    for i, it in enumerate(items):
        ic = T.ico(PASOS_ICONOS[i]) if i < len(PASOS_ICONOS) else ""
        out.append(f'<li class="paso rv"><span class="paso__n">{i + 1:02d}</span>{f"<span class=paso__ico>{ic}</span>" if ic else ""}<span class="paso__txt">{inline(it)}</span></li>')
    return f'<ol class="pasos{"" if PASOS_ICONOS else " pasos--sin-ico"}">{"".join(out)}</ol>'


def tabla_html(cab, filas):
    th = "".join(f'<th scope="col">{inline(h)}</th>' for h in cab)
    trs = []
    for f in filas:
        f = (f + [""] * len(cab))[:len(cab)]
        trs.append("<tr>" + "".join(f'<td data-col="{A(plano(h))}">{inline(c)}</td>' for h, c in zip(cab, f)) + "</tr>")
    return f'<div class="tabla rv"><table class="tabla-datos"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'


def enlaces_desc_html(items):
    """Lista de «**[Nombre](/url/):** descripción» → tarjetas de enlace con descripción (hubs del catálogo)."""
    out = []
    for x in items:
        m = ENLACE_DESC.match(x) or ENLACE_DESC2.match(x)
        if m:
            n, u, d = m.groups()
            pr = datos.producto(u)
            mini = T.producto_img(pr["foto"], "", "120px", "enl__mini") if pr and pr.get("foto") else ""
            out.append(f'<li class="enl rv"><a href="{A(u)}">{mini}<span class="enl__txt"><strong>{esc(n)}</strong><span>{inline(d)}</span></span>{T.ico("flecha-diagonal")}</a></li>')
        else:
            m2 = re.match(r"^\*\*(.+?)[:.]?\*\*[:.]?\s*(.*)$", x)
            if m2:
                out.append(f'<li class="enl enl--sin rv"><span class="enl__txt"><strong>{inline(m2.group(1))}</strong><span>{inline(m2.group(2))}</span></span></li>')
            else:
                out.append(f'<li class="enl enl--sin rv"><span class="enl__txt"><span>{inline(x)}</span></span></li>')
    return f'<ul class="enlaces-desc">{"".join(out)}</ul>'


def render_bloques(bl, estructura=None, filete=False):
    """Markdown en bloques → HTML. estructura (lista) recibe lo que va a ancho completo en la home."""
    out, i, tras = [], 0, [False]

    def pon(h, estr=False):
        if estructura is not None and (estr or tras[0]):
            estructura.append(h if estr else f'<div class="prosa blq__tras rv">{h}</div>'); tras[0] = True
        else:
            out.append(h)
    while i < len(bl):
        t, c = bl[i]
        if t == "p":
            if ES_WIDGET(c) or c.startswith("(Formulario") or c.strip() in ("[[FORMULARIO]]", "[[MAPA]]"):
                i += 1; continue
            grupo = []
            while i < len(bl) and bl[i][0] == "p" and FILA.match(bl[i][1]):
                m = FILA.match(bl[i][1]); grupo.append((m.group(1), m.group(2))); i += 1
            if len(grupo) >= 3:
                pon(filas_html(grupo), True); continue
            for tit, cu in grupo:
                pon(f"<p><strong>{inline(tit)}</strong> {inline(cu)}</p>")
            if grupo:
                continue
            pon(f"<p>{inline(c)}</p>")
        elif t in ("h3", "h4"):
            pon(f"<{t}>{inline(c)}</{t}>")
        elif t == "ul":
            if all(SOLO_ENLACE.match(x) for x in c):
                items = []
                for x in c:
                    m = re.search(r"\[(?:LINK )?([^\]]+)\]\(([^)]+)\)", x)
                    items.append(f'<li><a href="{m.group(2)}">{esc(m.group(1))}{T.ico("flecha-diagonal")}</a></li>')
                pon(f'<ul class="enlaces">{"".join(items)}</ul>', True)
            elif sum(1 for x in c if ENLACE_DESC.match(x) or ENLACE_DESC2.match(x)) >= 2:
                pon(enlaces_desc_html(c), True)
            elif filete and all(FILA.match(x) for x in c):
                pon(lista_filete(c), True)
            else:
                vin = T.simbolo("vineta")
                pon('<ul class="lista">' + "".join(f"<li>{vin}<span>{inline(x)}</span></li>" for x in c) + "</ul>")
        elif t == "ol":
            pon(pasos_html(c), True)
        elif t == "tabla":
            pon(tabla_html(*c), True)
        i += 1
    return re.sub(r" {2,}", " ", "\n".join(out))


# ---------- Piezas comunes ----------
def pueblo_de(url):
    return PUEBLO.get(url, BASE)


def etiqueta_y_entrada(p):
    pb = pueblo_de(p["url"])
    muni = datos.tipo_de(p["url"]) == "municipio"
    et = esc(p.get("etiqueta") or texto("etiqueta_portada", pueblo=pb))
    en = inline(p["entrada_corta"]) if p.get("entrada_corta") else esc(texto("corta_municipio" if muni else "corta", pueblo=pb))
    return et, en


def intro_parrafos(intro):
    return [c for t, c in intro if t == "p" and not ES_WIDGET(c)]


def botones(url, t, nombre_pr="", slug_pr="", claro=False):
    """Pareja de botones de la página según la tabla de llamadas a la acción (misma fuente que el pie)."""
    f = T.frase_pie(url, t, nombre_pr, slug_pr) or ("", "", "tarifa", "llamar")
    b1, b2 = f[2], f[3]
    def b(clave, principal):
        cls = ("btn--blanco" if claro else "btn--acento") if principal else ("btn--linea-claro" if claro else "btn--linea")
        if clave == "tarifa":
            return T.btn_tarifa(cls, extra=' data-zona="portada_boton"')
        if clave == "llamar":
            return T.btn_llamar(cls, extra=' data-zona="portada_boton"')
        if clave == "whatsapp":
            return T.btn_whatsapp(cls, t="Escribir por WhatsApp")
        tx, u = clave
        return T.boton(tx.format(nombre=nombre_pr, slug=slug_pr), u.format(nombre=nombre_pr, slug=slug_pr), cls)
    return b(b1, True) + b(b2, False)


def confianza_html(clase=""):
    c = getattr(CFG, "PORTADA", {}).get("confianza") or texto("form_confianza")
    return f'<p class="confianza {clase}">{esc(c)}</p>'


# ---------- Portada de la home: titular + foto grande en caja que sobresale (Jesper A1 + Antra index-7) ----------
def portada_foto(p, intro):
    etiqueta, _ = etiqueta_y_entrada(p)
    ps = intro_parrafos(intro)
    entr = f'<p class="entradilla portada__entr">{inline(ps[0])}</p>' if ps else ""
    PO = getattr(CFG, "PORTADA", {})
    foto = T.foto(PO["foto"], PO.get("alt", ""), "(max-width: 1024px) 100vw, 54vw", prioridad=True, clase="portada__img") if PO.get("foto") else T.pieza_tipografica(N["nombre"], texto("oficio"), "portada__tipo")
    return f"""<section class="portada" data-portada>
 <div class="contenedor portada__in">
  <div class="portada__txt">
   <p class="antetitulo">{etiqueta}</p>
   <h1 class="h1 h1--portada" data-palabras>{esc(p['h1'])}</h1>
   {entr}
   <div class="acciones" data-acciones>{botones("/", "home")}</div>
   {confianza_html()}
  </div>
  <figure class="portada__foto" data-paralaje>{foto}</figure>
 </div>
</section>
"""


# ---------- La estantería: franja clavada que avanza de lado (Jesper F1) con cinta de D.O. (C5) ----------
def estanteria():
    E = getattr(CFG, "ESTANTERIA", [])
    if not E:
        return ""
    tarj = []
    for u, tit, sub, foto, oscura in E:
        img = T.producto_img(foto, "", "(max-width: 767px) 120px, 150px", "estante__img" + (" estante__img--foto" if not foto.endswith(".png") else "")) if foto else T.pieza_tipografica(tit, sub, "estante__tipo")
        tarj.append(f'<li><a class="estante{" estante--oscuro" if oscura else ""}" href="{u}">{img}<span class="estante__tit">{esc(tit)}</span><span class="estante__sub">{esc(sub)}</span></a></li>')
    return f"""<section class="estanteria" aria-labelledby="estanteria-tit" data-estanteria>
 {T.cinta(CINTA_PORTADA, "cinta--do", -1)}
 <div class="contenedor estanteria__cab">
  <h2 id="estanteria-tit" class="sr">Entradas al catálogo</h2>
  <p class="antetitulo">{esc(getattr(CFG, "ESTANTERIA_ETIQUETA", ""))}</p>
  <p class="estanteria__nota">{esc(getattr(CFG, "ESTANTERIA_NOTA", ""))}</p>
 </div>
 <div class="estanteria__clavo" data-estanteria-clavo>
  <ul class="estanteria__pista" data-estanteria-pista>{"".join(tarj)}</ul>
 </div>
</section>
"""


# ---------- Bloque partido: antetítulo + H2 a la izquierda (clavado), texto que se enciende a la derecha ----------
def bloque_partido(sec, etiqueta=None, enlace=None, clase=""):
    cuerpo = render_bloques(sec["bl"])
    cuerpo = cuerpo.replace("<p>", '<p class="enciende">')
    enl = f'<a class="enlace-flecha" href="{enlace[1]}">{esc(enlace[0])} {T.ico("flecha-derecha")}</a>' if enlace else ""
    return f"""<section class="seccion partido-sec {clase}" id="{slug(sec['h2'])}">
 <div class="contenedor partido">
  <div class="partido__izq">
   {f'<p class="antetitulo">{esc(etiqueta)}</p>' if etiqueta else ""}
   <h2 class="h2">{esc(plano(sec['h2']))}</h2>
  </div>
  <div class="partido__der prosa prosa--grande">{cuerpo}{enl}</div>
 </div>
</section>
"""


def bloque_filete(sec, etiqueta=None):
    """«Cómo trabajamos»: lista numerada con filete sobre hueso a sangre."""
    cuerpo = render_bloques(sec["bl"], filete=True)
    return f"""<section class="seccion seccion--hueso filete-sec" id="{slug(sec['h2'])}">
 <div class="contenedor">
  <div class="encabezado">{f'<p class="antetitulo">{esc(etiqueta)}</p>' if etiqueta else ""}<h2 class="h2">{esc(plano(sec['h2']))}</h2></div>
  {cuerpo}
 </div>
</section>
"""


# ---------- Catálogo en la home: caja grande (2/3) + turbio y licores apilados (1/3) ----------
def cajas_catalogo(sec):
    ps = [c for t, c in sec["bl"] if t == "p"]
    p_cat = inline(ps[0]) if ps else ""
    p_tur = inline(ps[1]) if len(ps) > 1 else ""
    p_lic = inline(ps[2]) if len(ps) > 2 else ""
    pills = "".join(f'<li><a href="{URLS["denominacion"]}{k}/">{esc(n)}</a></li>' for k, (n, _, _, _) in DEN.items())
    bot = "".join(T.producto_img(f, "", "(max-width: 767px) 30vw, 180px", "caja__botella") for f in getattr(CFG, "CATALOGO_HOME_BOTELLAS", []))
    tf, ta = getattr(CFG, "TURBIO_FOTO", (None, ""))
    lf, la = getattr(CFG, "LICORES_FOTO", (None, ""))
    turbio_img = T.foto(tf, ta, "(max-width: 767px) 100vw, 220px", clase="caja__img") if tf else T.pieza_tipografica(nombre(URLS["turbio"]), "", "caja__tipo")
    licores_img = T.foto(lf, la, "(max-width: 767px) 100vw, 220px", clase="caja__img") if lf else T.pieza_tipografica(nombre(URLS["licores"]), "", "caja__tipo")
    return f"""<section class="seccion catalogo-sec" id="{slug(sec['h2'])}">
 <div class="contenedor">
  <div class="encabezado encabezado--ancho"><p class="antetitulo">{esc(nombre(URLS["catalogo"]))}</p><h2 class="h2">{esc(plano(sec['h2']))}</h2></div>
  <div class="cajas">
   <article class="caja caja--catalogo rv">
    <div class="caja__txt prosa"><p>{p_cat}</p><ul class="etiquetas" aria-label="Denominaciones">{pills}</ul>
     <a class="enlace-flecha" href="{URLS["catalogo"]}">{esc(texto("do_ver_todos"))} {T.ico("flecha-derecha")}</a></div>
    <div class="caja__botellas" aria-hidden="true" data-botellas>{bot}</div>
   </article>
   <article class="caja caja--turbio rv">{turbio_img}<div class="caja__txt"><h3>{esc(nombre(URLS["turbio"]))} gallego</h3><p>{p_tur}</p></div></article>
   <article class="caja caja--licores rv">{licores_img}<div class="caja__txt"><h3>Licores y aguardientes</h3><p>{p_lic}</p></div></article>
  </div>
 </div>
</section>
"""


# ---------- Banda oscura «El grifo del turbio» (pieza nueva del motivo del cliente, FIRMA §4) ----------
def grifo(url_pagina="/"):
    G = getattr(CFG, "GRIFO", None)
    if not G:
        return ""
    tit = inline(G["titulo"])   # *cursiva* → <em>: la palabra en --turbio
    f, alt = getattr(CFG, "TURBIO_FOTO_BANDA", (None, ""))
    img = T.foto(f, alt, "(max-width: 1024px) 100vw, 520px", clase="grifo__img") if f else T.pieza_tipografica("Vino turbio", "de grifo", "grifo__tipo")
    bt, bu = G["boton"]
    boton1 = T.boton(bt, bu, "btn--blanco") if bu != url_pagina else T.btn_tarifa("btn--blanco", "Solicitar tarifa del turbio", f"{URLS['contacto']}?interes=vino-turbio")
    return f"""<section class="grifo" aria-labelledby="grifo-tit" data-grifo>
 <div class="contenedor grifo__in">
  <figure class="grifo__foto">{img}<span class="grifo__nivel" aria-hidden="true" data-nivel></span></figure>
  <div class="grifo__txt">
   <p class="antetitulo antetitulo--claro">{esc(G["etiqueta"])}</p>
   <h2 class="h2 grifo__tit" id="grifo-tit" data-lineas>{tit}</h2>
   <p>{inline(G["texto"])}</p>
   <div class="acciones">{boton1}{T.btn_llamar("btn--linea-claro", extra=' data-zona="grifo"')}</div>
  </div>
 </div>
</section>
"""


# ---------- La casa: foto vertical en caja + hitos escritos ----------
def casa(sec):
    f, alt, pie = getattr(CFG, "CASA_FOTO", (None, "", ""))
    img = (f'<figure class="casa__foto" data-zoom>{T.foto(f, alt, "(max-width: 1024px) 100vw, 40vw")}<figcaption>{esc(pie)}</figcaption></figure>' if f
           else f'<div class="casa__foto">{T.pieza_tipografica(N["nombre"], str(N.get("fundacion", "")), "casa__tipo")}</div>')
    hitos = "".join(f'<div class="rv"><dt>{esc(a)}</dt><dd>{esc(b)}</dd></div>' for a, b in getattr(CFG, "CASA_HITOS", []))
    return f"""<section class="seccion casa-sec" id="{slug(sec['h2'])}">
 <div class="contenedor casa">
  {img}
  <div class="casa__txt">
   <p class="antetitulo">Tres generaciones</p>
   <h2 class="h2">{esc(plano(sec['h2']))}</h2>
   <div class="prosa prosa--grande">{render_bloques(sec['bl'])}</div>
   {f'<dl class="hitos">{hitos}</dl>' if hitos else ""}
  </div>
 </div>
</section>
"""


# ---------- Reparto: texto + píldoras de municipios + foto (o pieza tipográfica) ----------
def reparto(sec):
    mun = "".join(f'<li>{esc(m)}</li>' for m in getattr(CFG, "REPARTO_MUNICIPIOS", []))
    f, alt = getattr(CFG, "REPARTO_FOTO", (None, ""))
    img = f'<figure class="reparto__foto" data-zoom>{T.foto(f, alt, "(max-width: 1024px) 100vw, 40vw")}</figure>' if f else f'<div class="reparto__foto">{T.pieza_tipografica("Provincia de Madrid", "Reparto", "reparto__tipo")}</div>'
    return f"""<section class="seccion seccion--hueso reparto-sec" id="{slug(sec['h2'])}">
 <div class="contenedor reparto">
  <div class="reparto__txt">
   <p class="antetitulo">{esc(texto("zona_etiqueta"))}</p>
   <h2 class="h2">{esc(plano(sec['h2']))}</h2>
   <div class="prosa">{render_bloques(sec['bl'])}</div>
   <ul class="municipios" aria-label="Municipios">{mun}<li class="municipios__mas">{esc(texto("zona_resto"))}</li></ul>
  </div>
  {img}
 </div>
</section>
"""


# ---------- Formulario de solicitud de tarifa (cinco campos, sin casilla) ----------
URL_PRIVACIDAD = next((u for n, u in LEGALES if "privacidad" in n.lower()), "/politica-de-privacidad/")


def formulario(interes=None, compacto=False):
    """Cinco campos (nombre, negocio, tipo de negocio, teléfono, mensaje), sin casilla; línea informativa bajo el botón.
    data-intereses: diccionario clave → texto para prerrellenar el mensaje desde ?interes=…"""
    F = FORM
    tipos = "".join(f"<option>{esc(t)}</option>" for t in F["tipos_negocio"])
    intereses = dict(F.get("intereses", {}))
    for pr in CAT:
        intereses[pr["slug"]] = pr["nombre"]
    msg = f"Me interesa: {intereses[interes]}." if interes and interes in intereses else ""
    return f"""<form class="formulario rv" action="/enviar.php" method="post" aria-label="Solicitud de tarifa" data-intereses='{A(json.dumps(intereses, ensure_ascii=False))}'>
 <div class="aviso aviso--ok" id="form-ok" hidden><strong>{esc(F["ok_titulo"])}</strong> {esc(F["ok_texto"])}</div>
 <div class="aviso aviso--error" id="form-error" hidden><strong>{esc(F["error_titulo"])}</strong> {esc(F["error_texto"])}</div>
 <input type="hidden" name="tipo" value="contacto"><input type="hidden" name="pagina" value=""><input type="hidden" name="t" value="">
 <label>Nombre<input type="text" name="nombre" autocomplete="name" required maxlength="80" placeholder="Cómo quiere que le llamemos"></label>
 <label>Negocio<input type="text" name="negocio" autocomplete="organization" required maxlength="80" placeholder="Nombre de su bar, restaurante o tienda"></label>
 <div class="fila-form">
  <label>Tipo de negocio<select name="tipo_negocio" required data-tipo-negocio><option value="">Elija una opción</option>{tipos}</select></label>
  <label>Teléfono<input type="tel" name="telefono" autocomplete="tel" inputmode="tel" required pattern="[0-9 +()\\-]{{9,20}}" maxlength="20" placeholder="Le llamamos o le escribimos a este número"></label>
 </div>
 <label>{texto("form_mensaje_label")} <span class="opcional">(opcional)</span><textarea name="mensaje" maxlength="2000" placeholder="{A(texto('form_mensaje_ph'))}" data-mensaje>{esc(msg)}</textarea></label>
 <label class="trampa" aria-hidden="true">Web<input type="text" name="web" tabindex="-1" autocomplete="off"></label>
 <div class="acciones">{T.boton_form(F["boton"])}</div>
 <p class="confianza">{esc(F["confianza"])} <span data-particular hidden>{esc(F["confianza_particular"])}</span></p>
 <p class="casilla casilla--info">{esc(F["informativa"])}<a href="{URL_PRIVACIDAD}">Política de privacidad</a>.</p>
</form>"""


def tarifa(sec, p, interes=None):
    """«Pida su tarifa»: ficha de contacto a la izquierda (teléfono grande, WhatsApp, horario, correo) y formulario a la derecha."""
    ps = intro_parrafos(sec["bl"]) if sec else []
    txt = "".join(f"<p>{inline(x)}</p>" for x in ps)
    # En la home, el antetítulo del formulario es la pregunta de la tabla de Dani (el pie, pegado debajo, va compacto)
    fp = T.frase_pie(p["url"], datos.tipo_de(p["url"])) or ("", "", "", "")
    pregunta = fp[0]
    return f"""<section class="seccion tarifa-sec" id="tarifa">
 <div class="contenedor tarifa">
  <div class="tarifa__txt">
   <p class="antetitulo">{esc(pregunta if sec and pregunta else texto("contacto_etiqueta"))}</p>
   <h2 class="h2">{esc(plano(sec["h2"])) if sec else esc(texto("pie_titular"))}</h2>
   <div class="prosa">{txt}</div>
   <a class="tel-grande tel" href="tel:{N['telefono_e164']}" data-zona="tarifa">{N['telefono']}</a>
   <p class="tarifa__datos">{esc(texto("contacto_tambien"))} · <a href="mailto:{N['email']}">{N['email']}</a><br>{N['horario_texto']}. {esc(texto("contacto_horario_extra"))}</p>
   {T.estado()}
   <div class="acciones">{T.btn_whatsapp("btn--linea", t="Escribir por WhatsApp")}{T.btn_llamar("btn--linea")}</div>
  </div>
  <div class="tarifa__form">{formulario(interes)}</div>
 </div>
</section>
"""


# ---------- Cabeceras interiores ----------
def cab_interior(p, t, etiqueta=None, tinte=None, nombre_pr="", slug_pr="", con_botones=True, clase=""):
    et, _ = etiqueta_y_entrada(p)
    et = esc(etiqueta) if etiqueta else et
    intro, _ = secciones(p["bloques"])
    ps = intro_parrafos(intro)
    entr = f'<p class="entradilla">{inline(ps[0])}</p>' if ps else ""
    resto = "".join(f"<p>{inline(x)}</p>" for x in ps[1:])
    estilo = f' style="--tinte:{tinte}"' if tinte else ""
    racimo = f'<div class="cab-int__racimo" aria-hidden="true">{T.simbolo_trazado("cab-int__sim")}</div>' if tinte else ""
    bot = f'<div class="acciones" data-acciones>{botones(p["url"], t, nombre_pr, slug_pr)}</div>{confianza_html()}' if con_botones else ""
    return f"""<section class="cab-int{' cab-int--tinte' if tinte else ''} {clase}"{estilo}>
 <div class="contenedor">
  {migas_html(p['url'])}
  <div class="cab-int__grid">
   <div class="cab-int__txt">
    <p class="antetitulo">{et}</p>
    <h1 class="h1 h1--int" data-palabras>{esc(p['h1'])}</h1>
    {entr}
    {f'<div class="prosa cab-int__resto">{resto}</div>' if resto else ""}
    {bot}
   </div>
   {racimo}
  </div>
 </div>
</section>
"""


# ---------- Columna de lectura con índice clavado (Rayo) ----------
def lectura(p, secs_normales, extra_ind=(), filete=False):
    ind, blq = [], []
    for s in secs_normales:
        sid = slug(s["h2"])
        ind.append(f'<li><a href="#{sid}">{esc(plano(s["h2"]))}</a></li>')
        blq.append(f'<section class="lectura__blq" id="{sid}"><h2 class="h2-lect rv">{inline(s["h2"])}</h2><div class="prosa rv">{render_bloques(s["bl"], filete=filete)}</div></section>')
    for a, n in extra_ind:
        ind.append(f'<li><a href="{a}">{esc(n)}</a></li>')
    if p["faq"]:
        ind.append('<li><a href="#preguntas">Preguntas frecuentes</a></li>')
    if not blq:
        return ""
    return f"""<section class="lectura">
 <div class="contenedor lectura__in">
  <aside class="lectura__lado" aria-label="{A(texto('indice_titulo'))}">
   <details class="indice" data-indice open><summary>{esc(texto("indice_titulo"))}</summary><ol>{"".join(ind)}</ol></details>
   <div class="mini">
    <p class="mini__tit">{esc(texto("indice_llamar"))}</p>
    {T.estado()}
    {T.btn_llamar("btn--acento btn--peq", N['telefono'], ' data-zona="indice"')}
    {T.btn_tarifa("btn--linea btn--peq")}
   </div>
  </aside>
  <div class="lectura__col">{"".join(blq)}</div>
 </div>
</section>
"""


def faq_html(faq):
    if not faq:
        return ""
    items = "".join(f'<details class="rv" name="faq"{" open" if i == 1 else ""}><summary><span>{esc(q)}</span><i aria-hidden="true"></i></summary>'
                    f'<div class="faq__resp"><p>{inline(a)}</p></div></details>' for i, (q, a) in enumerate(faq, 1))
    return f"""<section class="seccion faq-sec" id="preguntas">
 <div class="contenedor faq">
  <div class="faq__cab">
   <p class="antetitulo">{esc(texto("faq_etiqueta"))}</p>
   <h2 class="h2">{esc(texto("faq_titulo"))}</h2>
   <a class="faq__tel tel" href="tel:{N['telefono_e164']}"><span>{esc(texto("faq_cta"))}</span><strong>{N['telefono']}</strong></a>
  </div>
  <div class="faq__lista">{items}</div>
 </div>
</section>
"""


def cierre(sec, p, t, nombre_pr="", slug_pr=""):
    """La última sección (o la que casa con CTA_H2): texto de cierre con los botones de la tabla, antes del pie."""
    if not sec:
        return ""
    ps = intro_parrafos(sec["bl"])
    txt = "".join(f"<p>{inline(x)}</p>" for x in ps)
    otros = render_bloques([b for b in sec["bl"] if b[0] != "p"])
    return f"""<section class="seccion cierre-sec" id="{slug(sec['h2'])}">
 <div class="contenedor cierre">
  <div class="cierre__txt"><h2 class="h2">{esc(plano(sec['h2']))}</h2><div class="prosa">{txt}{otros}</div></div>
  <div class="cierre__acc"><div class="acciones">{botones(p["url"], t, nombre_pr, slug_pr)}</div>{confianza_html()}</div>
 </div>
</section>
"""


# ---------- Catálogo: tarjetas de producto y rejilla filtrable ----------
def tarjeta_producto(pr, con_do=True):
    img = T.producto_img(pr["foto"], pr["alt"], "(max-width: 767px) 44vw, 220px", "prod__img" + (" prod__img--foto" if not pr["foto"].endswith(".png") else "")) if pr.get("foto") else T.pieza_tipografica(pr["nombre"], pr.get("tipo", ""), "prod__tipo")
    do = DEN[pr["do"]][0] if pr.get("do") in DEN else ("Vino turbio" if pr.get("familia") == "turbio" else ("Licores Pousada" if pr.get("familia") == "licor" else "Sin D.O."))
    meta = " · ".join(x for x in [pr.get("tipo", ""), pr.get("graduacion", "")] if x)
    fam = pr.get("familia", "vino")
    tipo_filtro = "tinto" if "tinto" in (pr.get("tipo", "") + pr.get("uva", "")).lower() or "crianza" in pr.get("tipo", "").lower() or "mencía" in pr.get("tipo", "").lower() else ("licor" if fam == "licor" else ("turbio" if fam == "turbio" else "blanco"))
    return (f'<li class="prod rv" data-do="{pr.get("do") or ("turbio" if fam == "turbio" else ("licor" if fam == "licor" else "sin-do"))}" data-tipo="{tipo_filtro}">'
            f'<a href="{pr["url"]}"><span class="prod__marco">{img}</span><span class="prod__txt">{f"<span class=prod__do>{esc(do)}</span>" if con_do else ""}'
            f'<strong class="prod__nombre">{esc(pr["nombre"])}</strong><span class="prod__meta">{esc(meta)}</span></span></a></li>')


def rejilla(lista, id_="vinos", clase="", con_do=True):
    return f'<ul class="rejilla {clase}" id="{id_}" data-rejilla>{"".join(tarjeta_producto(pr, con_do) for pr in lista)}</ul>'


def filtros():
    """Botones de filtro del catálogo: por D.O. y por tipo. Sin JS, no se muestran (mejora progresiva)."""
    dos = "".join(f'<button type="button" data-filtro="do" data-valor="{k}" aria-pressed="false">{esc(n)}</button>' for k, (n, _, _, _) in DEN.items())
    dos += f'<button type="button" data-filtro="do" data-valor="sin-do" aria-pressed="false">{esc(texto("catalogo_sin_do"))}</button>'
    dos += f'<button type="button" data-filtro="do" data-valor="turbio" aria-pressed="false">{esc(texto("catalogo_turbio"))}</button>'
    dos += f'<button type="button" data-filtro="do" data-valor="licor" aria-pressed="false">{esc(texto("catalogo_licores"))}</button>'
    tipos = "".join(f'<button type="button" data-filtro="tipo" data-valor="{k}" aria-pressed="false">{n}</button>' for k, n in [("blanco", "Blancos"), ("tinto", "Tintos"), ("turbio", "Turbio"), ("licor", "Licores")])
    return f"""<div class="filtros" data-filtros hidden>
 <div class="filtros__grupo"><span class="filtros__h">{esc(texto("catalogo_filtro_do"))}</span><button type="button" data-filtro="todo" aria-pressed="true">{esc(texto("catalogo_filtro_todo"))}</button>{dos}</div>
 <div class="filtros__grupo"><span class="filtros__h">{esc(texto("catalogo_filtro_tipo"))}</span>{tipos}</div>
 <p class="filtros__cuenta" aria-live="polite" data-cuenta></p>
</div>"""


def catalogo_pagina(p, normales):
    cuerpo = [cab_interior(p, "catalogo")]
    lista = productos_de("catalogo", p)
    for s in normales:
        if s is normales[0]:
            # «Vinos por denominación»: la lista de D.O. del texto → tarjetas; debajo la rejilla filtrable
            cuerpo.append(f"""<section class="seccion cat-sec" id="{slug(s['h2'])}">
 <div class="contenedor">
  <div class="encabezado"><h2 class="h2">{esc(plano(s['h2']))}</h2></div>
  <div class="prosa">{render_bloques(s['bl'])}</div>
 </div>
</section>
<section class="seccion rejilla-sec" aria-labelledby="rejilla-tit">
 <div class="contenedor">
  <div class="encabezado encabezado--fila"><h2 class="h2-lect" id="rejilla-tit">Todas las referencias</h2><p class="rejilla__n">{len(lista)} referencias</p></div>
  {filtros()}
  {rejilla(lista, "vinos")}
 </div>
</section>
""")
        else:
            cuerpo.append(f"""<section class="seccion cat-sec" id="{slug(s['h2'])}">
 <div class="contenedor partido">
  <div class="partido__izq"><h2 class="h2">{esc(plano(s['h2']))}</h2></div>
  <div class="partido__der prosa">{render_bloques(s['bl'])}</div>
 </div>
</section>
""")
    return cuerpo


# ---------- Ficha de producto ----------
def datos_producto(pr):
    filas = [("Denominación", DEN[pr["do"]][0] if pr.get("do") in DEN else ("Sin denominación de origen" if pr.get("familia") == "vino" else ("Zona de Ribadavia" if pr.get("familia") == "turbio" else "Licores Pousada"))),
             ("Tipo", pr.get("tipo", "")), ("Uva", pr.get("uva", "")), ("Graduación", pr.get("graduacion", "")),
             ("Formato", pr.get("formato", "")), ("Servicio", pr.get("temperatura", "")), ("Maridaje", pr.get("maridaje", ""))]
    return '<dl class="datos">' + "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in filas if v) + "</dl>"


def ficha_pagina(p, t, normales, cta):
    pr = datos.producto(p["url"]) or {"nombre": p["h1"], "slug": p["url"].strip("/").split("/")[-1], "familia": "vino"}
    intro, _ = secciones(p["bloques"])
    ps = intro_parrafos(intro)
    img = T.producto_img(pr["foto"], pr["alt"], "(max-width: 900px) 70vw, 420px", "ficha__img" + (" ficha__img--foto" if not pr["foto"].endswith(".png") else ""), prioridad=True) if pr.get("foto") else T.pieza_tipografica(pr["nombre"], pr.get("formato", ""), "ficha__tipo")
    do_nombre = DEN[pr["do"]][0] if pr.get("do") in DEN else None
    etiqueta = f"D.O. {do_nombre}" if do_nombre else ("Vino turbio gallego" if pr.get("familia") == "turbio" else ("Licores Pousada · garrafa de 3 litros" if pr.get("familia") == "licor" else "Vino sin denominación de origen"))
    enlace_do = f'<a class="enlace-flecha" href="{URLS["denominacion"]}{pr["do"]}/">Todos los vinos de {esc(do_nombre)} {T.ico("flecha-derecha")}</a>' if do_nombre else (f'<a class="enlace-flecha" href="{URLS["turbio"]}">Todo sobre el vino turbio {T.ico("flecha-derecha")}</a>' if pr.get("familia") == "turbio" else (f'<a class="enlace-flecha" href="{URLS["licores"]}">Todos los licores {T.ico("flecha-derecha")}</a>' if pr.get("familia") == "licor" else f'<a class="enlace-flecha" href="{URLS["catalogo"]}">Todo el catálogo {T.ico("flecha-derecha")}</a>'))
    provisional = ' <span class="prov" title="Foto provisional, recortada del catálogo">foto provisional</span>' if pr.get("provisional") else ""
    cab = f"""<section class="ficha">
 <div class="contenedor">
  {migas_html(p['url'])}
  <div class="ficha__grid">
   <figure class="ficha__foto" data-zoom>{img}</figure>
   <div class="ficha__txt">
    <p class="antetitulo">{esc(etiqueta)}</p>
    <h1 class="h1 h1--ficha" data-palabras>{esc(p['h1'])}</h1>
    {f'<p class="entradilla">{inline(ps[0])}</p>' if ps else ""}
    <div class="acciones" data-acciones>{botones(p["url"], t, pr["nombre"], pr["slug"])}</div>
    {confianza_html()}
    <p class="antetitulo ficha__datos-h">{esc(texto("ficha_datos"))}{provisional}</p>
    {datos_producto(pr)}
    {enlace_do}
   </div>
  </div>
 </div>
</section>
"""
    # Características, maridaje… en columna de lectura; el resto de la entradilla, delante
    if len(ps) > 1 and normales:
        normales[0]["bl"] = [("p", x) for x in ps[1:]] + normales[0]["bl"]
    lect = lectura(p, normales, extra_ind=[("#relacionados", texto("ficha_tambien"))])
    # También le puede interesar: 3 de la misma D.O. (o de la misma familia), nunca el propio
    if pr.get("do"):
        rel = [x for x in CAT if x.get("do") == pr["do"] and x["url"] != pr["url"] and x["url"] in POR_URL]
    else:
        rel = [x for x in CAT if x.get("familia") == pr.get("familia") and x["url"] != pr["url"] and x["url"] in POR_URL]
    if len(rel) < 3:
        rel += [x for x in CAT if x not in rel and x["url"] != pr["url"] and x["url"] in POR_URL and x.get("familia") == pr.get("familia", "vino")]
    rel = rel[:3]
    relacionados = f"""<section class="seccion relacionados-sec" id="relacionados">
 <div class="contenedor">
  <div class="encabezado encabezado--fila"><h2 class="h2-lect">{esc(texto("ficha_tambien"))}</h2><a class="enlace-flecha" href="{URLS["catalogo"]}">{esc(texto("do_ver_todos"))} {T.ico("flecha-derecha")}</a></div>
  {rejilla(rel, "relacionados-lista", "rejilla--3")}
 </div>
</section>
""" if rel else ""
    return [cab, lect, faq_html(p["faq"]), relacionados, cierre(cta, p, t, pr["nombre"], pr["slug"])], pr


# ---------- Hubs: denominación, turbio, licores ----------
def hub_pagina(p, t, normales, cta):
    cuerpo = []
    lista = productos_de(t, p)
    if t == "denominacion":
        k = p.get("denominacion")
        nom, uva, _, tinte = DEN.get(k, (nombre(p["url"]), "", "", None))
        cuerpo.append(cab_interior(p, t, getattr(CFG, "DENOMINACION_ETIQUETA", "D.O. {nombre}").format(nombre=nom) + (f" · {uva}" if uva else ""), tinte, nom, k))
        titulo_rej = texto("do_vinos_titulo", nombre=nom)
    elif t == "turbio":
        cuerpo.append(cab_interior(p, t))
        cuerpo.append(grifo(p["url"]))
        titulo_rej = "El turbio, en barril y en botella"
    else:
        cuerpo.append(cab_interior(p, t))
        titulo_rej = texto("licores_lista_titulo")
    # la sección del texto que lista las referencias (enlaces a fichas) se sustituye por la rejilla; su texto se conserva
    resto, rej_sec = [], None
    for s in normales:
        enlaces = sum(1 for tt, c in s["bl"] if tt == "ul" and any(URLS["ficha"] in x or URLS["licores"] in x for x in c))
        if enlaces and rej_sec is None and lista:
            rej_sec = s
        else:
            resto.append(s)
    rej_html = ""
    if lista:
        extra = ""
        if rej_sec:
            otros = [b for b in rej_sec["bl"] if not (b[0] == "ul" and any(URLS["ficha"] in x or URLS["licores"] in x for x in b[1]))]
            extra = f'<div class="prosa rejilla__extra">{render_bloques(otros)}</div>' if otros else ""
        rej_html = f"""<section class="seccion rejilla-sec" id="vinos">
 <div class="contenedor">
  <div class="encabezado encabezado--fila"><h2 class="h2">{esc(plano(rej_sec["h2"])) if rej_sec else esc(titulo_rej)}</h2><p class="rejilla__n">{len(lista)} referencia{"s" if len(lista) != 1 else ""}</p></div>
  {rejilla(lista, "vinos-lista", "rejilla--3" if len(lista) <= 3 or len(lista) % 3 == 0 and len(lista) % 4 != 0 else "", con_do=False)}
  {extra}
 </div>
</section>
"""
    # orden: en D.O. y licores, lectura (qué es, uvas…) antes de la rejilla; en turbio, lectura tras la banda
    lect = lectura(p, resto, extra_ind=[("#vinos", plano(rej_sec["h2"]) if rej_sec else titulo_rej)] if lista else ())
    if t == "denominacion":
        cuerpo += [lect, rej_html]
    else:
        cuerpo += [rej_html, lect] if t == "licores" else [lect, rej_html]
    k = p.get("denominacion", "")
    nom = DEN[k][0] if k in DEN else ""
    cuerpo += [faq_html(p["faq"]), cierre(cta, p, t, nom, k)]
    return cuerpo


# ---------- Página ----------
def es_widget(s):
    return any(tt == "p" and ES_WIDGET(c) for tt, c in s["bl"])


def pagina(p):
    t = datos.tipo_de(p["url"])
    intro, secs = secciones(p["bloques"])
    pb = pueblo_de(p["url"]) if t == "municipio" else None
    T.CTX["pueblo"] = pb
    cuerpo, cta = [], None
    normales = []
    for k, s in enumerate(secs):
        if ES_CTA.match(plano(s["h2"])) or (CTA_ULTIMO and k == len(secs) - 1 and not es_widget(s) and len(secs) > 1):
            if cta is None:
                cta = s
            else:
                normales.append(s)
        elif es_widget(s):
            continue
        elif t == "contacto" and plano(s["h2"]) in CONTACTO_YA:
            continue
        else:
            normales.append(s)
    nombre_pr = slug_pr = ""
    if t == "home":
        cuerpo.append(portada_foto(p, intro))
        cuerpo.append(estanteria())
        for s in normales:
            if empieza(s, "PROVEEDOR_H2"):
                cuerpo.append(bloque_partido(s, texto("declara_etiqueta"), ("Pedir la tarifa", URLS["contacto"])))
            elif empieza(s, "PASOS_H2"):
                cuerpo.append(bloque_filete(s, "Sin tienda, sin mínimos"))
            elif empieza(s, "CATALOGO_H2"):
                cuerpo.append(cajas_catalogo(s))
                cuerpo.append(grifo("/"))
            elif empieza(s, "CASA_H2"):
                cuerpo.append(casa(s))
            elif ZONA_H2 and plano(s["h2"]).startswith(ZONA_H2):
                cuerpo.append(reparto(s))
            else:
                cuerpo.append(bloque_partido(s))
        cuerpo.append(faq_html(p["faq"]))
        cuerpo.append(tarifa(cta, p))
    elif t == "contacto":
        cuerpo.append(cab_interior(p, t, con_botones=False))
        cuerpo.append(tarifa(None, p, interes="__url__"))
        if normales:
            cuerpo.append(lectura(p, normales))
        cuerpo.append(faq_html(p["faq"]))
    elif t == "catalogo":
        cuerpo += catalogo_pagina(p, normales)
        cuerpo.append(faq_html(p["faq"]))
        cuerpo.append(cierre(cta, p, t))
    elif t in ("ficha", "licor"):
        piezas, pr = ficha_pagina(p, t, normales, cta)
        cuerpo += piezas
        nombre_pr, slug_pr = pr["nombre"], pr["slug"]
    elif t in ("denominacion", "turbio", "licores"):
        cuerpo += hub_pagina(p, t, normales, cta)
        if t == "denominacion":
            k = p.get("denominacion", "")
            nombre_pr, slug_pr = (DEN[k][0] if k in DEN else ""), k
    else:
        cuerpo.append(cab_interior(p, t))
        cuerpo.append(lectura(p, normales, filete=(t == "servicio")))
        cuerpo.append(faq_html(p["faq"]))
        cuerpo.append(cierre(cta, p, t))
    robots = "noindex, follow" if (t == "contacto" and not CONTACTO_INDEXABLE) else "index, follow"
    pre = None
    PO = getattr(CFG, "PORTADA", {})
    if t == "home" and PO.get("foto"):
        b = PO["foto"].rsplit(".", 1)[0]
        ws = T.anchos_foto(PO["foto"])
        pre = (", ".join(f"/img/{b}-{x}.webp {x}w" for x in ws), "(max-width: 1024px) 100vw, 54vw")
    # Si la última pieza es el formulario de tarifa (inicio, contacto), el pie no repite la frase de la tabla de llamadas
    compacto = bool(cuerpo) and 'class="seccion tarifa-sec"' in cuerpo[-1]
    return montar(T.cabeza(p, schema_de(p), robots, precarga=pre) + T.cabecera(p["url"]) + "".join(cuerpo) + T.pie(p["url"], t, nombre_pr, slug_pr, compacto=compacto))


def montar(h):
    """El sprite de la página (solo los iconos que usa) se inserta al abrir <body>."""
    return h.replace("<!--SPRITE-->", T.sprite(h), 1)


# ---------- Legales y 404 ----------
def legales():
    txt = open(os.path.join(RAIZ, "contenido", "legales", "legales.md"), encoding="utf-8").read()
    res = []
    for m in re.finditer(r"^## (/[^\n]+/)\n(.*?)(?=^## /|\Z)", txt, re.S | re.M):
        url, cuerpo = m.group(1).strip(), m.group(2).strip()
        lineas = cuerpo.split("\n")
        res.append((url, lineas[0].strip(), "\n".join(lineas[1:]).strip().replace("\n---", "")))
    return res


def pagina_legal(url, titulo, md):
    """Legales en markdown (## apartados, ### subapartados, listas, tablas): se pintan con el mismo render que las páginas."""
    T.CTX["pueblo"] = None
    p = {"url": url, "title": f"{titulo} | {N['nombre']}", "meta": f"{titulo} de {DOMINIO.split('//')[1]}: titular, condiciones y datos de contacto de {N['nombre']}, distribuidor de vinos para hostelería en Madrid.", "h1": titulo}
    NOMBRE_CORTO[url] = titulo
    bl = datos.bloques(md)
    partes = []
    for t, c in bl:
        if t == "h2":
            partes.append(f'<h2 class="h2-lect">{inline(c)}</h2>')
        else:
            partes.append(render_bloques([(t, c)]))
    schema = {"@context": "https://schema.org", "@graph": [negocio_schema(), {"@type": "WebPage", "url": DOMINIO + url, "name": titulo,
                                                                          "dateModified": fecha_mod(os.path.join(RAIZ, "contenido", "legales", "legales.md"))}]}
    return montar(T.cabeza(p, schema, "noindex, follow") + T.cabecera(url) + f"""<section class="cab-int cab-int--legal"><div class="contenedor">{migas_html(url)}<h1 class="h1 h1--int">{esc(titulo)}</h1></div></section>
<section class="seccion"><div class="contenedor"><div class="prosa legal">{"".join(partes)}</div></div></section>""" + T.pie(url, "legal"))


def pagina_404():
    T.CTX["pueblo"] = None
    p = {"url": "/404/", "title": f"Página no encontrada | {N['nombre']}", "meta": "Esta página no existe.", "h1": "Esta página no existe"}
    schema = {"@context": "https://schema.org", "@graph": [negocio_schema()]}
    return montar(T.cabeza(p, schema, "noindex, follow") + T.cabecera("") + f"""<section class="cab-int"><div class="contenedor"><p class="antetitulo">Error 404</p><h1 class="h1 h1--int">Esta página no existe</h1>
<p class="entradilla">{texto("error_texto")}</p>
<div class="acciones">{T.btn_llamar()}{T.boton("Ir al inicio", "/", "btn--linea")}{T.boton("Ver el catálogo", URLS.get("catalogo", "/"), "btn--linea")}</div></div></section>""" + T.pie("/404/", "error"))


def fecha_mod(ruta):
    import datetime, subprocess
    hoy = datetime.date.today().isoformat()
    try:
        r = subprocess.run(["git", "status", "--porcelain", "--", ruta], cwd=RAIZ, capture_output=True, text=True, timeout=20)
        if r.returncode == 0:
            if r.stdout.strip():
                return hoy
            f = subprocess.run(["git", "log", "-1", "--format=%cs", "--", ruta], cwd=RAIZ, capture_output=True, text=True, timeout=20).stdout.strip()
            if f:
                return f
    except Exception:
        pass
    try:
        return datetime.date.fromtimestamp(os.path.getmtime(ruta)).isoformat()
    except OSError:
        return hoy


def escribir(url, contenido):
    ruta = os.path.join(SITIO, url.strip("/"), "index.html") if url != "/" else os.path.join(SITIO, "index.html")
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    open(ruta, "w", encoding="utf-8").write(contenido)


def main():
    if os.path.isdir(SITIO):
        shutil.rmtree(SITIO)
    os.makedirs(SITIO)
    urls = []
    for p in PAGINAS:
        p["mod"] = fecha_mod(p["ruta"])
        escribir(p["url"], pagina(p))
        if CONTACTO_INDEXABLE or datos.tipo_de(p["url"]) != "contacto":
            urls.append((p["url"], p["mod"]))
    for url, tit, md in legales():
        escribir(url, pagina_legal(url, tit, md))
    open(os.path.join(SITIO, "404.html"), "w", encoding="utf-8").write(pagina_404())
    sm = "".join(f"<url><loc>{DOMINIO}{u}</loc><lastmod>{f}</lastmod></url>" for u, f in urls)
    open(os.path.join(SITIO, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    open(os.path.join(SITIO, "robots.txt"), "w", encoding="utf-8").write(
        f"User-agent: *\nAllow: /\nDisallow: /enviar.php\n\nSitemap: {DOMINIO}/sitemap.xml\n")
    datos_neg = [f"- Nombre: {N['nombre']} ({N['razon_social']}).",
                 f"- Dirección: {N['calle']}, {N['cp']} {N['localidad']} ({N['provincia']}).",
                 f"- Teléfono: {N['telefono']} (también WhatsApp) · Correo: {N['email']}" + (f" · Ficha de Google: {FICHA}" if FICHA.startswith("http") else ""),
                 f"- Horario: {N['horario_texto']}. {texto('llms_horario_extra')}".rstrip(),
                 *TEXTOS["llms_datos"]]
    if N.get("pago"):
        datos_neg.append(f"- Pago: {N['pago']}.")
    resumen = f"> {texto('llms_resumen')} {N['horario_texto']}. Teléfono {N['telefono']}."
    if int(N["resenas"]) > 0:
        resumen += f" {N['valoracion']} en Google con {N['resenas']} reseñas."
    llms = [texto("llms_titulo"), "", resumen, "", "## Datos del negocio", *datos_neg]
    no_hace = [x for x in TEXTOS.get("llms_no_hace", []) if x]
    if no_hace:
        llms += ["", f"## Lo que {N['nombre']} no hace", *no_hace]
    llms += ["", "## Páginas principales"]
    llms += [f"- [{nombre(u)}]({DOMINIO}{u}): {POR_URL[u]['meta']}" for u in LLMS_PRINCIPALES if u in POR_URL]
    dos = [f"{URLS.get('denominacion', '/denominaciones/')}{k}/" for k in DEN]
    if any(u in POR_URL for u in dos):
        llms += ["", "## Denominaciones"] + [f"- [{nombre(u)}]({DOMINIO}{u}): {POR_URL[u]['meta']}" for u in dos if u in POR_URL]
    if CAT:
        llms += ["", "## Catálogo (sin precios: se piden por tarifa)"] + [f"- [{pr['nombre']}]({DOMINIO}{pr['url']}): {POR_URL[pr['url']]['meta']}" for pr in CAT if pr["url"] in POR_URL]
    if PUEBLO:
        llms += ["", "## Zonas"] + [f"- [{v}]({DOMINIO}{k})" for k, v in PUEBLO.items() if k in POR_URL]
    open(os.path.join(SITIO, "llms.txt"), "w", encoding="utf-8").write("\n".join(llms) + "\n")
    print(f"build: {len(PAGINAS)} páginas + {len(legales())} legales + 404 · sitemap con {len(urls)} URLs")


if __name__ == "__main__":
    main()
