# Día de publicar · Vinos Gallegos Pousada · lista de comprobación por HTTP

Pasos 42-45 del protocolo. Lo ejecuta Álvaro con el dominio ya apuntando al hosting del cliente (Plesk/Apache). Cada punto
tiene su orden de consola y el resultado que tiene que dar; si uno no sale, no se sigue. Fuente: Bruno (A4, M6 y Anexo A de
`09-AUDITORIA/02-BRUNO-SEO-TECNICO.md`), Turing (M1, M9) y Dani (C-02). Escrito el 09/10/2026 (paso 36).

Por qué importa: los 29 301, el paso a HTTPS y el sin-www viven solo en `.htaccess`, un archivo que GitHub no sube y que los
gestores de archivos esconden. Sin él, 36 URLs viejas con 1.029 clics (el 43 % del tráfico histórico) dan 404 el primer día
y la web se ve perfecta navegando por las URLs nuevas: el fallo es silencioso.

## 0 · Antes de subir nada

1. En `08-WEB/repositorio-vN/`: `python3 generador/build.py && python3 generador/rematar.py && python3 generador/controles.py`
   → `ERRORES: 0` y `0 con medida o srcset distintos del archivo`.
2. Datos que tienen que estar en `generador/config.py` ANTES de generar la versión que se publica (si faltan, se publica igual
   y se apuntan como pendientes, pero conviene que entren en esta versión):
   - `GTM_ID` (contenedor de Google Tag Manager; vacío = el código mide en `dataLayer` pero no carga nada).
   - `NEGOCIO["email_aviso"]` (segundo buzón para el aviso corto de cada solicitud; el de Álvaro el primer mes).
   - `FORMULARIO["buzon"]` confirmado (hoy `info@vinospousada.es`, ⚑ paso 44).
   - `NEGOCIO["cid"]`, `lat`/`lng` del pin y `geo_aproximado = False` si ya hay ficha de Google alineada (paso 3).
3. `python3 herramientas/entrega.py --cliente pousada --version N --produccion`
   → `08-WEB/HOSTING/` con SOLO el contenido de `sitio/` (incluidos `.htaccess` y `enviar.php`) y SIN `vercel.json`,
   más `08-WEB/pousada-vN-hosting.zip`. Es lo único que se sube al hosting. `vercel.json` lleva `X-Robots-Tag: noindex` para
   la vista previa de Vercel: si llega a producción, la web desaparece de Google.

## 1 · Subida al hosting (Plesk)

- Subir el CONTENIDO de `HOSTING/` a la raíz pública del dominio (`httpdocs/`), no la carpeta.
- Comprobar en el gestor de archivos que `.htaccess` está en la raíz (activar «mostrar archivos ocultos»). Si el hosting
  hace la subida por zip, usar `pousada-vN-hosting.zip` y descomprimirlo en `httpdocs/`.
- Si `vercel.json` aparece en el servidor (una subida anterior), borrarlo. El `.htaccess` lo niega de todas formas (`<Files "vercel.json">`).
- Borrar lo que quede del WordPress viejo en `httpdocs/` ANTES de subir (paso 39 solo vacía el hosting viejo si es otro).
- Permisos: archivos 644, carpetas 755. Para el registro `solicitudes-web.log` (se escribe en la carpeta PADRE de `httpdocs/`,
  fuera de lo público) hace falta que PHP pueda escribir ahí; si no puede, el correo sale igual y solo falta el registro.

## 2 · Comprobaciones por HTTP (con el dominio ya apuntando)

Desde cualquier terminal con `curl`. `-sI` pide solo las cabeceras.

### 2.1 HTTPS y sin www, en un solo salto

```bash
for u in http://vinospousada.es/ http://www.vinospousada.es/ https://www.vinospousada.es/ http://www.vinospousada.es/catalogo/; do
  curl -sIL -o /dev/null -w "$u → %{num_redirects} salto(s) → %{url_effective} (%{http_code})\n" "$u"
done
```
Esperado: `1 salto(s)` en los cuatro, `url_effective` que empieza por `https://vinospousada.es/` y `(200)`.
Si sale `0 salto(s)` con `http://`, el `.htaccess` no está o `AllowOverride` no lo permite (hablar con el hosting).
Si sale bucle (`ERR_TOO_MANY_REDIRECTS` en el navegador), hay un proxy delante que no manda `X-Forwarded-Proto`: avisar a Claude.

