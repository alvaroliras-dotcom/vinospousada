# -*- coding: utf-8 -*-
"""GYF-Rayo + 010-Jesper · Plantilla común: <head>, cabecera (barra horizontal en ordenador + capa a pantalla
completa en móvil, o solo capa como en Rayo), pie (oscuro con frase por página, o tres tarjetas de Rayo) y piezas
reutilizables (botón que rueda letra a letra, cintas, iconos del sprite, fotos, imágenes de producto con alfa).
Un cambio aquí llega a todas las páginas (paso 48)."""
import html, json, os, re
from config import (VERSION, DOMINIO, GTM_ID, NEGOCIO as N, MENU, LEGALES, CREDITO, MARCA, URLS, COLOR_TEMA,
                    FICHA, FUENTES_PRECARGA, SERVICIOS_HOME, MUNICIPIOS, texto)
import config as CFG

A = lambda s: html.escape(str(s), quote=True)
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------- Sprite: iconos (recursos/iconos/sprite.svg, estilo C) + el símbolo de la marca ----------
_SP = open(os.path.join(RAIZ, "recursos", "iconos", "sprite.svg"), encoding="utf-8").read()
SIMBOLOS = {m.group(1): m.group(0) for m in re.finditer(r'<symbol id="i-([a-z0-9-]+)".*?</symbol>', _SP, re.S)}

_SVG = open(os.path.join(RAIZ, "recursos", "marca", MARCA["simbolo"]), encoding="utf-8").read()
_SVG = re.sub(r"<metadata>.*?</metadata>", "", _SVG, flags=re.S)
_CUERPO = re.search(r"<svg[^>]*>(.*)</svg>", _SVG, re.S).group(1)
VB = re.search(r'viewBox="([^"]+)"', _SVG).group(1)
# El <svg> que usa el símbolo va en 0 0 ancho alto: el <symbol> ya trae su viewBox (con origen donde sea)
VB0 = "0 0 {} {}".format(*VB.split()[2:4])
# Un solo color: símbolos rellenos (fill) y símbolos de trazo (stroke, como el racimo de Pousada)
_MONO = re.sub(r'fill="#[0-9A-Fa-f]{3,6}"', 'fill="currentColor"', _CUERPO)
_MONO = re.sub(r'stroke="#[0-9A-Fa-f]{3,6}"', 'stroke="currentColor"', _MONO)
if "fill=" not in _MONO and "stroke=" not in _MONO:
    _MONO = f'<g fill="currentColor">{_MONO}</g>'
SIMBOLO_TRAZO = 'stroke="' in _CUERPO     # el símbolo es de trazo: se puede «trazar» con stroke-dashoffset (J3)


def sprite(html_pagina):
    """Solo los símbolos que usa la página (se inserta al abrir <body>)."""
    usados = sorted(set(re.findall(r'href="#i-([a-z0-9-]+)"', html_pagina)))
    faltan = [u for u in usados if u not in SIMBOLOS]
    if faltan:
        raise SystemExit(f"plantilla: iconos que no están en recursos/iconos/sprite.svg: {faltan}")
    cuerpo = "".join(SIMBOLOS[u] for u in usados)
    return (f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">'
            f'<symbol id="simbolo-c" viewBox="{VB}">{_CUERPO}</symbol><symbol id="simbolo-m" viewBox="{VB}">{_MONO}</symbol>{cuerpo}</svg>')


def ico(nombre, clase=""):
    """Icono del sprite (trazo en currentColor + un acento .a/.al que pinta var(--ico-acento))."""
    return f'<svg class="ico {clase}" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><use href="#i-{nombre}"/></svg>'


def simbolo(clase="", color=False):
    """El símbolo de la marca. color=False lo pinta de un solo color (currentColor): viñetas y separadores."""
    return f'<svg class="simbolo {clase}" viewBox="{VB0}" aria-hidden="true" focusable="false"><use href="#simbolo-{"c" if color else "m"}"/></svg>'


def simbolo_trazado(clase=""):
    """El símbolo con sus trazados en línea (no por <use>) para que el JS pueda trazarlo (stroke-dashoffset, J3).
    Si el símbolo no es de trazo, devuelve el símbolo normal."""
    if not SIMBOLO_TRAZO:
        return simbolo(clase)
    return f'<svg class="simbolo {clase}" viewBox="{VB}" aria-hidden="true" focusable="false" data-traza>{_MONO}</svg>'


