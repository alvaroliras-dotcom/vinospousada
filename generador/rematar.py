# -*- coding: utf-8 -*-
"""GYF-Rayo · Rematar (paso 52): siempre el ÚLTIMO del build.
Copia recursos, genera imágenes 800/1600 en JPG y WebP, une y minifica el CSS,
y deja los archivos de servidor (.htaccess, enviar.php, favicons, manifest)."""
import os, re, shutil, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (VERSION, NEGOCIO as N, DOMINIO, MARCA, COOKIES_CLAVE, HOST_PRODUCCION, COLOR_TEMA, REDIRECCIONES,
                    REDIRECCIONES_302, URLS, OBJETO_PORTADA, texto)
import config as CFG
import json

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = lambda *p: os.path.join(RAIZ, *p)
S = lambda *p: os.path.join(RAIZ, "sitio", *p)


def css():
    base = open(R("base", "css", "base.css"), encoding="utf-8").read()
    tema = open(R("cliente", "css", "tema.css"), encoding="utf-8").read()
    # el tema va DESPUÉS de la base para que sus variables manden; las @font-face, arriba
    fuentes = "".join(re.findall(r"@font-face\{[^}]+\}", tema))
    tema = re.sub(r"@font-face\{[^}]+\}", "", tema)
    todo = fuentes + base + tema
    todo = re.sub(r"/\*.*?\*/", "", todo, flags=re.S)
    todo = re.sub(r"\s+", " ", todo)
    todo = re.sub(r"\s*([{}:;,>])\s*", r"\1", todo)
    todo = todo.replace(";}", "}")
    # restaurar espacios necesarios en selectores/valores que la regla anterior pudo tocar
    todo = re.sub(r"@media\(", "@media (", todo)
    todo = todo.replace(")and(", ") and (").replace("and(", "and (")
    os.makedirs(S("css"), exist_ok=True)
    open(S("css", "estilo.css"), "w", encoding="utf-8").write(todo)
    return len(todo)


CACHE = R("recursos", ".cache-img")   # las variantes se generan una vez por origen (por fecha) y se copian a sitio/img


def _cache(origen, salidas, generar):
    """Genera las variantes de una imagen solo si el origen es más nuevo que la caché; luego las copia a sitio/img."""
    os.makedirs(CACHE, exist_ok=True)
    m = os.path.getmtime(origen)
    if any(not os.path.exists(os.path.join(CACHE, f)) or os.path.getmtime(os.path.join(CACHE, f)) < m for f in salidas):
        generar(CACHE)
    for f in salidas:
        shutil.copy2(os.path.join(CACHE, f), S("img", f))