### 2.2 Las 29 URLs viejas → 301 → destino → 200

Lee las parejas del propio `.htaccess` generado (así nunca se desincroniza de la hoja 301):

```bash
cd 08-WEB/repositorio-vN
grep -E '^RewriteRule \^[a-z].*\[L,R=301\]$' sitio/.htaccess \
 | sed -E 's#^RewriteRule \^(.*)/\?\$ (\S+) .*#\1 \2#; s#\\##g' \
 | while read vieja nueva; do
     cod=$(curl -s -o /dev/null -w '%{http_code}' "https://vinospousada.es/$vieja")
     loc=$(curl -sI "https://vinospousada.es/$vieja" | awk 'tolower($1)=="location:"{print $2}' | tr -d '\r')
     fin=$(curl -s -o /dev/null -w '%{http_code}' "https://vinospousada.es$nueva")
     ok="OK"; [ "$cod" = "301" ] && [ "$loc" = "https://vinospousada.es$nueva" ] && [ "$fin" = "200" ] || ok="MAL"
     echo "$ok  /$vieja → $cod $loc → $fin  (esperado 301 https://vinospousada.es$nueva → 200)"
   done
```
Esperado: 29 líneas con `OK`. Las cinco que más tráfico traen (si solo hay tiempo para cinco, estas):

| URL vieja | Esperado | Clics históricos |
|---|---|---|
| `/productos/pousada/licores/crema-orujo/` | 301 → `/licores/crema-de-orujo/` → 200 | 562 (23 % del total) |
| `/vino/turbio/` | 301 → `/vino-turbio/` → 200 | 320 |
| `/productos/pousada/licores/vodka-caramelo/` | 301 → `/licores/` → 200 | 7.382 impresiones |
| `/comprar/vina-sobreira/` | 301 → `/denominaciones/rias-baixas/` → 200 | 77 |
| `/quienes-somos/` | 301 → `/nosotros/` → 200 | — |

Las fichas que conservan URL (`/comprar/finca-lavandeira/`, `/comprar/vino-terras-vellas-albarino/`, `/comprar/da-vina-galega/`:
296, 242 y 220 clics) tienen que dar `200` directo, sin salto: `curl -s -o /dev/null -w '%{http_code}\n' https://vinospousada.es/comprar/finca-lavandeira/`.