# ---------- Botón: el texto rueda letra a letra (R13) ----------
def _letras(t):
    return "".join(f'<span style="--i:{k}">{"&nbsp;" if c == " " else html.escape(c)}</span>' for k, c in enumerate(t))


def txt_boton(t):
    return (f'<span class="sr">{html.escape(t)}</span><span class="btn__txt" aria-hidden="true">'
            f'<span class="btn__a">{_letras(t)}</span><span class="btn__b">{_letras(t)}</span></span>')


def boton(t, href, clase="", icono="flecha-diagonal", extra=""):
    ic = f'<span class="btn__ico">{ico(icono)}{ico(icono)}</span>' if icono else ""
    pre = ""
    if icono in ("contacto", "whatsapp-generico"):   # el icono de llamar/WhatsApp va delante y quieto
        pre, ic = ico(icono, "btn__pre"), ""
    return f'<a class="btn {clase}" href="{A(href)}"{extra}>{pre}{txt_boton(t)}{ic}</a>'


def boton_form(t, clase="btn--acento"):
    return f'<button class="btn {clase}" type="submit">{txt_boton(t)}<span class="btn__ico">{ico("flecha-diagonal")}{ico("flecha-diagonal")}</span></button>'


def btn_llamar(clase="btn--acento", t=None, extra=""):
    return boton(t or f"Llamar al {N['telefono']}", f"tel:{N['telefono_e164']}", clase + " tel", "contacto", extra)


CTX = {"pueblo": None}   # en las landings de municipio, todos los WhatsApp llevan el pueblo


def wa_url(pueblo=None):
    from urllib.parse import quote
    pueblo = pueblo or CTX["pueblo"]
    t = texto("whatsapp_saludo") + (texto("whatsapp_pueblo", pueblo=pueblo) if pueblo else "") + ": "
    return f"https://wa.me/{N['whatsapp']}?text={quote(t)}"


def btn_whatsapp(clase="btn--linea", pueblo=None, t="WhatsApp"):
    return boton(t, wa_url(pueblo), clase, "whatsapp-generico", ' rel="noopener" target="_blank"')


def btn_tarifa(clase="btn--acento", t=None, href=None, extra=""):
    """Botón principal de Pousada: solicitar tarifa (→ contacto)."""
    mb = getattr(CFG, "MENU_BOTON", ("Solicitar tarifa", URLS["contacto"]))
    return boton(t or mb[0], href or mb[1], clase, "flecha-diagonal", extra)


# ---------- Imágenes ----------
def medida(archivo, carpetas=("fotos", "casos", "producto")):
    from PIL import Image
    for d in carpetas:
        r = os.path.join(RAIZ, "recursos", d, archivo)
        if os.path.exists(r):
            with Image.open(r) as im:
                return im.width, im.height
    return 1600, 1067


def anchos_foto(archivo):
    """Anchos que genera rematar.py para una foto: 800 siempre; 1600 solo si el original llega (no se amplía)."""
    w, _ = medida(archivo, ("fotos", "casos"))
    return [800] + ([1600] if w >= 1200 else [])


def foto(archivo, alt, sizes="(max-width: 900px) 100vw, 50vw", prioridad=False, clase=""):
    """Foto de recursos/fotos o recursos/casos (las genera rematar.py en JPG y WebP, 800 y, si llega, 1600)."""
    base = archivo.rsplit(".", 1)[0]
    w, h = medida(archivo, ("fotos", "casos"))
    ws = anchos_foto(archivo)
    mayor = ws[-1]
    alto = round(mayor * h / w)
    carga = 'fetchpriority="high"' if prioridad else 'loading="lazy" decoding="async"'
    ss = lambda ext: ", ".join(f"/img/{base}-{x}.{ext} {x}w" for x in ws)
    return (f'<picture class="{clase}"><source type="image/webp" srcset="{ss("webp")}" sizes="{sizes}">'
            f'<img src="/img/{base}-{mayor}.jpg" srcset="{ss("jpg")}" sizes="{sizes}" '
            f'width="{mayor}" height="{alto}" alt="{A(alt)}" {carga}></picture>')


