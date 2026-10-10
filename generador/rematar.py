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
                # El recorte del alfa es el de plantilla.recorta_alfa: la página declara las medidas de la imagen recortada (Bruno A3)
                from plantilla import tamanos_producto, recorta_alfa
                im = Image.open(os.path.join(d, f)).convert("RGBA" if alfa else "RGB")
                if alfa:
                    im = recorta_alfa(im)
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
    corto = N.get("nombre_corto") or N["nombre"]
    open(S("site.webmanifest"), "w", encoding="utf-8").write(json.dumps({
        "name": N["nombre"], "short_name": corto if len(corto) <= 12 else corto[:12].rstrip(),   # «Pousada», no «Vinos Galleg» (Bruno B7)
        "icons": [{"src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"}],
        "theme_color": COLOR_TEMA, "background_color": COLOR_TEMA, "display": "standalone"}, ensure_ascii=False))
    os.makedirs(S("js"), exist_ok=True)
    js()
    shutil.copytree(R("cliente", "js", "vendor"), S("js", "vendor"), dirs_exist_ok=True)
    if OBJETO_PORTADA.get("tipo") != "3d" and os.path.exists(S("js", "vendor", "objeto3d.min.js")):
        os.remove(S("js", "vendor", "objeto3d.min.js"))   # three.js solo si hay objeto 3D
    if os.path.exists(R("cliente", "js", "tema.js")):
        open(S("js", "tema.js"), "w", encoding="utf-8").write(medicion_tema(open(R("cliente", "js", "tema.js"), encoding="utf-8").read()))
    # resenas.json es público (lo lee main.js): sale sin las claves internas que empiezan por «_» (Bruno M6, Matías L-15)
    _res = json.load(open(R("contenido", "resenas.json"), encoding="utf-8"))
    open(S("resenas.json"), "w", encoding="utf-8").write(json.dumps({k: v for k, v in _res.items() if not str(k).startswith("_")}, ensure_ascii=False))
    # Vista previa en Vercel (Root Directory = sitio): nunca se indexa. Las mismas redirecciones 301 de un salto que el
    # .htaccess (hoja 301 de la arquitectura), para que la vista previa se pueda probar con las URLs viejas.
    # En producción (Plesk) este archivo NO se sube: herramientas/entrega.py --produccion lo deja fuera y el .htaccess lo niega.
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
# vercel.json es solo de la vista previa: si alguien lo sube por error, no se sirve (Bruno M6)
<Files "vercel.json">
  Require all denied
</Files>
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
# text/javascript además de application/javascript: según la versión de Apache sirve .js con uno u otro (Bruno M6)
AddOutputFilterByType DEFLATE text/html text/css application/javascript text/javascript image/svg+xml application/json text/xml application/xml text/plain
</IfModule>

<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType text/html "access plus 0 seconds"
ExpiresByType text/css "access plus 1 year"
ExpiresByType application/javascript "access plus 1 year"
ExpiresByType text/javascript "access plus 1 year"
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
/* __NOMBRE__ · formulario de solicitud de tarifa (y «Que me llamen», si la web lo lleva).
   Antispam sin captcha: campo trampa con nombre sin sentido (__TRAMPA__), tiempo en la página y sin enlaces en el mensaje.
   «t» lo rellena main.js al enviar: milisegundos que lleva la página abierta. Un envío demasiado rápido (o con la página
   abierta más de 24 h) NO se descarta: se envía igual, marcado como SOSPECHOSO en el asunto. Solo se descarta la trampa
   rellena (un robot). Ningún descarte silencioso (Dani C-02): cada rechazo vuelve con su motivo y queda en el registro.
   Buzón de destino: __EMAIL__ · aviso corto a un segundo buzón: __EMAIL_AVISO__ (vacío = sin aviso).
   Registro sin datos personales (fecha, resultado, motivo, página) en ../solicitudes-web.log, fuera de la carpeta
   pública, si el hosting deja escribir ahí. */