### 2.3 Restos de WordPress (410), página de error propia (404) y barra final

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://vinospousada.es/wp-admin/            # 410
curl -s -o /dev/null -w '%{http_code}\n' https://vinospousada.es/wp-login.php         # 410
curl -s -o /dev/null -w '%{http_code}\n' https://vinospousada.es/esto-no-existe/      # 404
curl -s https://vinospousada.es/esto-no-existe/ | grep -c 'Esta página no existe'     # 1 (es nuestra 404, no la de Apache)
curl -sI https://vinospousada.es/catalogo | awk 'tolower($1)=="location:"{print $2}'   # https://vinospousada.es/catalogo/
curl -sI https://vinospousada.es/sitemap_index.xml | awk 'tolower($1)=="location:"{print $2}'  # https://vinospousada.es/sitemap.xml
```

### 2.4 Cabeceras: ni rastro del noindex de la vista previa, seguridad, compresión y caché

```bash
curl -sI https://vinospousada.es/ | grep -i 'x-robots-tag'                    # NADA (vacío). Si sale «noindex», parar: es vercel.json o una regla del panel
curl -sI https://vinospousada.es/licores/crema-de-orujo/ | grep -i 'x-robots-tag'   # NADA
curl -s https://vinospousada.es/ | grep -o '<meta name="robots"[^>]*>'        # <meta name="robots" content="index, follow">
curl -s https://vinospousada.es/ | grep -o '<link rel="canonical"[^>]*>'      # href="https://vinospousada.es/"
curl -sI https://vinospousada.es/ | grep -iE 'x-content-type-options|referrer-policy|x-frame-options'   # nosniff · strict-origin-when-cross-origin · SAMEORIGIN
curl -sI -H 'Accept-Encoding: gzip, br' https://vinospousada.es/js/main.js | grep -iE 'content-encoding|cache-control|expires|content-type'
curl -sI -H 'Accept-Encoding: gzip, br' https://vinospousada.es/css/estilo.css | grep -iE 'content-encoding|cache-control|expires'
curl -sI https://vinospousada.es/fuentes/fraunces-500.woff2 | grep -i 'content-type'   # font/woff2
```
Esperado en JS y CSS: `content-encoding: gzip` (o `br`) y `cache-control: max-age=31536000` (o `expires` a un año). Si falta la
compresión, hay un nginx delante de Apache en Plesk: activar la compresión en el panel (Apache y nginx > «Compresión»).
Si `main.js` sale como `text/javascript` sin comprimir, el `.htaccess` ya cubre ese tipo (Bruno M6): el problema es del panel.

### 2.5 Archivos que no deben verse y archivos públicos que sí

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://vinospousada.es/vercel.json          # 403 o 404 (NUNCA 200)
curl -s -o /dev/null -w '%{http_code}\n' https://vinospousada.es/.htaccess            # 403
curl -s -o /dev/null -w '%{http_code}\n' https://vinospousada.es/enviar.php           # 302 (GET → redirige a /contacto/)
curl -s https://vinospousada.es/resenas.json                                          # sin ninguna clave que empiece por «_»
curl -sI https://vinospousada.es/robots.txt | grep -i 'content-type'                  # text/plain
curl -s https://vinospousada.es/robots.txt                                            # el comentario de rastreadores de IA + Sitemap
curl -sI https://vinospousada.es/llms.txt | grep -iE '^HTTP|content-type'             # 200 · text/plain; charset=utf-8
curl -sI https://vinospousada.es/sitemap.xml | grep -iE '^HTTP|content-type'          # 200 · xml
curl -sI https://vinospousada.es/og-image.jpg | grep -E '^HTTP'                       # 200
curl -sI https://vinospousada.es/site.webmanifest | grep -i 'content-type'            # application/manifest+json
```

### 2.6 Formulario (Dani C-02, C-03): envío real, errores con motivo y trampa

1. Tres envíos desde móvil y tres desde ordenador en `https://vinospousada.es/contacto/`, con datos reales de prueba
   (nombre «PRUEBA», negocio «PRUEBA WEB»). Cada uno tiene que volver a `/contacto/?enviado=1#form-ok` con el aviso
   «Solicitud recibida» y llegar al buzón (bandeja o spam) en menos de un minuto; si `email_aviso` está puesto, también el aviso corto.
2. Teléfono mal en el navegador: «abc» y «12345» no dejan enviar y el mensaje dice el formato («Escriba un teléfono de 9 cifras…»).
3. Servidor, sin navegador (la vuelta trae el motivo, nunca un error genérico):
```bash
curl -s -o /dev/null -w '%{redirect_url}\n' -X POST https://vinospousada.es/enviar.php \
  -d tipo=contacto -d pagina=/contacto/ -d nombre=PRUEBA -d negocio=PRUEBA -d tipo_negocio=Bar -d telefono=12345 -d t=5000
# → https://vinospousada.es/contacto/?enviado=0&motivo=telefono#form-error
curl -s -o /dev/null -w '%{redirect_url}\n' -X POST https://vinospousada.es/enviar.php \
  -d tipo=contacto -d pagina=/contacto/ -d nombre=PRUEBA -d negocio=PRUEBA -d tipo_negocio=Bar -d telefono=666631615 -d t=5000 -d contacto_alt=robot
# → …?enviado=1#form-ok  y NO llega ningún correo (trampa rellena = robot; es el único descarte, y queda en el registro)
```
4. Si los correos van a spam: SPF, DKIM y DMARC del dominio para `web@vinospousada.es` (`dig TXT vinospousada.es`,
   `dig TXT default._domainkey.vinospousada.es`). Lo configura el hosting; sin ello `mail()` de PHP cae en spam a menudo.