def tamanos_producto(w, h):
    """Variantes de una imagen de producto: lado mayor a 420 y 840 (sin ampliar más de un 15 %). Devuelve [(nombre, ancho, alto)]."""
    lado = max(w, h)
    res = []
    for objetivo in (420, 840):
        f = min(objetivo / lado, 1.15)
        res.append((objetivo, round(w * f), round(h * f)))
    return res


def producto_img(archivo, alt, sizes="(max-width: 900px) 40vw, 300px", clase="", prioridad=False):
    """Imagen de producto (recursos/producto/): botellas con alfa (PNG → WebP con alfa + PNG) o recortes (JPG → WebP + JPG),
    con el lado mayor a 420 y 840. Las genera rematar.py con tamanos_producto()."""
    base, ext = archivo.rsplit(".", 1)
    w, h = medida(archivo, ("producto",))
    tam = tamanos_producto(w, h)
    resp = "png" if ext.lower() == "png" else "jpg"
    carga = 'fetchpriority="high"' if prioridad else 'loading="lazy" decoding="async"'
    ss = lambda e: ", ".join(f"/img/{base}-{n}.{e} {aw}w" for n, aw, ah in tam)
    n, aw, ah = tam[-1]
    return (f'<picture class="{clase}"><source type="image/webp" srcset="{ss("webp")}" sizes="{sizes}">'
            f'<img src="/img/{base}-{n}.{resp}" srcset="{ss(resp)}" sizes="{sizes}" '
            f'width="{aw}" height="{ah}" alt="{A(alt)}" {carga}></picture>')


def pieza_tipografica(titulo, sub="", clase=""):
    """Sin foto: pieza tipográfica con el símbolo, nunca un hueco vacío ni una foto borrosa."""
    return (f'<div class="tipo {clase}" aria-hidden="true">{simbolo("tipo__sim")}<span class="tipo__tit">{A(titulo)}</span>'
            f'{f"<span class=tipo__sub>{A(sub)}</span>" if sub else ""}</div>')


# ---------- <head> ----------
def cabeza(p, schema, robots="index, follow", precarga=None):
    """precarga: (srcset, sizes) de la imagen LCP (el objeto de portada o la foto de portada en la home)."""
    url = DOMINIO + p["url"]
    pre = ""
    if precarga:
        pre = f'<link rel="preload" as="image" type="image/webp" imagesrcset="{precarga[0]}" imagesizes="{precarga[1]}" fetchpriority="high">'
    fuentes = "".join(f'<link rel="preload" href="/fuentes/{f}" as="font" type="font/woff2" crossorigin>' for f in FUENTES_PRECARGA)
    return f"""<!doctype html>
<html lang="es" data-gtm="{GTM_ID}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{A(p['title'])}</title>
<meta name="description" content="{A(p['meta'])}">
<meta name="robots" content="{robots}">
{"" if p["url"] == "/404/" else f'<link rel="canonical" href="{url}">'}
<meta name="theme-color" content="{COLOR_TEMA}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="{A(N['nombre'])}">
<meta property="og:title" content="{A(p['title'])}">
<meta property="og:description" content="{A(p['meta'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMINIO}/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
{fuentes}
{pre}
<link rel="stylesheet" href="/css/estilo.css?v={VERSION}">
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False, separators=(",", ":"))}</script>
</head>
"""


# ---------- Cabecera ----------
def _menu(actual):
    grandes, cols = [], []
    for k, (nombre, dest) in enumerate(MENU):
        if isinstance(dest, list):
            if not dest:
                continue
            li = "".join(f'<li><a href="{u}"{" aria-current=page" if u == actual else ""}>{n}</a></li>' for n, u in dest)
            cols.append(f'<div class="menu__col"><p class="menu__h">{nombre}</p><ul>{li}</ul></div>')
        else:
            cur = ' aria-current="page"' if dest == actual else ""
            grandes.append(f'<li style="--i:{len(grandes)}"><a href="{dest}"{cur}><span>{nombre}</span></a></li>')
    return "".join(grandes), "".join(cols)


