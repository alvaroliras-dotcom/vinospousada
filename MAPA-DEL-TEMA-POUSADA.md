# 010 · GYF-Jesper (Pousada) · Mapa de lo que cambia respecto al tema de Rayo

Escrito el 07/10/2026 (pasos 23-27 de Vinos Gallegos Pousada). Este repositorio nace de `003-RAYO/tema/` (base GYF +
Rayo) y le añade **el tema de la plantilla Jesper** (ficha en `07-FIRMA-GRAFICA/010-JESPER-para-la-biblioteca/`) en modo
claro, con las piezas de Antra y Floka que eligió la firma gráfica (`07-FIRMA-GRAFICA/FIRMA.md`) y los **tipos de página
de un catálogo** (hubs, fichas, rejilla filtrable). Todo lo nuevo es código propio, sin jQuery ni librerías nuevas: GSAP +
ScrollTrigger + Lenis ya venían en `cliente/js/vendor/`.

Este archivo es lo que se lleva a la biblioteca en el paso 48 como `010-JESPER/tema/` (junto a `MAPA-DEL-TEMA.md` de
Rayo, que sigue valiendo para todo lo que no se nombra aquí). Lo que aquí se marca **(tema)** vale para cualquier cliente;
lo marcado **(Pousada)** es dato de este cliente y vive en `config.py` o en `contenido/`.

---

## 1. Resumen de cambios por archivo