5. Después de las pruebas, borrar los correos de prueba del buzón del cliente.

### 2.7 Medición (Dani C-01, Turing M9), solo si `GTM_ID` ya está puesto

- `curl -s https://vinospousada.es/ | grep -o '<html[^>]*>'` → `data-gtm="GTM-…"` con el ID del contenedor.
- Vista previa de GTM sobre `https://vinospousada.es/`: aceptar cookies, pulsar «Solicitar tarifa» (evento `clic_cta_tarifa`
  con `origen`), el teléfono (`clic_llamar`), WhatsApp (`clic_whatsapp`), un filtro del catálogo (`filtro_catalogo`), un envío
  de prueba (`formulario_enviado` UNA sola vez, con `origen`, `interes`, `tipo_negocio`) y un envío con teléfono mal (`formulario_error`).
- GA4 DebugView: los mismos eventos; marcar como clave solo `formulario_enviado` y `clic_llamar` (filtrado a móvil y tableta).
- El código solo carga GTM en `vinospousada.es` y `www.vinospousada.es`: en la vista previa de Vercel no se mide nunca.

## 3 · Search Console y robots (propiedad de prefijo `https://vinospousada.es/`)

1. Sitemaps: enviar `https://vinospousada.es/sitemap.xml`; quitar de la lista el `sitemap_index.xml` antiguo (ya redirige).
2. Inspección de URL y «Solicitar indexación» de: `/`, `/vino-turbio/`, `/licores/crema-de-orujo/`, `/catalogo/`, `/contacto/`.
3. NO usar la herramienta de eliminación de URLs para las viejas: los 301 hacen el trabajo.
4. Pedir a Álvaro la verificación de la propiedad de DOMINIO (registro TXT en el DNS) el día que se toque el DNS: sin ella no
   se ve `http://` ni `www` y el informe de IA generativa de Search Console puede salir incompleto (Turing M9).
5. `robots.txt`: rastreadores de IA abiertos a propósito, con el comentario y la fecha dentro del archivo (decisión del 09/10/2026,
   opción A de Turing). Si Álvaro cambia de política, se cambia en `generador/build.py` (bloque de robots.txt), no a mano en el servidor.

## 4 · Calendario después de publicar

- A las 48-72 h: inspección de URL en 5 páginas; cobertura; que las 29 viejas sigan en 301 (repetir 2.2).
- A los 7 días: páginas indexadas (objetivo 49 de 49) y errores de rastreo; primer vistazo a `solicitudes-web.log` y al buzón.
- A las 4 semanas: Core Web Vitals con datos reales (INP y LCP; si INP > 200 ms, revisar Lenis/GSAP: Bruno B3), fragmentos de
  producto (objetivo 0 errores: ya no se emite `Product`), posiciones de «crema de orujo grados» e «ingredientes» (objetivo 1-5),
  y la batería de 25 preguntas a los motores de IA del Anexo D de Turing (comparar con la tanda hecha con la web vieja).
- Antes de vaciar el hosting viejo (paso 39): comprobar los restos de la anomalía de `maquinariataski.com` en el sitemap de categorías.

## 5 · Pendiente de dato (no bloquea la publicación; sí la nota de la reauditoría)

| Dato | Para qué | Quién |
|---|---|---|
| CID de la ficha de Google (y ficha alineada: 666 631 615, 8:00-20:00, categoría de mayorista, dirección completa) | `geo`, `hasMap`, `sameAs`, mapa y enlace a reseñas | Álvaro / Matías |
| `GTM_ID` | Medición: sin él no hay reauditoría con datos | Álvaro / Iñaki |
| Buzón del formulario confirmado y `email_aviso` | Que ninguna solicitud se pierda y que llegue aviso al móvil | Álvaro / David |
| SPF, DKIM y DMARC de `vinospousada.es` | Que el correo del formulario no caiga en spam | Hosting |