def logo_html(claro=False):
    """El logo de la cabecera: SVG apaisado (MARCA["logo"]) o, si es None, símbolo + nombre compuesto en HTML (FIRMA §1.4)."""
    if MARCA.get("logo"):
        f = (MARCA.get("logo_blanco") or MARCA["logo"]) if claro else MARCA["logo"]
        return f'<img src="/marca/{f}" alt="{A(texto("logo_alt"))}" width="{MARCA["logo_ancho"]}" height="{MARCA["logo_alto"]}">'
    ante, nombre = MARCA.get("logo_texto") or ("", N["nombre"])
    return (f'<span class="marca">{simbolo("marca__sim", color=not claro)}<span class="marca__txt">'
            f'{f"<span class=marca__ante>{A(ante)}</span>" if ante else ""}<span class="marca__nombre">{A(nombre)}</span></span></span>')


def cabecera(actual):
    grandes, cols = _menu(actual)
    barra = getattr(CFG, "CAB_ESTILO", "capa") == "barra"
    nav = ""
    if barra:
        li = "".join(f'<li><a href="{u}"{" aria-current=page" if u == actual else ""}>{A(n)}</a></li>' for n, u in MENU if not isinstance(u, list))
        nav = f'<nav class="cab__nav" aria-label="Principal"><ul>{li}</ul></nav>'
    mb = getattr(CFG, "MENU_BOTON", None)
    boton_cab = btn_tarifa("btn--acento btn--cab btn--peq", mb[0], mb[1], ' data-zona="cabecera"') if (barra and mb) else btn_llamar("btn--acento btn--cab", N['telefono'], ' data-zona="cabecera"')
    tel_cab = (f'<a class="cab__tel tel" href="tel:{N["telefono_e164"]}" data-zona="cabecera">{ico("contacto")}<span>{N["telefono"]}</span></a>' if barra else
               f'<a class="cab__circulo tel" href="tel:{N["telefono_e164"]}" aria-label="Llamar al {N["telefono"]}" data-zona="cabecera">{ico("contacto")}</a>')
    return f"""<body>
<!--SPRITE-->
<a class="saltar" href="#contenido">Saltar al contenido</a>
<header class="cab{' cab--barra' if barra else ''}" data-cab>
 <div class="contenedor cab__in">
  <a class="cab__logo" href="/" aria-label="{A(N['nombre'])}: inicio">{logo_html()}</a>
  {nav}
  <div class="cab__der">
   {tel_cab}
   {boton_cab}
   <button class="cab__burger" type="button" aria-label="Abrir menú" aria-expanded="false" aria-controls="menu"><span></span><span></span></button>
  </div>
 </div>
</header>
<div class="menu" id="menu" aria-hidden="true" role="dialog" aria-label="Menú" data-menu>
 <div class="contenedor menu__in">
  <div class="menu__top"><a class="menu__logo" href="/" aria-label="{A(N['nombre'])}: inicio">{logo_html(claro=True)}</a><button class="menu__cerrar" type="button" aria-label="Cerrar menú">{ico("cerrar")}</button></div>
  <nav class="menu__nav" aria-label="Menú"><ul class="menu__grandes">{grandes}</ul><div class="menu__cols">{cols}</div></nav>
  <div class="menu__contacto">
   <p class="estado" data-estado><i></i><span>{N['horario_corto']}</span></p>
   <a class="menu__tel tel" href="tel:{N['telefono_e164']}">{N['telefono']}</a>
   <a class="menu__mail" href="mailto:{N['email']}">{N['email']}</a>
   <div class="acciones">{btn_whatsapp("btn--linea-claro")}</div>
  </div>
 </div>
</div>
<main id="contenido">
"""


# ---------- Cintas (R14): pista con dos grupos iguales para que el bucle no tenga costura ----------
def cinta(palabras, clase="", sentido=-1):
    sep = simbolo("cinta__sep")
    grupo = "".join(f"<span>{A(x)}</span>{sep}" for x in list(palabras) * 2)
    return (f'<div class="cinta {clase}" aria-hidden="true"><div class="cinta__pista" data-cinta="{sentido}">'
            f'<div class="cinta__grupo">{grupo}</div><div class="cinta__grupo">{grupo}</div></div></div>')


# ---------- Estado abierto / cerrado y nota de Google (piezas de la base GYF) ----------
def estado(clase=""):
    return f'<p class="estado {clase}" data-estado><i></i><span>{N["horario_corto"]}</span></p>'


def nota(clase="", enlace=None):
    cuerpo = (f'<strong data-nota>{N["valoracion"]}</strong><span class="estrellas" aria-hidden="true">★★★★★</span>'
              f'<span><span data-resenas>{N["resenas"]}</span> reseñas en Google</span>')
    if enlace:
        return f'<a class="nota {clase}" href="{A(enlace)}"{" rel=noopener target=_blank" if enlace.startswith("http") else ""}>{cuerpo}</a>'
    return f'<p class="nota {clase}">{cuerpo}</p>'