def imagenes():
    """Fotos y casos (JPG/PNG/WebP) → 800 y, si el original llega a 1.200 px, 1600, en JPG y WebP (no se amplía: una foto
    de 800 sale solo a 800; plantilla.foto() lo sabe). Producto (recursos/producto/, botellas con alfa o recortes) → 420 y
    840 en WebP (con alfa si lo hay) y PNG o JPG de respaldo. El objeto de portada (si lo hay) → 420 y 840 WebP + 840 PNG.
    Todo pasa por una caché (recursos/.cache-img) para no recomprimir en cada build."""
    os.makedirs(S("img"), exist_ok=True)
    n = 0
    for carpeta in ("fotos", "casos"):
        d = R("recursos", carpeta)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            b = f.rsplit(".", 1)[0]
            with Image.open(os.path.join(d, f)) as im0:
                anchos = [800] + ([1600] if im0.width >= 1200 else [])
            salidas = [f"{b}-{w}.{e}" for w in anchos for e in ("jpg", "webp")]

            def gen(dc, f=f, b=b, anchos=anchos, d=d):
                im = Image.open(os.path.join(d, f)).convert("RGB")
                for w in anchos:
                    v = im if im.width == w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                    v.save(os.path.join(dc, f"{b}-{w}.jpg"), "JPEG", quality=80 if w == 1600 else 78, optimize=True, progressive=True)
                    v.save(os.path.join(dc, f"{b}-{w}.webp"), "WEBP", quality=76, method=5)
            _cache(os.path.join(d, f), salidas, gen)
            n += 1
    d = R("recursos", "producto")
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if not f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            b, ext = f.rsplit(".", 1)
            alfa = ext.lower() == "png"
            resp = "png" if alfa else "jpg"
            salidas = [f"{b}-{w}.{e}" for w in (420, 840) for e in ("webp", resp)]

            def gen(dc, f=f, b=b, alfa=alfa, resp=resp, d=d):
                im = Image.open(os.path.join(d, f)).convert("RGBA" if alfa else "RGB")
                if alfa:
                    bb = im.getbbox()
                    if bb:
                        im = im.crop(bb)
                from plantilla import tamanos_producto
                for n_, aw, ah in tamanos_producto(im.width, im.height):
                    v = im if (im.width, im.height) == (aw, ah) else im.resize((aw, ah), Image.LANCZOS)
                    v.save(os.path.join(dc, f"{b}-{n_}.webp"), "WEBP", quality=82, method=5)
                    if alfa:
                        v.save(os.path.join(dc, f"{b}-{n_}.png"), "PNG", optimize=False, compress_level=6)
                    else:
                        v.save(os.path.join(dc, f"{b}-{n_}.jpg"), "JPEG", quality=82, optimize=True, progressive=True)
            _cache(os.path.join(d, f), salidas, gen)
            n += 1
    if OBJETO_PORTADA.get("imagen"):
        o = R("recursos", "objeto", OBJETO_PORTADA["imagen"])
        if os.path.exists(o):
            im = Image.open(o).convert("RGBA")
            b = OBJETO_PORTADA["imagen"].rsplit(".", 1)[0]
            for w in (420, 840):
                v = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
                v.save(S("img", f"{b}-{w}.webp"), "WEBP", quality=82, method=5)
            im.resize((840, round(im.height * 840 / im.width)), Image.LANCZOS).save(S("img", f"{b}-840.png"), "PNG", optimize=True)
        else:
            sys.exit(f"rematar: falta el objeto de portada recursos/objeto/{OBJETO_PORTADA['imagen']} (herramientas/objeto3d/foto_fija.py lo genera)")
        for k in ("video_webm", "video_mov"):
            if OBJETO_PORTADA.get(k):
                os.makedirs(S("objeto"), exist_ok=True)
                shutil.copy(R("recursos", "objeto", OBJETO_PORTADA[k]), S("objeto", OBJETO_PORTADA[k]))
    return n