| Archivo | Qué cambia | Para la biblioteca |
|---|---|---|
| `generador/config.py` | Reescrito para Pousada. Claves nuevas del tema: `PORTADA` (foto en caja, texto de confianza), `URLS` con `servicio`, `catalogo`, `ficha`, `denominacion`, `turbio`, `licores`; `DENOMINACIONES` (nombre, uva, descripción, tinte); `ESTANTERIA`, `ESTANTERIA_ETIQUETA/NOTA`; `CATALOGO_HOME_BOTELLAS`, `TURBIO_FOTO`, `TURBIO_FOTO_BANDA`, `LICORES_FOTO`, `CASA_FOTO`, `CASA_HITOS`, `REPARTO_MUNICIPIOS`, `REPARTO_FOTO`; `GRIFO` (banda oscura del motivo); `MENU_BOTON`; `PIE_COLUMNAS`, `PIE_FRASES`, `PIE_FRASES_TIPO`, `PIE_SUB`; `FORMULARIO` (cinco campos, textos, buzón); interruptores `OPINIONES_SECCION`, `PIE_ESTILO` («oscuro» / «tarjetas»), `CAB_ESTILO` («barra» / «capa»), `MAPA_SECCION`; H2 que el tema reconoce: `CASA_H2`, `CATALOGO_H2`, `PROVEEDOR_H2`, `PASOS_H2`; `NO_SE_DICE` (frases prohibidas de PROMESAS para `controles.py`). `MARCA["logo"] = None` compone racimo + nombre en HTML (`logo_texto`). `OBJETO_PORTADA["tipo"] = None` apaga el objeto de Rayo | **(tema)** las claves; **(Pousada)** los valores |
| `generador/datos.py` | `tipo_de()` reconoce `catalogo`, `ficha`, `denominacion`, `turbio`, `licores`, `licor`. Lee `contenido/catalogo.json` (`catalogo()`, `producto()`). Front-matter nuevo: `Producto:` (slug) y `Denominacion:` (clave). `inline()` convierte `` `código` `` en `<code>` | **(tema)** |
| `generador/plantilla.py` | Cabecera **barra** (menú horizontal en ≥ 1.025 px + teléfono + botón; capa a pantalla completa solo en móvil y tableta). Logo compuesto en HTML. Símbolos **de trazo** (`stroke`) en el sprite y `simbolo_trazado()` (paths en línea para trazarlos con JS). `foto()` no amplía (800 siempre; 1600 solo si el original ≥ 1.200). `producto_img()` + `tamanos_producto()` (lado mayor a 420/840, alfa). `pieza_tipografica()` (sin foto, nunca vacío). `pie()` → `pie_oscuro()` (frase por página de `PIE_FRASES`, 4 columnas, racimo que se traza) o `pie_tarjetas()` (Rayo). `btn_tarifa()`. Carga `cliente/js/tema.js` tras `main.js` si existe. Aviso de cookies con dos botones iguales («Aceptar todas» / «Solo las necesarias») | **(tema)** |
| `generador/build.py` | Piezas nuevas: `portada_foto` (A1 + Antra index-7), `estanteria` (F1 + cinta C5), `bloque_partido` (C1), `bloque_filete` (lista 01-05 de Antra), `cajas_catalogo` (2/3 + 1/3), `grifo` (banda oscura del motivo), `casa` (foto + hitos), `reparto` (píldoras), `formulario` de cinco campos + `tarifa`, `cab_interior` (con tinte y racimo en los hubs de D.O.), `cierre` (último H2 + botones de la tabla), `catalogo_pagina` (tarjetas de D.O. + `filtros()` + `rejilla()`), `ficha_pagina` (foto grande o pieza tipográfica, `datos_producto()`, lectura, «también le puede interesar» = 3 de la misma D.O., cierre), `hub_pagina` (D.O. / turbio / licores: la lista de enlaces a fichas del texto se sustituye por la rejilla y su texto se conserva), `enlaces_desc_html` (listas «**[Nombre](/url/):** texto» → tarjetas con miniatura). Schema: `Product` **sin precio** (`additionalProperty` con D.O., uva, graduación, formato…) + `BreadcrumbList` en fichas; `ItemList` en hubs; `WholesaleStore` con `taxID`; `aggregateRating` y `hasMap` solo si hay datos. Migas de ficha: Inicio → Catálogo → D.O. → vino. `pagina_legal()` pinta markdown completo (listas, tablas, h3). `llms.txt` con denominaciones y catálogo. Opiniones, cifras, casos y objeto 3D solo si están activados | **(tema)** |
| `generador/rematar.py` | Fotos sin ampliar; `recursos/producto/` → 420/840 WebP con alfa + PNG/JPG; **caché** de variantes en `recursos/.cache-img/` (un build pasa de 2 min a 0,4 s); fuentes itálicas (`-italic`); `vercel.json` con `noindex`; `objeto3d.min.js` solo si hay 3D; `enviar.php` con los cinco campos (negocio, tipo de negocio), asunto «SOLICITUD DE TARIFA · local (tipo) · nombre», a los robots les responde como si fuera bien; buzón de `FORMULARIO["buzon"]` | **(tema)** |
| `generador/controles.py` | **Promesas** (v11): ERROR si hay un precio en el texto o una frase de `NO_SE_DICE`; AVISO si una página usa el pie de defecto; fotos < 800 px (producto: lado mayor < 400) ERROR; portada < 1.600 ERROR; PROVISIONAL en el nombre → AVISO; catálogo sin foto o con foto provisional → AVISO; reseñas de EJEMPLO solo avisan si `OPINIONES_SECCION`; CID pendiente → AVISO | **(tema)** |
| `base/css/base.css` | **Intacto** | — |
| `cliente/css/tema.css` | Reescrito entero: tokens de FIRMA (Fraunces + Instrument Sans locales, turquesa en tres valores, hueso, verde-tinta), botones con barrido (Antra) sobre el texto que rueda (base), cabecera barra, y el CSS de todas las piezas nuevas (§5-16 del archivo). Overrides de piel sobre las piezas de Rayo que se siguen usando (índice, FAQ, migas, formularios, cookies) | **(tema)** la estructura; **(Pousada)** los valores de los tokens |
| `cliente/js/main.js` | Dos retoques mínimos: el selector de la barra fija del móvil admite `[data-acciones]`, y al final de `capa()` añade `html.con-gsap` y dispara el evento **`gyf:capa`** con GSAP/ScrollTrigger/Lenis para que el tema enganche su movimiento sin tocar la base | **(tema)**: llevar a la base de Rayo |
| `cliente/js/tema.js` | **Nuevo.** Capa de movimiento del tema (§3) + filtros del catálogo + formulario (prerrelleno `?interes=`, frase «particular», «Enviando…»). Mejora progresiva y `prefers-reduced-motion` | **(tema)** |
| `cliente/js/vendor/` | Sin cambios (GSAP, ScrollTrigger, Lenis, objeto3d) | — |
| `herramientas/entrega.py` | Reescrito: sin git (en las carpetas conectadas no se usa), tandas < 100 archivos y < 25 MB con comprobación, carpetas TANDA-n + zip, LEEME con el alta de Vercel | **(tema)** |
| `herramientas/importar_textos.py` | **Nuevo (Pousada).** Convierte los textos de Merche (05-TEXTOS-NUEVOS, 04-LEGALES) al formato del tema: quita lo que no se publica (⚑ por frases, notas, botones, vodka caramelo), FAQ al bloque `---\nFAQ`, legales a `legales.md`. Deja `contenido/NO-PUBLICADO.txt` con las frases que han caído | **(Pousada)**; el patrón vale para otros clientes |
| `recursos/` | `marca/`: racimo reconstruido en SVG como trazo (7 arcos; el cliente no tenía vector), en turquesa, blanco y oscuro; OG 1.200 × 630 compuesto. `fuentes/`: Fraunces 500/600 + 500 itálica e Instrument Sans 400/500/600, subconjunto latino, woff2 (de google/fonts, instanciadas con fontTools). `favicon/`: del racimo. `producto/`: 31 imágenes (ver §4). `fotos/`: 6 de ambiente. Sin `casos/` ni `objeto/` | **(Pousada)** |
| `contenido/` | `catalogo.json` (32 productos con D.O., tipo, uva, graduación, formato, temperatura, maridaje, foto, alt, provisional), 49 páginas, `legales.md`, `resenas.json` vacío | **(Pousada)**; el formato de `catalogo.json` es **(tema)** |