# ---------- Pie ----------
def _boton_pie(clave, principal, nombre="", slug=""):
    cls = "btn--blanco" if principal else "btn--linea-claro"
    if clave == "tarifa":
        return btn_tarifa(cls, extra=' data-zona="pie"')
    if clave == "llamar":
        return btn_llamar(cls, extra=' data-zona="pie"')
    if clave == "whatsapp":
        return btn_whatsapp(cls, t="Escribir por WhatsApp")
    t, u = clave
    return boton(t.format(nombre=nombre, slug=slug), u.format(nombre=nombre, slug=slug), cls)


def frase_pie(url, tipo="", nombre="", slug=""):
    """(pregunta, titular, botón principal, botón secundario) de PIE_FRASES por URL o PIE_FRASES_TIPO por tipo; None si no hay."""
    return getattr(CFG, "PIE_FRASES", {}).get(url) or getattr(CFG, "PIE_FRASES_TIPO", {}).get(tipo)


def pie(url="", tipo="", nombre="", slug="", compacto=False):
    if getattr(CFG, "PIE_ESTILO", "tarjetas") == "oscuro":
        return pie_oscuro(url, tipo, nombre, slug, compacto)
    return pie_tarjetas()


def pie_oscuro(url, tipo, nombre, slug, compacto=False):
    """Pie oscuro (Jesper 4 columnas + pieza de marca GYF J3): el símbolo grande que se traza al entrar, la frase del pie
    de la tabla de llamadas a la acción (pregunta → titular → botones), columnas y línea legal.
    compacto=True (páginas cuyo cierre es el formulario de tarifa: inicio y contacto): la frase de la tabla ya la lleva
    la sección del formulario (pregunta como antetítulo, titular y botones), así que el pie no la repite pegada debajo
    (detector: «la misma llamada dos veces seguidas»); queda el racimo junto a las columnas."""
    f = frase_pie(url, tipo, nombre, slug) or ("", texto("pie_titular"), "tarifa", "llamar")
    pregunta, titular, b1, b2 = f
    cols = "".join(f'<div class="pie__col"><p class="pie__h">{A(t)}</p><ul>{"".join(f"<li><a href={u}>{A(n)}</a></li>" for n, u in L)}</ul></div>'
                   for t, L in getattr(CFG, "PIE_COLUMNAS", []))
    leg = "".join(f'<li><a href="{u}">{n}</a></li>' for n, u in LEGALES)
    sub = getattr(CFG, "PIE_SUB", "")
    if compacto:
        frase = f"""<div class="pie__frase pie__frase--compacta">
   <div class="pie__racimo">{simbolo_trazado("pie__sim")}</div>
   <div class="pie__txt"><p class="pie__marca">{A(N['nombre'])}</p><p class="pie__sub">{A(N['nombre_largo'].split('·', 1)[-1].strip())} · {A(N['localidad'])} ({A(N['provincia'])})</p></div>
  </div>"""
    else:
        frase = f"""<div class="pie__frase">
   <div class="pie__racimo">{simbolo_trazado("pie__sim")}</div>
   <div class="pie__txt">
    {f'<p class="antetitulo antetitulo--claro">{A(pregunta)}</p>' if pregunta else ""}
    <p class="pie__titular">{A(titular)}</p>
    {f'<p class="pie__sub">{A(sub)}</p>' if sub else ""}
    <div class="acciones">{_boton_pie(b1, True, nombre, slug)}{_boton_pie(b2, False, nombre, slug)}</div>
   </div>
  </div>"""
    return f"""</main>
<footer class="pie pie--oscuro">
 <div class="contenedor">
  {frase}
  <div class="pie__columnas">
   {cols}
   <div class="pie__col"><p class="pie__h">{texto("pie_etiqueta_contacto")}</p><ul>
    <li><a class="tel" href="tel:{N['telefono_e164']}">{N['telefono']}</a> {texto("pie_tambien_whatsapp")}</li>
    <li><a href="mailto:{N['email']}">{N['email']}</a></li>
    <li>{N['localidad']} ({N['provincia']})</li>
    <li>{N['horario_texto']}</li>
    <li>{estado("estado--claro")}</li></ul></div>
   <div class="pie__col"><p class="pie__h">{texto("pie_legal_titulo")}</p><ul>{leg}<li><a href="#" data-cookies-config>Cookies</a></li></ul></div>
  </div>
  <div class="pie__legal">
   <span>© <span data-anio>2026</span> {N['razon_social']} · {N['localidad']} ({N['provincia']})</span>
   <span class="pie__credito">Web de <a href="{CREDITO[1]}" target="_blank" rel="noopener">{CREDITO[0]}</a></span>
  </div>
 </div>
</footer>
""" + _cola()