header('X-Robots-Tag: noindex');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: __CONTACTO__'); exit; }
$c = function ($k, $max) { return trim(mb_substr(strip_tags((string)($_POST[$k] ?? '')), 0, $max)); };
$tipo = ($_POST['tipo'] ?? '') === 'llamada' ? 'llamada' : 'contacto';
$pagina = $c('pagina', 120);
if (!preg_match('#^/[a-z0-9\-/]*$#', $pagina) || strpos($pagina, '//') !== false) { $pagina = '/'; }
$nombre = $c('nombre', 80); $telefono = $c('telefono', 20); $negocio = $c('negocio', 80); $tipo_negocio = $c('tipo_negocio', 30);
$municipio = $c('municipio', 60); $mensaje = $c('mensaje', 2000);
$trampa = (string)($_POST['__TRAMPA__'] ?? ''); $t = (int)($_POST['t'] ?? 0);
/* Teléfono: se admite +34, espacios, puntos, guiones y paréntesis; se exigen de 9 a 15 cifras */
$solo = preg_replace('/[^0-9+]/', '', $telefono); $cifras = strlen(preg_replace('/\D/', '', $solo));
$motivo = '';
if ($trampa !== '') { $motivo = 'trampa'; }
elseif ($nombre === '') { $motivo = 'nombre'; }
elseif ($cifras < 9 || $cifras > 15 || strpos($solo, '+') > 0) { $motivo = 'telefono'; }
elseif ($tipo === 'contacto' && $negocio === '') { $motivo = 'negocio'; }
elseif ($tipo === 'contacto' && $tipo_negocio === '') { $motivo = 'tipo_negocio'; }
elseif (preg_match('#https?://|www\.#i', $mensaje)) { $motivo = 'enlaces'; }
$sospechoso = ($t < 3000 || $t > 86400000);
if ($tipo === 'llamada') { $vuelta = $pagina; $clave = 'llamada'; $ancla = '#te-llamamos'; $ancla_ko = '#te-llamamos'; }
else { $vuelta = ($pagina !== '/' && $pagina !== '') ? $pagina : '__CONTACTO__'; $clave = 'enviado'; $ancla = '#form-ok'; $ancla_ko = '#form-error'; }
$registro = function ($linea) { @file_put_contents(dirname(__DIR__) . '/solicitudes-web.log', date('c') . ' ' . $linea . "\n", FILE_APPEND | LOCK_EX); };
if ($motivo === 'trampa') { $registro("robot pagina=$pagina"); header('Location: ' . $vuelta . '?' . $clave . '=1' . $ancla); exit; } /* a los robots no se les da pista */
if ($motivo !== '') { $registro("rechazado motivo=$motivo pagina=$pagina"); header('Location: ' . $vuelta . '?' . $clave . '=0&motivo=' . $motivo . $ancla_ko); exit; }
$para = '__EMAIL__'; $aviso = '__EMAIL_AVISO__';
$marca = $sospechoso ? 'SOSPECHOSO · ' : '';
$interes = preg_match('/me interesa:\s*([^.\n]{1,80})/iu', $mensaje, $mi) ? trim($mi[1]) : '';
$segundos = $t > 0 ? round($t / 1000) . ' s con la página abierta' : 'tiempo en la página desconocido';
if ($tipo === 'llamada') {
  $asunto = '=?UTF-8?B?' . base64_encode($marca . 'QUE ME LLAMEN · ' . $nombre . ' · ' . $telefono) . '?=';
  $cuerpo = "Petición de llamada desde la web.\n\nNombre: $nombre\nTeléfono: $telefono\nPágina: __DOMINIO__$pagina\n$segundos\n";
} else {
  $asunto = '=?UTF-8?B?' . base64_encode($marca . 'SOLICITUD DE TARIFA · ' . $negocio . ' (' . $tipo_negocio . ') · ' . $nombre . ' · ' . $telefono . ($interes !== '' ? ' · ' . $interes : '')) . '?=';
  $cuerpo = "Solicitud de tarifa desde la web.\n\nNombre: $nombre\nNegocio: $negocio\nTipo de negocio: $tipo_negocio\nTeléfono: $telefono\n"
    . ($municipio !== '' ? "Municipio: $municipio\n" : '') . ($interes !== '' ? "Le interesa: $interes\n" : '')
    . "\nMensaje:\n" . ($mensaje !== '' ? $mensaje : '(sin mensaje)') . "\n\nPágina: __DOMINIO__$pagina\n$segundos"
    . ($sospechoso ? " (marcada como sospechosa: puede ser un robot; si los datos tienen sentido, es una solicitud real)" : '')
    . "\n-- Enviado desde __HOST____CONTACTO__\n";
}
$cab = "From: Web __NOMBRE__ <web@__HOST_SIN_WWW__>\r\nReply-To: Web __NOMBRE__ <web@__HOST_SIN_WWW__>\r\nContent-Type: text/plain; charset=UTF-8\r\n";
$enviado = @mail($para, $asunto, $cuerpo, $cab);
if ($aviso !== '' && $aviso !== $para) {
  /* Aviso corto al segundo buzón (el móvil lo muestra entero en la notificación): quién, qué tipo de local y el teléfono */
  $asunto2 = '=?UTF-8?B?' . base64_encode($marca . 'Aviso · solicitud de tarifa en la web · ' . ($tipo === 'llamada' ? $nombre : $negocio)) . '?=';
  $cuerpo2 = "Ha entrado una solicitud en __DOMINIO__.\n" . ($tipo === 'llamada' ? "Nombre: $nombre" : "Negocio: $negocio ($tipo_negocio)") . "\nTeléfono: $telefono\n"
    . ($interes !== '' ? "Le interesa: $interes\n" : '') . "\nEl correo completo " . ($enviado ? "está en $para." : "NO se ha podido entregar en $para: llame a este teléfono.") . "\n";
  @mail($aviso, $asunto2, $cuerpo2, $cab);
}
$registro(($enviado ? 'enviado' : 'FALLO-mail') . " tipo=$tipo pagina=$pagina tipo_negocio=$tipo_negocio" . ($sospechoso ? ' sospechoso' : ''));
header('Location: ' . $vuelta . '?' . $clave . '=' . ($enviado ? '1' . $ancla : '0&motivo=envio' . $ancla_ko));
"""


def servidor():
    host = DOMINIO.split("//")[1]
    red = "\n".join(f"RewriteRule ^{re.escape(a)}/?$ {b} [L,R=301]" for a, b in REDIRECCIONES) or "# (ninguna)"
    red2 = "\n".join(f"RewriteRule ^{re.escape(a)}/?$ {b} [L,R=302]" for a, b in REDIRECCIONES_302) or "# (ninguna)"
    F = getattr(CFG, "FORMULARIO", None) or {}
    sust = {"__NOMBRE__": N["nombre"], "__DOMINIO__": DOMINIO, "__HOST_SIN_WWW__": host.removeprefix("www."),
            "__HOST__": host, "__CONTACTO__": URLS["contacto"], "__REDIRECCIONES_302__": red2, "__REDIRECCIONES__": red,
            "__EMAIL__": F.get("buzon") or N["email"],
            "__EMAIL_AVISO__": N.get("email_aviso") or "",            # segundo buzón (aviso corto); vacío = sin aviso
            "__TRAMPA__": F.get("trampa") or "contacto_alt"}          # el mismo nombre de campo que pone build.formulario()
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


PARCHES_AVISOS = []   # anclas de medición que no se han encontrado en el JS (controles.py lo comprueba sobre sitio/js/)


def _parche(j, viejo, nuevo, que, archivo):
    """Sustitución anclada en el JS del cliente. Si el ancla no está (alguien ha reescrito ese trozo), avisa y sigue:
    controles.py falla después si en sitio/js/ quedan nombres de evento viejos o falta clic_cta_tarifa."""
    if viejo not in j:
        PARCHES_AVISOS.append(f"{archivo}: ancla no encontrada para «{que}»")
        print(f"rematar: AVISO · {archivo}: ancla no encontrada para «{que}» (controles.py lo comprobará)")
        return j
    return j.replace(viejo, nuevo)


def medicion_main(j):
    """Capa de medición de Pousada sobre el main.js de la base (Dani C-01, C-03, C-16, C-26), sin tocar cliente/js/main.js.
    Un solo nombre por evento, el de la tabla de Dani (FIRMA.md §5), en castellano («clic», no «click»):
      clic_llamar · clic_whatsapp · clic_cta_tarifa (origen, interes) · formulario_enviado (una sola vez; origen, interes,
      tipo_negocio) · formulario_error (campo o motivo) · filtro_catalogo (en tema.js). Fuera los heredados de otras webs
      (solicitud_llamada, click_te_llamamos, click_cta_extra). El motivo del servidor se traduce a un texto concreto."""
    A = "main.js"
    j = _parche(j, 'w.dataLayer.push({ event: /^tel:/.test(href) ? "click_llamar" : "click_whatsapp", ubicacion: ubicacion(a), pagina: PAG, abierto: ABIERTO === true });',
                'w.dataLayer.push({ event: /^tel:/.test(href) ? "clic_llamar" : "clic_whatsapp", ubicacion: ubicacion(a), pagina: PAG, abierto: ABIERTO === true });',
                "clic_llamar / clic_whatsapp", A)
    j = _parche(j, '''    } else if (/maps\\.google\\.com\\/\\?cid/.test(href)) {
      w.dataLayer.push({ event: "click_resenas_google", ubicacion: ubicacion(a), pagina: PAG });
    } else if (a.classList.contains("tarjeta__ir")) {
      w.dataLayer.push({ event: "click_te_llamamos", pagina: PAG });
    } else if (a.matches(".tarjeta__extra, .banda__extra, .mini__extra")) {
      w.dataLayer.push({ event: "click_cta_extra", ubicacion: ubicacion(a), destino: href, pagina: PAG });
    }''',
                '''    } else if (/maps\\.google\\.com\\/\\?cid/.test(href)) {
      w.dataLayer.push({ event: "clic_resenas_google", ubicacion: ubicacion(a), pagina: PAG });
    } else if (/^__CONTACTO_RE__([?#]|$)/.test(href)) {
      /* Dani C-01: cualquier enlace a la página de contacto es «clic_cta_tarifa», con la ubicación, la página de origen y el interés (?interes=) */
      var mi = /[?&]interes=([a-z0-9\\-]+)/i.exec(href);
      w.dataLayer.push({ event: "clic_cta_tarifa", ubicacion: ubicacion(a), origen: PAG, interes: mi ? mi[1] : "", pagina: PAG });
    }''', "clic_cta_tarifa", A)
    j = _parche(j, '  if (/llamada=1/.test(q)) w.dataLayer.push({ event: "solicitud_llamada", pagina: w.location.pathname });\n', "", "solicitud_llamada fuera", A)
    j = _parche(j, '  if (/enviado=1/.test(q)) w.dataLayer.push({ event: "formulario_enviado", pagina: w.location.pathname });',
                '  if (/enviado=1/.test(q)) { var ev = w.__gyfEnvio || {}; w.dataLayer.push({ event: "formulario_enviado", pagina: w.location.pathname, origen: ev._origen || "", interes: ev._interes || "", tipo_negocio: ev.tipo_negocio || "" }); }',
                "formulario_enviado con origen/interes/tipo_negocio", A)
    j = _parche(j, '    var datos = {}; camposForm(f).forEach(function (i) { datos[i.name] = i.value; });\n',
                '''    var datos = {}; camposForm(f).forEach(function (i) { datos[i.name] = i.value; });
    var sel = f.querySelector('select[name="tipo_negocio"]'); if (sel) datos.tipo_negocio = sel.value;
    var qi = /[?&]interes=([a-z0-9\\-]+)/i.exec(w.location.search); datos._interes = qi ? qi[1] : "";
    try { var ref = d.referrer ? new URL(d.referrer) : null; datos._origen = ref && ref.hostname === w.location.hostname ? ref.pathname : ""; } catch (x) { datos._origen = ""; }
''', "datos del envío (interes, origen, tipo_negocio)", A)
    j = _parche(j, '''      if (okForm) { sessionStorage.removeItem(k); return; }
      var datos = JSON.parse(sessionStorage.getItem(k) || "null"); if (!datos) return;
      camposForm(f).forEach(function (i) { if (datos[i.name] && !i.value) i.value = datos[i.name]; });''',
                '''      var datos = JSON.parse(sessionStorage.getItem(k) || "null");
      if (okForm) { if (datos) w.__gyfEnvio = datos; sessionStorage.removeItem(k); return; }
      if (!datos) return;
      camposForm(f).forEach(function (i) { if (datos[i.name] && !i.value) i.value = datos[i.name]; });
      var s2 = f.querySelector('select[name="tipo_negocio"]'); if (s2 && datos.tipo_negocio && !s2.value) s2.value = datos.tipo_negocio;''',
                "recuperar lo escrito (también el tipo de negocio)", A)
    j = _parche(j, 'event: "form_error"', 'event: "formulario_error"', "formulario_error", A)
    j = _parche(j, 'i.name !== "web"', 'i.name !== "__TRAMPA__"', "nombre del campo trampa", A)
    j = _parche(j, '  if (ko && /enviado=0/.test(q)) ko.hidden = false;',
                '''  if (ko && /enviado=0/.test(q)) {
    ko.hidden = false;
    /* Dani C-03: el motivo que devuelve enviar.php se traduce al texto concreto de data-motivos (lo escribe build.formulario) */
    try {
      var mo = /[?&]motivo=([a-z_\\-]+)/i.exec(q), mapa = JSON.parse(ko.getAttribute("data-motivos") || "{}"), tx = ko.querySelector("[data-error-texto]");
      if (tx && mo && mapa[mo[1]]) tx.textContent = mapa[mo[1]];
    } catch (x) {}
  }''', "texto de error por motivo", A)
    return j


def medicion_tema(j):
    """tema.js: el envío del formulario ya lo cuenta main.js (formulario_enviado); aquí se quita el duplicado envio_formulario."""
    lineas = j.split("\n")
    sin = [l for l in lineas if 'event: "envio_formulario"' not in l]
    if len(sin) == len(lineas):
        PARCHES_AVISOS.append("tema.js: no estaba el push envio_formulario (¿ya quitado?)")
    return "\n".join(sin)


def js():
    """main.js del cliente con sus datos (horario, festivos, dominio, clave de cookies, textos del estado) y la capa de medición."""
    N_ = N
    hosts = "|".join(re.escape(h) for h in HOST_PRODUCCION).replace("\\", "\\\\")
    F = getattr(CFG, "FORMULARIO", None) or {}
    sust = {"__HOSTS_RE__": hosts, "__COOKIES__": COOKIES_CLAVE, "__TZ__": N_["zona_horaria"],
            "__CONTACTO_RE__": URLS["contacto"].replace("/", "\\/"), "__TRAMPA__": F.get("trampa") or "contacto_alt",
            "__FESTIVOS__": json.dumps(N_["festivos"]), "__PASCUA__": json.dumps(N_.get("festivos_pascua", [])),
            "__DIAS_N__": json.dumps([DIAS_N[d] for d in N_["dias_schema"]]),
            "__ABRE_H__": str(int(N_["abre"][:2])), "__CIERRA_H__": str(int(N_["cierra"][:2])),
            "__ESTADO_ABIERTO__": json.dumps(texto("estado_abierto"), ensure_ascii=False),
            "__ESTADO_FUERA__": json.dumps(texto("estado_fuera"), ensure_ascii=False),
            "__PROMESA_ABIERTO__": json.dumps(texto("promesa_abierto"), ensure_ascii=False),
            "__PROMESA_ANTES__": json.dumps(texto("promesa_antes"), ensure_ascii=False),
            "__PROMESA_SIGUIENTE__": json.dumps(texto("promesa_siguiente", dia="{dia}"), ensure_ascii=False)}
    j = medicion_main(open(R("cliente", "js", "main.js"), encoding="utf-8").read())
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