## 2. Tipos de página del tema (añadidos a los de Rayo)

| Tipo | URL (Pousada) | Qué pinta |
|---|---|---|
| `home` | `/` | Portada con foto en caja → estantería → bloque partido («Un proveedor…») → lista con filete («Cómo trabajamos») → cajas 2/3 + 1/3 («Vinos gallegos, vino turbio y licores») → **el grifo del turbio** → la casa («Una casa familiar…») → reparto («Reparto en toda la provincia») → tarifa (último H2 + formulario) → pie |
| `servicio` / `municipio` / `empresa` | hostelería, Madrid, Alcorcón, nosotros | Cabecera interior → lectura con índice clavado (listas «**Título.** texto» → filete) → FAQ → cierre → pie |
| `catalogo` | `/catalogo/` | Cabecera → primer H2 con la lista de D.O. como tarjetas → rejilla filtrable (por D.O. y por tipo; filtros solo con JS) → resto de H2 en partido → cierre |
| `ficha` / `licor` | `/comprar/<slug>/` · `/licores/<slug>/` | Foto grande (o pieza tipográfica) + H1 + entradilla + botones + **datos** → lectura (Características, Maridaje…) → FAQ → «También le puede interesar» (3 de la misma D.O. o familia) → cierre («Para su carta») → pie con la frase de ficha. Schema `Product` sin precio |
| `denominacion` | `/denominaciones/<do>/` | Cabecera con tinte de la D.O. y el racimo que se traza → lectura → rejilla de sus vinos (`#vinos`; «Ver los vinos» es el botón principal) → FAQ → cierre |
| `turbio` | `/vino-turbio/` | Cabecera → banda del grifo (con pin y scrub en ordenador) → lectura → rejilla (barril, pieza tipográfica + Faladoiro) → FAQ → cierre |
| `licores` | `/licores/` | Cabecera → rejilla de los 6 licores → lectura → cierre |
| `contacto` | `/contacto/` | Cabecera sin botones → tarifa (teléfono grande + formulario) → pie |

**Reglas de texto que reconoce:** las de Rayo (primer párrafo = entradilla; último H2 o `CTA_H2` = cierre; `## Preguntas frecuentes`
→ FAQ) más: H2 que empiezan por `PROVEEDOR_H2`, `PASOS_H2`, `CATALOGO_H2`, `CASA_H2`, `ZONA_H2` → sus piezas; en hubs, el H2
cuya lista enlaza a fichas → rejilla; listas «**[Nombre](/url/):** texto» → tarjetas con miniatura del producto.

## 3. Movimiento (nivel «como GYF»; números de la ficha de Jesper, con código propio)