def copiar():
    shutil.copytree(R("recursos", "fuentes"), S("fuentes"), dirs_exist_ok=True)
    for f in os.listdir(S("fuentes")):
        m = re.match(r"(.+)-latin-(\d+)-(normal|italic)\.woff2", f)
        if m:
            os.replace(S("fuentes", f), S("fuentes", f"{m.group(1)}-{m.group(2)}{'' if m.group(3) == 'normal' else '-italic'}.woff2"))
    os.makedirs(S("marca"), exist_ok=True)
    for f in os.listdir(R("recursos", "marca")):
        if f.endswith(".svg"):
            shutil.copy(R("recursos", "marca", f), S("marca", f))
    shutil.copy(R("recursos", "marca", MARCA["og"]), S("og-image.jpg"))
    for f in os.listdir(R("recursos", "favicon")):
        shutil.copy(R("recursos", "favicon", f), S(f))
    # el manifest sale de config.py (nombre y color), no se copia a mano
    open(S("site.webmanifest"), "w", encoding="utf-8").write(json.dumps({
        "name": N["nombre"], "short_name": N["nombre"][:12],
        "icons": [{"src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"}],
        "theme_color": COLOR_TEMA, "background_color": COLOR_TEMA, "display": "standalone"}, ensure_ascii=False))
    os.makedirs(S("js"), exist_ok=True)
    js()
    shutil.copytree(R("cliente", "js", "vendor"), S("js", "vendor"), dirs_exist_ok=True)
    if OBJETO_PORTADA.get("tipo") != "3d" and os.path.exists(S("js", "vendor", "objeto3d.min.js")):
        os.remove(S("js", "vendor", "objeto3d.min.js"))   # three.js solo si hay objeto 3D
    if os.path.exists(R("cliente", "js", "tema.js")):
        shutil.copy(R("cliente", "js", "tema.js"), S("js", "tema.js"))
    shutil.copy(R("contenido", "resenas.json"), S("resenas.json"))
    # Vista previa en Vercel (Root Directory = sitio): nunca se indexa. Las mismas redirecciones 301 de un salto que el
    # .htaccess (hoja 301 de la arquitectura), para que la vista previa se pueda probar con las URLs viejas.
    redirs = [{"source": "/" + v.strip("/") + "{/}?", "destination": n, "permanent": True} for v, n in getattr(CFG, "REDIRECCIONES", [])]
    redirs += [{"source": "/" + v.strip("/") + "{/}?", "destination": n, "permanent": False} for v, n in getattr(CFG, "REDIRECCIONES_302", [])]
    open(S("vercel.json"), "w", encoding="utf-8").write(json.dumps({
        "cleanUrls": True, "trailingSlash": True,
        "headers": [{"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]}],
        "redirects": redirs}, indent=1, ensure_ascii=False))


HTACCESS = r"""# __NOMBRE__ · servidor Apache (hosting Plesk del cliente)
Options -Indexes
DirectoryIndex index.html
AddType font/woff2 .woff2
AddType application/manifest+json .webmanifest
AddCharset utf-8 .txt

# Nada de copias, volcados ni registros a la vista
<FilesMatch "\.(zip|sql|bak|old|log|sh|ini|env|git.*|md|py|csv)$">
  Require all denied
</FilesMatch>
ErrorDocument 404 /404.html

<IfModule mod_rewrite.c>
RewriteEngine On
# Sin www (paso 18)
RewriteCond %{HTTP_HOST} ^www\. [NC]
RewriteRule ^ __DOMINIO__%{REQUEST_URI} [L,R=301]
# A https. Solo si ni Apache ni el proxy de Plesk (nginx delante) dicen que ya es https:
# así no entra en bucle detrás de un proxy (lo que tiró la web de Marcos).
RewriteCond %{HTTPS} off
RewriteCond %{HTTP:X-Forwarded-Proto} !https [NC]
RewriteCond %{HTTP:X-Forwarded-SSL} !on [NC]
RewriteRule ^ __DOMINIO__%{REQUEST_URI} [L,R=301]
# Restos del WordPress antiguo: 410 (ya no existen y no vuelven)
RewriteRule ^(wp-admin|wp-content|wp-includes|wp-json)(/.*)?$ - [G,L]
RewriteRule ^(wp-login\.php|xmlrpc\.php|wp-cron\.php|feed/?|comments/feed/?)$ - [G,L]
RewriteRule ^(author|category|tag|page)(/.*)?$ - [G,L]
# Sitemaps viejos de WordPress / Yoast / Rank Math → el nuevo
RewriteRule ^(sitemap_index\.xml|wp-sitemap\.xml|[a-z0-9_-]+-sitemap[0-9]*\.xml)$ /sitemap.xml [L,R=301]
# Redirecciones del cambio (paso 17)
__REDIRECCIONES__
# Temporales (302): URLs reservadas que volverán a servir 200
__REDIRECCIONES_302__
# Barra final en las URLs de carpeta
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_URI} !(\.[a-z0-9]{2,5})$ [NC]
RewriteCond %{REQUEST_URI} !/$
RewriteRule ^(.*)$ /$1/ [L,R=301]
</IfModule>

<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml application/json text/xml application/xml
</IfModule>

<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType text/html "access plus 0 seconds"
ExpiresByType text/css "access plus 1 year"
ExpiresByType application/javascript "access plus 1 year"
ExpiresByType image/jpeg "access plus 1 year"
ExpiresByType image/webp "access plus 1 year"
ExpiresByType image/svg+xml "access plus 1 year"
ExpiresByType font/woff2 "access plus 1 year"
ExpiresByType image/png "access plus 1 year"
ExpiresByType image/x-icon "access plus 1 year"
ExpiresByType image/vnd.microsoft.icon "access plus 1 year"
ExpiresByType application/manifest+json "access plus 1 week"
ExpiresByType application/json "access plus 0 seconds"
ExpiresByType application/xml "access plus 1 hour"
ExpiresByType text/xml "access plus 1 hour"
</IfModule>

<IfModule mod_headers.c>
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set X-Frame-Options "SAMEORIGIN"
</IfModule>
"""

ENVIAR = r"""<?php
/* __NOMBRE__ · formularios de la web: «Que me llamen» (si la web lo lleva) y la solicitud de tarifa (contacto).
   Antispam: trampa + tiempo en la página + sin enlaces en el mensaje. Sin captcha. El mensaje es opcional.
   «t» lo rellena main.js al enviar: milisegundos que lleva la página abierta (performance.now()). Válido entre 3 s y 24 h.
   Buzón de destino: __EMAIL__ (⚑ confirmar en el paso 44). */
header('X-Robots-Tag: noindex');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: __CONTACTO__'); exit; }
$c = function ($k, $max) { return trim(mb_substr(strip_tags($_POST[$k] ?? ''), 0, $max)); };
$tipo = ($_POST['tipo'] ?? '') === 'llamada' ? 'llamada' : 'contacto';
$pagina = $c('pagina', 120);
if (!preg_match('#^/[a-z0-9\-/]*$#', $pagina) || strpos($pagina, '//') !== false) { $pagina = '/'; }
$nombre = $c('nombre', 80); $telefono = $c('telefono', 20); $negocio = $c('negocio', 80); $tipo_negocio = $c('tipo_negocio', 30);
$municipio = $c('municipio', 60); $mensaje = $c('mensaje', 2000);
$trampa = $_POST['web'] ?? ''; $t = (int)($_POST['t'] ?? 0);
$motivo = '';
if ($trampa !== '') { $motivo = 'trampa'; }
elseif ($t < 3000 || $t > 86400000) { $motivo = 'tiempo'; }
elseif ($nombre === '' || !preg_match('/^[0-9 +()\-]{9,20}$/', $telefono)) { $motivo = 'datos'; }
elseif ($tipo === 'contacto' && ($negocio === '' || $tipo_negocio === '')) { $motivo = 'datos'; }
elseif (preg_match_all('#https?://#i', $mensaje) > 0) { $motivo = 'enlaces'; }
$ok = $motivo === '';
if ($tipo === 'llamada') { $vuelta = $pagina; $clave = 'llamada'; $ancla = '#te-llamamos'; $ancla_ko = '#te-llamamos'; }
else { $vuelta = ($pagina !== '/' && $pagina !== '') ? $pagina : '__CONTACTO__'; $clave = 'enviado'; $ancla = '#form-ok'; $ancla_ko = '#form-error'; }
if ($motivo === 'trampa' || $motivo === 'tiempo') { header('Location: ' . $vuelta . '?' . $clave . '=1' . $ancla); exit; } /* a los robots no se les da pista */
if (!$ok) { header('Location: ' . $vuelta . '?' . $clave . '=0&motivo=' . $motivo . $ancla_ko); exit; }
$para = '__EMAIL__';
if ($tipo === 'llamada') {
  $asunto = '=?UTF-8?B?' . base64_encode('QUE ME LLAMEN · ' . $nombre . ' · ' . $telefono) . '?=';
  $cuerpo = "Petición de llamada desde la web.\n\nNombre: $nombre\nTeléfono: $telefono\nPágina: __DOMINIO__$pagina\n";
} else {
  $asunto = '=?UTF-8?B?' . base64_encode('SOLICITUD DE TARIFA · ' . $negocio . ' (' . $tipo_negocio . ') · ' . $nombre) . '?=';
  $cuerpo = "Solicitud de tarifa desde la web.\n\nNombre: $nombre\nNegocio: $negocio\nTipo de negocio: $tipo_negocio\nTeléfono: $telefono\n" . ($municipio ? "Municipio: $municipio\n" : "") . "\nMensaje:\n$mensaje\n\nPágina: __DOMINIO__$pagina\n-- Enviado desde __HOST____CONTACTO__";
}
$cab = "From: Web __NOMBRE__ <web@__HOST_SIN_WWW__>\r\nReply-To: Web __NOMBRE__ <web@__HOST_SIN_WWW__>\r\nContent-Type: text/plain; charset=UTF-8\r\n";
$enviado = @mail($para, $asunto, $cuerpo, $cab);
header('Location: ' . $vuelta . '?' . $clave . '=' . ($enviado ? '1' . $ancla : '0&motivo=envio' . $ancla_ko));
"""


def servidor():
    host = DOMINIO.split("//")[1]
    red = "\n".join(f"RewriteRule ^{re.escape(a)}/?$ {b} [L,R=301]" for a, b in REDIRECCIONES) or "# (ninguna)"
    red2 = "\n".join(f"RewriteRule ^{re.escape(a)}/?$ {b} [L,R=302]" for a, b in REDIRECCIONES_302) or "# (ninguna)"
    sust = {"__NOMBRE__": N["nombre"], "__DOMINIO__": DOMINIO, "__HOST_SIN_WWW__": host.removeprefix("www."),
            "__HOST__": host, "__CONTACTO__": URLS["contacto"], "__REDIRECCIONES_302__": red2, "__REDIRECCIONES__": red, "__EMAIL__": (getattr(CFG, "FORMULARIO", None) or {}).get("buzon") or N["email"]}
    h, e = HTACCESS, ENVIAR
    for k, v in sust.items():
        h, e = h.replace(k, v), e.replace(k, v)
    if not host.startswith("www."):
        pass  # dominio sin www: la regla de arriba quita el www
    else:  # dominio con www: se fuerza el www en lugar de quitarlo
        h = h.replace("# Sin www (paso 18)\nRewriteCond %{HTTP_HOST} ^www\\. [NC]", "# Con www (paso 18)\nRewriteCond %{HTTP_HOST} !^www\\. [NC]")
    open(S(".htaccess"), "w").write(h)
    open(S("enviar.php"), "w").write(e)


DIAS_N = {"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}


def js():
    """main.js del cliente con sus datos (horario, festivos, dominio, clave de cookies, textos del estado)."""
    N_ = N
    hosts = "|".join(re.escape(h) for h in HOST_PRODUCCION).replace("\\", "\\\\")
    sust = {"__HOSTS_RE__": hosts, "__COOKIES__": COOKIES_CLAVE, "__TZ__": N_["zona_horaria"],
            "__FESTIVOS__": json.dumps(N_["festivos"]), "__PASCUA__": json.dumps(N_.get("festivos_pascua", [])),
            "__DIAS_N__": json.dumps([DIAS_N[d] for d in N_["dias_schema"]]),
            "__ABRE_H__": str(int(N_["abre"][:2])), "__CIERRA_H__": str(int(N_["cierra"][:2])),
            "__ESTADO_ABIERTO__": json.dumps(texto("estado_abierto"), ensure_ascii=False),
            "__ESTADO_FUERA__": json.dumps(texto("estado_fuera"), ensure_ascii=False),
            "__PROMESA_ABIERTO__": json.dumps(texto("promesa_abierto"), ensure_ascii=False),
            "__PROMESA_ANTES__": json.dumps(texto("promesa_antes"), ensure_ascii=False),
            "__PROMESA_SIGUIENTE__": json.dumps(texto("promesa_siguiente", dia="{dia}"), ensure_ascii=False)}
    j = open(R("cliente", "js", "main.js"), encoding="utf-8").read()
    for k, v in sust.items():
        j = j.replace(k, v)
    faltan = re.findall(r"__[A-Z_]+__", j)
    if faltan:
        sys.exit(f"main.js: marcadores sin rellenar {faltan}")
    open(S("js", "main.js"), "w", encoding="utf-8").write(j)


def main():
    copiar()
    n = imagenes()
    k = css()
    servidor()
    print(f"rematar: {n} fotos × 4 variantes · estilo.css {k/1024:.1f} KB · v{VERSION}")


if __name__ == "__main__":
    main()