def pie_tarjetas():
    """Pie de Rayo: tres tarjetas blancas (variación A), sin nombre gigante."""
    serv = [(n, u) for n, u in (MENU[1][1] if len(MENU) > 1 and isinstance(MENU[1][1], list) else [])]
    base = [] if N["localidad"] in [n for _, n in MUNICIPIOS] else [(N["localidad"], "/")]
    zona = base + [(n, u) for u, n in MUNICIPIOS] if URLS.get("municipio") else []
    grandes = [(n, d) for n, d in MENU if not isinstance(d, list)]
    lst = lambda L: "".join(f'<li><a href="{u}">{n}</a></li>' for n, u in L)
    leg = "".join(f'<li><a href="{u}">{n}</a></li>' for n, u in LEGALES)
    return f"""</main>
<footer class="pie">
 <div class="contenedor">
  <div class="pie__tarjetas">
   <div class="pie__t pie__t--menu rv">
    <p class="pie__titular">{texto("pie_titular")}</p>
    <ul class="pie__grandes">{lst(grandes)}</ul>
   </div>
   <div class="pie__t pie__t--contacto rv">
    {estado()}
    <a class="pie__tel tel" href="tel:{N['telefono_e164']}">{N['telefono']}</a>
    <a class="pie__mail" href="mailto:{N['email']}">{N['email']}</a>
    <p class="pie__dir"><a href="{FICHA}" rel="noopener" target="_blank">{N['calle']}, {N['cp']} {N['localidad']} ({N['provincia']})</a><br>{N['horario_texto']}</p>
    <div class="acciones">{btn_whatsapp("btn--linea btn--peq")}</div>
   </div>
   <div class="pie__t pie__t--listas rv">
    <div><p class="pie__h">Servicios</p><ul>{lst(serv)}</ul></div>
    {f'<div><p class="pie__h">Zonas</p><ul>{lst(zona)}</ul></div>' if zona else ""}
   </div>
  </div>
  <div class="pie__legal">
   <span>© <span data-anio>2026</span> {N['razon_social']}</span>
   <ul>{leg}<li><a href="#" data-cookies-config>Configurar cookies</a></li></ul>
   <span class="pie__credito">Diseño y SEO: <a href="{CREDITO[1]}" target="_blank" rel="noopener">{CREDITO[0]}</a></span>
  </div>
 </div>
</footer>
""" + _cola()


def _cola():
    """Lo que va tras el pie en todas las páginas: subir, barra fija del móvil, aviso de cookies y los scripts."""
    tema_js = '<script src="/js/tema.js?v={}" defer></script>'.format(VERSION) if os.path.exists(os.path.join(RAIZ, "cliente", "js", "tema.js")) else ""
    return f"""<a class="subir" href="#contenido" aria-label="Volver arriba" data-subir>{ico("flecha-diagonal")}</a>
<nav class="barra-movil" aria-label="Contacto rápido">{btn_llamar("btn--acento", "Llamar")}{btn_whatsapp("btn--linea")}</nav>
<div class="cookies" id="cookies" role="dialog" aria-label="Aviso de cookies">
 <p>Usamos cookies propias necesarias y, solo si usted lo acepta, cookies de Google Analytics para saber cómo se usa la web. <a href="/politica-de-cookies/">Política de cookies</a>.</p>
 <div class="acciones"><button class="btn btn--oscuro btn--peq" type="button" data-cookies="si">{txt_boton("Aceptar todas")}</button><button class="btn btn--linea btn--peq" type="button" data-cookies="no">{txt_boton("Solo las necesarias")}</button></div>
</div>
<script src="/js/main.js?v={VERSION}" defer></script>
{tema_js}
</body>
</html>
"""