| Pieza | Dónde | Cómo | Táctil / reducido |
|---|---|---|---|
| A1 Palabras del titular | `[data-palabras]` (H1) | yPercent 101 → 0, 0,9 s, power2.out, 0,06 s entre palabras. **Solo si la página carga rápido** (< 1,5 s hasta `tema.js`); si GSAP no llega en 2,5 s se muestra sin más (R2 de Rayo: el titular nunca se queda oculto) | Visible y quieto |
| E1 Paralaje de la portada | `[data-paralaje] img` | ±7 % con scrub (15 % en total, no el 30 % de la demo) | No |
| F1 La estantería | `[data-estanteria]` | Pin de la sección bajo la cabecera, la pista avanza `x = -(ancho pista − ancho ventana)` con scrub 1, `end = recorrido + 200` | Pista deslizable con `scroll-snap` (CSS), sin pin |
| El grifo del turbio | `[data-grifo]` | Pin +600 px bajo la cabecera; `[data-nivel]` scaleY 0 → 1 y el titular aparece línea a línea (`lineas()` agrupa palabras por `offsetTop`), todo con scrub | Banda quieta y llena; el titular aparece una vez (sin scrub) |
| Zoom de imagen | `[data-zoom]` | 1,15 → 1 al entrar (IntersectionObserver + CSS) | Sin zoom en reducido |
| J3 El racimo que se traza | `[data-traza]` (pie y cabeceras de D.O.) | `stroke-dasharray/offset` por trazado, 1,6 s, 0,12 s entre trazados, al entrar | Entero |
| R11 Texto que se enciende | `.enciende` (bloque partido) | El de Rayo (main.js) | Sin scrub |
| R14 Cinta | `.cinta--do` | La de Rayo (main.js), con la piel de Jesper (itálica, puntos) | Quieta |
| R18 Aparición | `.rv` | La de Rayo, 0,9 s | Visible |
| Botones | `.btn` | Barrido de relleno 0,4 s (Antra) + letras que ruedan (base) | Sin hover |

Se apagan a propósito (ficha de Jesper, «no se toma nunca»): cursor mágico, ruido, máscara, cortinas, cabecera que se esconde, opiniones pegajosas.

## 4. Fotos (cómo se prepararon; `08-WEB/herramientas-v1/preparar_fotos.py`)

- Botellas de la web vieja con fondo blanco (Castel de Fornos, Da Viña Galega, Terras Vellas, Torremorón): fondo y logo antiguo fuera → PNG con alfa (~200 × 760).
- Botellas de la web vieja con fondo desenfocado (Finca Lavandeira ×2, Roandi, Flavia, Alento, Bancales): recorte vertical 480 × 800 sin el logo antiguo (JPG). Salen en caja como foto, no como botella recortada.
- 15 botellas del catálogo en PDF (**PROVISIONALES**, marcadas en `catalogo.json`): tal cual, renombradas keyword-localidad; en la ficha llevan la etiqueta «foto provisional».
- Garrafas de licores (web vieja): recorte 500 × 800 sin el logo antiguo. La de la caja de la home: 800 × 800 con el logo tapado con la madera vecina.
- Ambiente: las de la maqueta del paso 21 (portada de banco de la web vieja ⚑, cuncas, almacén, furgoneta PROVISIONAL).
- Sin foto → pieza tipográfica (`pieza_tipografica()`): el barril de turbio.

## 5. Lo que se cambió en los textos al importarlos (y dónde queda constancia)

- Frases con ⚑ fuera (25), y toda mención al vodka caramelo y a «siete licores» (`contenido/NO-PUBLICADO.txt`).
- «7 licores» → «6 licores» en inicio, catálogo, nosotros y metas (vuelve a 7 si Álvaro mantiene el vodka).
- Dos metas de menos de 120 caracteres (turbio, ficha del barril) terminan en «Sin pedido mínimo.» (frase de PROMESAS).
- Legales: fuera las líneas pendientes del paso 6 (Registro Mercantil, alojamiento, proveedor de correo), «Última actualización: octubre de 2026 (versión 1, vista previa)», la cookie de consentimiento se llama `pousada-cookies` (almacenamiento local, sin caducidad), fuera los «[nuevo]» y las notas en cursiva.
- El formulario de /contacto/ es el de cinco campos de Dani (04-LEGALES/formulario-textos.md); la lista de siete campos de Merche no se publica.

## 6. Lo que queda provisional o pendiente (ver ESTADO.md)

GTM_ID vacío · CID de la ficha (sin mapa ni enlace a reseñas) · buzón `info@vinospousada.es` por confirmar (paso 44) · foto de portada de banco y furgoneta PROVISIONAL · 15 botellas del catálogo PROVISIONALES · sin reseñas (sección fuera) · racimo SVG reconstruido (si el cliente tiene el vector, se sustituye en `recursos/marca/`) · Lighthouse sin pasar · táctil real y Safari sin probar.
