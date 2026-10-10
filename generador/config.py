# -*- coding: utf-8 -*-
"""GYF · Tema 010-JESPER (sobre la base GYF-Rayo) · CONFIGURACIÓN DEL CLIENTE: Vinos Gallegos Pousada.
Es el ÚNICO archivo de Python que se toca para una web nueva (pasos 15-24 del protocolo v12).

Regla: ante cualquier discrepancia de datos manda la ficha de Google Business Profile (y PROMESAS.md para lo que se dice).
Marcadores que se rellenan solos en los textos: {pueblo}, {nombre}, {localidad}, {telefono}, {horario}, {horario_min},
{abre}, {cierra}, {anios}, {anios_marca}, {devuelve}.
"""

VERSION = "1"          # sube en cada entrega: estilo.css?v=VERSION y main.js?v=VERSION

# ---------- Sitio ----------
DOMINIO = "https://vinospousada.es"                                   # sin www (paso 18): la web vieja ya iba sin www
HOST_PRODUCCION = ("vinospousada.es", "www.vinospousada.es")          # GTM y cookies solo cargan aquí
GTM_ID = ""                                                            # ⚑ paso 7: contenedor heredado o nuevo; vacío = no carga GTM
COOKIES_CLAVE = "pousada-cookies"                                      # clave de localStorage del aviso (la cita la política de cookies)
COLOR_TEMA = "#FFFFFF"                                                 # <meta theme-color>: modo claro
CONTACTO_INDEXABLE = True

# Redirecciones de un solo salto (hoja 301 de arquitectura-pousada-paso-11.xlsx). URL vieja sin barra inicial → nueva.
REDIRECCIONES = [
    ("productos/pousada/licores/crema-orujo", "/licores/crema-de-orujo/"),
    ("productos/pousada/licores/pacharan-gallego", "/licores/pacharan-gallego/"),
    ("productos/pousada/licores/licor-cafe", "/licores/licor-de-cafe/"),
    ("productos/pousada/licores/aguardiente", "/licores/aguardiente-de-hierbas/"),
    ("productos/pousada/licores/orujo-blanco", "/licores/orujo-blanco/"),
    ("productos/pousada/licores/limoncino", "/licores/limoncino/"),
    ("productos/pousada/licores/vodka-caramelo", "/licores/"),          # ⚑ decide Álvaro: el vodka no se publica (David: «caramelo no tengo»)
    ("productos/pousada/licores", "/licores/"),
    ("productos/pousada/vinos-gallegos/ribeiro", "/denominaciones/ribeiro/"),
    ("productos/pousada/vinos-gallegos/rias-baixas", "/denominaciones/rias-baixas/"),
    ("productos/pousada/vinos-gallegos/valdeorras", "/denominaciones/valdeorras/"),
    ("productos/pousada/vinos-gallegos/monterrey", "/denominaciones/monterrei/"),
    ("productos/pousada/vinos-de-espana/ribera-duero", "/denominaciones/ribera-del-duero/"),
    ("productos/pousada/vinos-de-espana/rioja", "/denominaciones/rioja/"),
    ("productos/pousada/vinos-de-espana/rueda", "/denominaciones/rueda/"),
    ("productos/pousada/vinos-de-espana/navarra", "/catalogo/"),
    ("productos/pousada/vinos-gallegos", "/catalogo/"),
    ("productos/pousada/vinos-de-espana", "/catalogo/"),
    ("productos/pousada/page/2", "/catalogo/"),
    ("productos/pousada", "/catalogo/"),
    ("shop", "/catalogo/"),
    ("quienes-somos", "/nosotros/"),
    ("vino/turbio", "/vino-turbio/"),
    ("vino/trio", "/catalogo/"),
    ("comprar/rueda-verdejo-musgo", "/denominaciones/rueda/"),
    ("comprar/vina-sobreira", "/denominaciones/rias-baixas/"),       # ⚑ alternativa: Terras Vellas si David confirma la bodega
    ("comprar/vino-tinto-davalillo", "/denominaciones/rioja/"),
    ("comprar/vino-tinto-don-paulino-crianza", "/denominaciones/rioja/"),
    ("comprar/tapias-godello", "/denominaciones/monterrei/"),
]
REDIRECCIONES_302 = []

# ---------- Negocio (ficha de Google + DATOS-LEGALES.md + PROMESAS.md) ----------
NEGOCIO = {
    "nombre": "Vinos Gallegos Pousada",
    "nombre_corto": "Pousada",
    "nombre_largo": "Vinos Gallegos Pousada · Distribuidor de vinos gallegos, vino turbio y licores para hostelería",
    "razon_social": "VINOS GALLEGOS POUSADA S.L.",
    "cif": "B-81336315",
    "telefono": "666 631 615",
    "telefono_e164": "+34666631615",
    "whatsapp": "34666631615",
    "email": "info@vinospousada.es",
    "calle": "Calle Porto Colón, 12 (posterior), Local 11",   # ⚑ la ficha dice «C. Porto Colón, 12»: completar la ficha, no contradecirla
    "cp": "28924",
    "localidad": "Alcorcón",
    "provincia": "Madrid",
    "region": "Madrid",
    "horario_texto": "De lunes a viernes, de 8:00 a 20:00",   # ⚑ días por confirmar (PROMESAS); las horas las validó Álvaro el 07/10/2026
    "horario_corto": "L-V · 8:00-20:00",
    "dias_texto": "Lunes a viernes",
    "abre": "08:00", "cierra": "20:00",
    "dias_schema": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "zona_horaria": "Europe/Madrid",
    "festivos": [],                      # PROMESAS: festivos y vacaciones no se mencionan en la web
    "festivos_pascua": [],
    "valoracion": "0", "resenas": "0",   # sin reseñas reales: no hay sección de opiniones (FIRMA.md)
    "anios": "47",                       # desde 1979
    "anios_marca": "47",
    "garantia": None,
    "fundacion": "1979",
    "devuelve_llamada": "de 8 a 20 h",
    "cambia_equipos": None,
    "cid": "0",                          # ⚑ CID de la ficha de Google pendiente (paso 3): sin él no hay mapa ni enlace a reseñas
    "lat": 40.3459, "lng": -3.8298,      # ⚑ aproximado (Alcorcón); se sustituye por el del pin de la ficha (5 o más decimales)
    "geo_aproximado": True,              # mientras sea True (o el CID sea 0) el JSON-LD NO lleva geo ni hasMap (Matías L-04, Turing A2)
    "email_aviso": "",                   # ⚑ segundo buzón para un aviso corto por cada solicitud (el de Álvaro el primer mes); vacío = sin aviso
    "zona_servida": "Madrid",            # areaServed del JSON-LD: la provincia (AdministrativeArea «Madrid»); la sede (Alcorcón) va en address
    "schema_tipo": "WholesaleStore",     # distribuidor mayorista con local; subtipo de LocalBusiness
    "servicio_tipo": "Distribución de vinos y licores para hostelería",
    "precio": None,                      # sin precios en la web
    "pago": "Transferencia, Bizum, tarjeta y efectivo",
    "knows_about": ["Vinos gallegos", "Vino turbio", "D.O. Rías Baixas", "D.O. Ribeiro", "D.O. Valdeorras", "D.O. Monterrei",
                    "Licores gallegos", "Distribución a hostelería"],
    "persona": None,                     # sin Person en el JSON-LD: el cliente no quiere su nombre en la web (David, 09/10/2026); el apellido nunca tuvo fuente
}

# Fuentes que se precargan (recursos/fuentes/<familia>-latin-<peso>-<estilo>.woff2 → /fuentes/<familia>-<peso>[-italic].woff2).
FUENTES_PRECARGA = ["fraunces-500.woff2", "instrument-sans-400.woff2"]

# ---------- Marca (archivos en recursos/marca/) ----------
MARCA = {
    "simbolo": "simbolo-color.svg",      # racimo (trazo): sprite, viñetas, pie
    "simbolo_blanco": "simbolo-blanco.svg",
    "logo": None,                        # None = la cabecera compone racimo + nombre en HTML (FIRMA §1.4); con SVG apaisado, su nombre
    "logo_ancho": 44, "logo_alto": 48,
    "logo_blanco": None,
    "logo_texto": ("Vinos gallegos", "Pousada"),   # antetítulo y nombre que acompañan al racimo
    "og": "og-image-1200x630.jpg",
}

# ---------- Objeto de portada (Rayo). Pousada no lleva objeto: portada tipográfica + foto en caja ----------
OBJETO_PORTADA = {"tipo": None, "imagen": None, "en_banda": False}

# Portada de la home · v2 (Jean Paul, paso 36, Anexo A de 05-JEAN-PAUL-DISENO.md + encargo de Álvaro del 09/10/2026):
# campo de color con la Praia das Catedrais lavada (blanco y negro teñido de la marca, recursos/fotos/, hecha con lavar.py
# a partir de 03-FOTOS/01-ORIGINALES/web-vieja-completa/2020/06/02-playas-galicia.jpg, 2048×1162), cinco botellas limpias
# que se salen por abajo y un cierre en onda («marea»), no un rectángulo. Sin foto en caja y sin paralaje.
PORTADA = {
    "foto": "paisaje-praia-das-catedrais-lavado.jpg",   # recursos/fotos/ · decorativa (alt vacío) · ⚑ licencia de la foto de banco por confirmar
    "alt": "",
    "botellas": ["terras-vellas-albarino-rias-baixas.png", "da-vina-galega-albarino-rias-baixas.png", "don-indalecio-verdejo-rueda.png",
                 "castel-de-fornos-albarino-rias-baixas.png", "penalagua-tinto-joven-ribera-del-duero.png"],   # recursos/producto/, sin defectos visibles; en móvil salen las 3 primeras
    "onda": "marea",
    "confianza": "Sin pedido mínimo · De lunes a viernes, de 8 a 20 h · Fuera de horario, cogemos el móvil",   # sin nombres (David, 09/10/2026)
}

# Cabeceras interiores · v2 (Jean Paul M-2 + encargo de Álvaro): la primera pantalla de cada tipo de página lleva imagen o
# pieza propia y el mismo cierre de onda (otra variante por tipo). Claves: el tipo de página (datos.tipo_de) o la URL.
#   fondo:  paisaje lavado de recursos/fotos/ que se funde detrás (o None)
#   pieza:  ("botellas", [archivos de recursos/producto/ con alfa]) · ("arco", archivo de recursos/fotos/, alt) · ("palabras", [...]) ·
#           ("cunca", foto de recursos/fotos/, alt, botella con alfa) · "botellas_do" (las de DENOMINACION_BOTELLAS) · None
#   tinte:  color del campo (las D.O. usan el suyo de DENOMINACIONES) · onda: variante de plantilla.ONDAS · siguiente: fondo del bloque de debajo
CABECERAS = {
    "catalogo":     {"fondo": "paisaje-uvas-lavado.jpg", "pieza": ("botellas", ["torremoron-tinto-joven-ribera-del-duero.png", "castel-de-fornos-albarino-rias-baixas.png", "don-indalecio-verdejo-rueda.png", "terras-vellas-albarino-rias-baixas.png"]), "tinte": "#EAF5F3", "onda": "ola"},
    "denominacion": {"fondo": "paisaje-vinedo-lavado.jpg", "pieza": "botellas_do", "onda": "ola"},
    "turbio":       {"fondo": None, "pieza": ("cunca", "vino-turbio-gallego-cunca-ribadavia.jpg", "Cunca de vino turbio sobre una barra de mármol", "faladoiro-vino-turbio-ribadavia.png"), "tinte": "#E4F3F1", "onda": "marea", "siguiente": "var(--oscuro)"},
    "licores":      {"fondo": None, "pieza": ("arco", "licores-gallegos-garrafa-3-litros-hosteleria.jpg", "Garrafa de 3 litros de crema de orujo Pousada"), "tinte": "#F4F2EC", "onda": "costa"},
    "servicio":     {"fondo": "paisaje-praia-das-catedrais-lavado.jpg", "pieza": ("arco", "vino-turbio-gallego-cuncas-mesa.jpg", "Cuncas de vino turbio sobre una mesa de madera"), "tinte": "#F4F2EC", "onda": "ola"},
    "/distribuidor-vinos-hosteleria-madrid/": {"fondo": "paisaje-praia-das-catedrais-lavado.jpg", "pieza": ("palabras", ["Alcorcón", "Móstoles", "Leganés", "Getafe", "Fuenlabrada", "Pozuelo", "Alcalá", "Madrid"]), "tinte": "#F4F2EC", "onda": "costa"},
    "/distribuidor-vinos-hosteleria-alcorcon/": {"fondo": None, "pieza": ("arco", "almacen-vinos-pousada-alcorcon.jpg", "Almacén de Vinos Gallegos Pousada en Alcorcón, con palés de cajas de vino"), "tinte": "#F4F2EC", "onda": "ribera"},
    "empresa":      {"fondo": "paisaje-praia-das-catedrais-lavado.jpg", "pieza": ("arco", "almacen-vinos-pousada-alcorcon.jpg", "Almacén de Vinos Gallegos Pousada en Alcorcón, con palés de cajas de vino"), "tinte": "#F4F2EC", "onda": "costa"},
    "contacto":     {"fondo": "paisaje-praia-das-catedrais-lavado.jpg", "pieza": None, "tinte": "#F4F2EC", "onda": "ribera"},
    "ficha":        {"fondo": None, "pieza": "producto", "tinte": "#F4F2EC", "onda": "ribera"},   # el tinte real es el de su D.O.
    "licor":        {"fondo": None, "pieza": "producto", "tinte": "#F4F2EC", "onda": "ribera"},
}
# Botellas (con alfa y sin defectos a tamaño medio) que asoman en la cabecera de cada D.O.; 1 a 3 por hub
DENOMINACION_BOTELLAS = {
    "rias-baixas": ["castel-de-fornos-albarino-rias-baixas.png", "terras-vellas-albarino-rias-baixas.png", "da-vina-galega-albarino-rias-baixas.png"],
    "ribeiro": ["gran-lavandeira-treixadura-ribeiro.png", "lagar-de-san-blas-blanco-ribeiro.png"],
    "valdeorras": ["lagar-de-cigur-godello-valdeorras.png", "camino-das-estrelas-blanco-valdeorras.png"],
    "monterrei": ["aunios-godello-monterrei.png"],
    "bierzo": ["quinta-grande-godello-bierzo.png"],
    "rueda": ["don-indalecio-verdejo-rueda.png"],
    "ribera-del-duero": ["penalagua-tinto-joven-ribera-del-duero.png", "torremoron-tinto-joven-ribera-del-duero.png"],
    "rioja": ["geron-crianza-rioja.png", "geron-joven-tinto-rioja.png"],
}

# ---------- Estructura de URLs (paso 22) ----------
URLS = {
    "hub": None,
    "municipio": "/distribuidor-vinos-hosteleria-",   # zonas: Madrid (provincia) y Alcorcón (sede)
    "marca": None,
    "empresa": "/nosotros/",
    "contacto": "/contacto/",
    "servicio": "/distribuidor-vinos-gallegos-hosteleria/",
    "catalogo": "/catalogo/",
    "ficha": "/comprar/",
    "denominacion": "/denominaciones/",
    "turbio": "/vino-turbio/",
    "licores": "/licores/",
}
MUNICIPIOS = [("/distribuidor-vinos-hosteleria-madrid/", "provincia de Madrid"), ("/distribuidor-vinos-hosteleria-alcorcon/", "Alcorcón")]
PREFIJOS_MUNICIPIO = ["Distribuidor de vinos para hostelería en"]
MUNICIPIO_ANCLA = "Reparto en {pueblo}"
# Municipios que se citan en la zona de reparto (PROMESAS: toda la provincia; estos son los de la orden de Álvaro)
REPARTO_MUNICIPIOS = ["Madrid", "Alcorcón", "Móstoles", "Leganés", "Getafe", "Fuenlabrada", "Pozuelo de Alarcón", "Alcalá de Henares"]
REPARTO_FOTO = ("furgoneta-reparto-vinos-madrid-PROVISIONAL.jpg", "Furgoneta de reparto de Vinos Gallegos Pousada delante de la sede de Alcorcón")  # ⚑ PROVISIONAL

# Denominaciones (hubs): clave → (nombre, uva o tipo que la define, descripción corta para rejillas, tinte de fondo)
DENOMINACIONES = {
    "rias-baixas": ("Rías Baixas", "Albariño", "Albariños del Salnés y de Ulla, para pescado, marisco y entrantes fríos", "#EEF5E9"),
    "ribeiro": ("Ribeiro", "Treixadura", "Treixadura, blancos jóvenes y un tinto de la zona de Ribadavia", "#F3F1E4"),
    "valdeorras": ("Valdeorras", "Godello y mencía", "Godellos de ladera y mencías con barrica", "#F5EDEA"),
    "monterrei": ("Monterrei", "Godello", "Godello de la D.O. más al sur de Galicia", "#F0F3EA"),
    "bierzo": ("Bierzo", "Godello", "Godello de la zona del Bierzo, vinos de Castilla y León", "#F2EFE9"),
    "rueda": ("Rueda", "Verdejo", "Verdejo seco y fresco para el aperitivo y la barra", "#F1F4E6"),
    "ribera-del-duero": ("Ribera del Duero", "Tinto joven", "Tempranillo joven para carnes y asados", "#F6ECEA"),
    "rioja": ("Rioja", "Crianza y joven", "Tempranillo y garnacha, en crianza y en joven", "#F6EDEA"),
}
DENOMINACION_ETIQUETA = "D.O. {nombre}"   # etiqueta de la cabecera de cada hub
# Bierzo no es una D.O. para este producto (Quinta Grande es «vino de Castilla y León · zona del Bierzo», sin sello D.O.):
# estas claves usan «Zona de {nombre}» en vez de «D.O. {nombre}» en cabeceras y antetítulos (paso 38, Bruno N-2).
DENOMINACIONES_SIN_DO = {"bierzo"}

# La estantería de la home (pieza clavada que avanza de lado): una entrada por hub, en este orden.
# (url, título, subtítulo, foto de recursos/producto/ o None, oscura)
ESTANTERIA = [
    ("/denominaciones/rias-baixas/", "Rías Baixas", "Albariño", "castel-de-fornos-albarino-rias-baixas.png", False),
    ("/denominaciones/ribeiro/", "Ribeiro", "Treixadura", "gran-lavandeira-treixadura-ribeiro.png", False),
    ("/denominaciones/valdeorras/", "Valdeorras", "Godello y mencía", "camino-das-estrelas-blanco-valdeorras.png", False),
    ("/denominaciones/monterrei/", "Monterrei", "Godello", "aunios-godello-monterrei.png", False),
    ("/denominaciones/bierzo/", "Bierzo", "Godello", "quinta-grande-godello-bierzo.png", False),
    ("/denominaciones/rueda/", "Rueda", "Verdejo", "don-indalecio-verdejo-rueda.png", False),
    ("/denominaciones/ribera-del-duero/", "Ribera del Duero", "Tintos jóvenes", "penalagua-tinto-joven-ribera-del-duero.png", False),
    ("/denominaciones/rioja/", "Rioja", "Crianza y joven", "geron-crianza-rioja.png", False),
    ("/vino-turbio/", "Vino turbio", "Barril de 50 litros", "faladoiro-vino-turbio-ribadavia.png", True),
    ("/licores/", "Licores Pousada", "Garrafa de 3 litros", "crema-de-orujo-gallega-garrafa-3-litros.jpg", False),
]
ESTANTERIA_ETIQUETA = "{n_vinos} vinos y {n_licores} licores"   # cifras que cuenta el generador (fichas publicadas), nunca fijas (David, 09/10/2026)
ESTANTERIA_NOTA = "Ordenados por origen. Cada entrada lleva a sus fichas."
CINTA_PORTADA = ["Rías Baixas", "Ribeiro", "Valdeorras", "Monterrei", "Bierzo", "Rueda", "Ribera del Duero", "Rioja", "Vino turbio", "Licores Pousada"]
CINTA_SECUNDARIA = None

# Caja del catálogo en la home (2/3): tres botellas que se asoman
CATALOGO_HOME_BOTELLAS = ["torremoron-tinto-joven-ribera-del-duero.png", "da-vina-galega-albarino-rias-baixas.png", "castel-de-fornos-albarino-rias-baixas.png"]
TURBIO_FOTO = ("vino-turbio-gallego-cunca-ribadavia.jpg", "Cunca de vino turbio sobre una barra de mármol")
TURBIO_FOTO_BANDA = ("vino-turbio-gallego-cuncas-mesa.jpg", "Cuncas de vino turbio sobre una mesa de madera")
LICORES_FOTO = ("licores-gallegos-garrafa-3-litros-hosteleria.jpg", "Garrafa de 3 litros de crema de orujo Pousada")
CASA_FOTO = ("almacen-vinos-pousada-alcorcon.jpg", "Almacén de Vinos Gallegos Pousada en Alcorcón, con palés de cajas de vino", "El almacén, en Alcorcón")
CASA_HITOS = [("1979", "Se funda en Alcorcón"), ("Hoy", "Sigue en la familia")]   # sin generaciones ni nombres fuera de Nosotros (David, 09/10/2026)

# Banda oscura «El grifo del turbio» (pieza del motivo del cliente, FIRMA §4). La palabra en --turbio va entre *cursivas*.
GRIFO = {
    "etiqueta": "El producto de la casa",
    "titulo": "Vino turbio gallego, *muy frío y de grifo*",
    "texto": "De la zona de Ribadavia, en barril de 50 litros, porque es lo que piden en hostelería. Sigue siendo uno de los productos de la casa.",   # sin «con serpentín» ni padre de David, sin explicar el sistema (David, 09/10/2026)
    "boton": ("Ver el vino turbio", "/vino-turbio/"),
}

# Menú (barra horizontal en ordenador; capa a pantalla completa en móvil). Sin listas: el pie lleva las columnas.
MENU = [
    ("Hostelería", "/distribuidor-vinos-gallegos-hosteleria/"),
    ("Catálogo", "/catalogo/"),
    ("Vino turbio", "/vino-turbio/"),
    ("Licores", "/licores/"),
    ("Nosotros", "/nosotros/"),
    ("Contacto", "/contacto/"),
]
MENU_BOTON = ("Solicitar tarifa", "/contacto/")

NOMBRE_CORTO = {
    "/": "Inicio",
    "/distribuidor-vinos-gallegos-hosteleria/": "Hostelería",
    "/distribuidor-vinos-hosteleria-madrid/": "Provincia de Madrid",
    "/distribuidor-vinos-hosteleria-alcorcon/": "Alcorcón",
    "/catalogo/": "Catálogo",
    "/vino-turbio/": "Vino turbio",
    "/licores/": "Licores",
    "/nosotros/": "Nosotros",
    "/contacto/": "Contacto",
}

# Columnas del pie (FIRMA §2): Vinos · Empresa · Contacto (la pone el tema) · Legal (LEGALES)
PIE_COLUMNAS = [
    ("Vinos", [("Catálogo", "/catalogo/")] + [(n, f"/denominaciones/{k}/") for k, (n, _, _, _) in DENOMINACIONES.items()] + [("Vino turbio", "/vino-turbio/"), ("Licores", "/licores/")]),
    ("Empresa", [("Distribución para hostelería", "/distribuidor-vinos-gallegos-hosteleria/"), ("Provincia de Madrid", "/distribuidor-vinos-hosteleria-madrid/"),
                 ("Sede en Alcorcón", "/distribuidor-vinos-hosteleria-alcorcon/"), ("Nosotros", "/nosotros/"), ("Contacto", "/contacto/")]),
]

# Pie por página (tabla de llamadas a la acción de Dani, FIRMA §5): url → (pregunta del lector, titular ≤ 5 palabras, botón principal, botón secundario)
# Botones: "tarifa" (→ /contacto/), "llamar" (tel:), "whatsapp" (wa.me), ("texto", "/url/") para otros.
PIE_FRASES = {
    "/": ("¿Me sirve este proveedor para mi local?", "Pida su tarifa", "tarifa", "llamar"),
    "/distribuidor-vinos-gallegos-hosteleria/": ("¿Cómo empiezo a trabajar con ellos?", "Solicite su tarifa", "tarifa", "llamar"),
    "/distribuidor-vinos-hosteleria-madrid/": ("¿Reparten en mi municipio?", "Repartimos en su municipio", "llamar", "tarifa"),
    "/distribuidor-vinos-hosteleria-alcorcon/": ("¿Con quién hablo?", "Hable con nosotros", "llamar", "whatsapp"),   # sin nombres (David, 09/10/2026)
    "/catalogo/": ("¿Cómo pido lo que he visto?", "El pedido se hace con nosotros", "tarifa", "llamar"),
    "/vino-turbio/": ("¿Me compensa poner el barril?", "Pida la tarifa del turbio", ("Solicitar tarifa del turbio", "/contacto/?interes=vino-turbio"), "llamar"),
    "/licores/": ("¿Lo añado al mismo pedido?", "Añádalos al mismo pedido", ("Solicitar tarifa", "/contacto/?interes=licores"), "llamar"),
    "/nosotros/": ("¿Es gente seria?", "Trabaje con la casa", "llamar", "tarifa"),
    "/contacto/": ("¿Qué pasa cuando envío esto?", "Le respondemos de 8 a 20 h", "llamar", "whatsapp"),
}
# Plantillas por tipo de página (las fichas y los hubs son muchos): {nombre} = nombre del producto o de la D.O.
PIE_FRASES_TIPO = {
    "ficha": ("¿Lo quiero en mi carta?", "Pida la tarifa de este vino", ("Solicitar tarifa", "/contacto/?interes={slug}"), "whatsapp"),
    "licor": ("¿Lo añado al mismo pedido?", "Pida la tarifa de este licor", ("Solicitar tarifa", "/contacto/?interes={slug}"), "whatsapp"),
    "denominacion": ("¿Qué vinos de esta zona me encajan?", "Pida la tarifa de esta zona", ("Solicitar tarifa", "/contacto/?interes=vinos"), "llamar"),
}
PIE_SUB = "Cuéntenos qué tipo de local tiene y qué le interesa: vinos, turbio, licores. Le atendemos de lunes a viernes, de 8 a 20 h."

# Formulario (04-LEGALES/formulario-textos.md): cinco campos, sin casilla, línea informativa (versión corta) y confianza
FORMULARIO = {
    "tipos_negocio": ["Bar", "Restaurante", "Tienda", "Particular"],
    "intereses": {"vinos": "vinos gallegos", "vino-turbio": "vino turbio", "licores": "licores"},   # ?interes=… → mensaje prerrelleno; un slug de producto → su nombre
    "boton": "Enviar solicitud de tarifa",
    "confianza": "Sin pedido mínimo · De 8 a 20 h · Fuera de horario, cogemos el móvil",   # sin nombres (David, 09/10/2026)
    "confianza_particular": "Para particulares, el mínimo es una caja.",
    "informativa": "Sus datos los usa VINOS GALLEGOS POUSADA S.L. solo para responder a su solicitud (art. 6.1.b RGPD) y los guarda como máximo un año. Derechos en info@vinospousada.es · ",
    # Confirmación (Dani C-16): sin nombres y sin plazo que PROMESAS.md no respalde (solo el horario de 8 a 20 h); con siguiente paso
    "ok_titulo": "Solicitud recibida",
    "ok_texto": "Gracias. Le contestamos en horario de 8 a 20 h. Si tiene prisa, llame o escriba por WhatsApp al 666 631 615.",
    "ok_enlace": ("Mientras tanto, vea el catálogo", "/catalogo/"),
    "error_titulo": "No hemos podido enviar su solicitud",
    "error_texto": "Ha fallado el envío. Sus datos no se han perdido: pruebe de nuevo en unos segundos o, si lo prefiere, llámenos o escríbanos por WhatsApp al 666 631 615, o por correo a info@vinospousada.es.",
    # Mensajes concretos por motivo (Dani C-03): enviar.php devuelve ?enviado=0&motivo=<clave> y main.js pone el texto
    "errores": {
        "nombre": "Falta su nombre. Escríbalo y vuelva a enviar; lo demás se ha conservado.",
        "telefono": "Revise el teléfono: tiene que tener 9 cifras, por ejemplo 666 631 615 (vale con +34, espacios, puntos o guiones).",
        "negocio": "Falta el nombre de su bar, restaurante o tienda.",
        "tipo_negocio": "Elija el tipo de negocio: bar, restaurante, tienda o particular.",
        "enlaces": "El mensaje no puede llevar enlaces ni direcciones web. Quítelos y vuelva a enviar.",
    },
    # Teléfono: patrón válido en Chrome (modo «v»: paréntesis, punto y guion escapados), +34 opcional, de 9 a 15 cifras con separadores
    "telefono_patron": r"\+?[0-9]([ .\-\(\)]?[0-9]){8,14}",
    "telefono_title": "Escriba un teléfono de 9 cifras, por ejemplo 666 631 615",
    "telefono_ph": "Para llamarle o escribirle",
    "negocio_ph": "Nombre de su local",
    "trampa": "contacto_alt",            # campo trampa antispam: nombre sin sentido para que ningún gestor de contraseñas lo rellene (Dani C-02)
    "buzon": "info@vinospousada.es",     # ⚑ confirmar en el paso 44 (buzón de destino, paso 6)
}

# Qué piezas de Rayo se usan en Pousada
OPINIONES_SECCION = False      # sin reseñas reales → fuera (FIRMA.md). resenas.json queda vacío y controles.py no avisa
CASOS = []                      # sin galería de casos
CASOS_VER = ""
CIFRAS = []
CIFRAS_EN = {}
SERVICIOS_HOME = []
SERVICIOS_SECCION = False
SERVICIOS_TITULO = SERVICIOS_TEXTO = ""
PASOS_ICONOS = []
ICONO_URL = {}
PIE_ESTILO = "oscuro"           # «oscuro» (frase por página + columnas, Jesper/Solvento) · «tarjetas» (tres tarjetas de Rayo)
CAB_ESTILO = "barra"            # «barra» (menú horizontal en ordenador + capa en móvil, Jesper) · «capa» (solo capa, Rayo)
MAPA_SECCION = False            # ⚑ sin CID y sin decidir si se enseña la dirección: el mapa no sale

# Secciones del texto que el tema reconoce por el principio de su H2
CTA_H2 = r"^(Pida |Pide |Solicite |Para su carta|Para su local|Hable con|Cómo pedir|Cómo se pide|Lo que nos mueve)"
CTA_ULTIMO = True               # el último H2 de cada página es el cierre (texto antes del pie)
ZONA_H2 = "Reparto en toda la provincia"   # tras esta sección en la home: píldoras de municipios + foto de reparto
HORARIO_H2 = "Horario"
CASA_H2 = "Una casa familiar"   # sección de la home con la foto del almacén y los hitos
CATALOGO_H2 = "Vinos gallegos, vino turbio y licores"   # sección de la home que se pinta como caja 2/3 + 1/3
PROVEEDOR_H2 = "Un proveedor al que se le puede llamar"  # bloque partido con el texto que se enciende
PASOS_H2 = "Cómo trabajamos"    # lista numerada 01-05 con filete

# PROMESAS.md, columna «no se dice nunca»: controles.py da ERROR si alguna aparece en la web (expresiones regulares)
NO_SE_DICE = [r"(?<!no hay )(?<!ni se )(?<!sin )(?<!no se )compr[ae] online", r"añad[ai]r? al carrito", r"env[ií]os? a (toda )?España", r"env[ií]os? a domicilio", r"s[ií]ganos en",
              r"desde 1995", r"precio por pal[eé]", r"vodka caramelo", r"Navarra", r"70 cl"]

CTA_EXTRA = None
CREDITO = ("El Gordo y el Flaco", "https://elgordoyelflaco.es/")

LEGALES = [
    ("Aviso legal", "/aviso-legal/"),
    ("Política de privacidad", "/politica-de-privacidad/"),
    ("Política de cookies", "/politica-de-cookies/"),
]

CONTACTO_YA = {"Teléfono", "Horario", "Email", "Correo", "Otras formas de contacto"}
BANDA_TIT = {}

# ---------- Textos del tema ----------
TEXTOS = {
    "oficio": "distribución de vinos",
    "logo_alt": "{nombre} · Distribuidor de vinos gallegos en Alcorcón",
    "whatsapp_saludo": "Hola, escribo desde la web de Vinos Pousada",
    "whatsapp_pueblo": " (desde {pueblo})",
    "whatsapp_producto": ", me interesa {producto}",   # el mensaje prerrelleno lleva el nombre del vino en las fichas (paso 38, punto 16)
    "etiqueta_portada": "Vinos Gallegos Pousada · Alcorcón",
    "corta_municipio": "Vinos gallegos, vino turbio y licores para la hostelería de {pueblo}. Sin pedido mínimo.",
    "corta": "Vinos gallegos, vino turbio y licores para bares y restaurantes de la provincia de Madrid. Sin pedido mínimo.",
    "tarjeta_titulo": "¿Prefiere que le llamemos?",
    "tarjeta_ir": "Déjenos su teléfono",
    "llamada_titulo": "Déjenos su nombre y su teléfono",
    "llamada_promesa": "Le llamamos de 8 a 20 h.",
    "llamada_ok": "Recibido. Le llamamos {devuelve}; si es fuera de ese horario, en cuanto empecemos.",
    "llamada_boton": "Que me llamen",
    "promesa_abierto": "Le llamamos hoy mismo.",
    "promesa_antes": "Le llamamos hoy a partir de las {abre}.",
    "promesa_siguiente": "Le llamamos {dia} a partir de las {abre}.",
    "declara_etiqueta": "Trato directo",
    "indice_titulo": "En esta página",
    "indice_llamar": "¿Lo hablamos?",
    "opiniones_etiqueta": "", "opiniones_titular": "", "opiniones_sello": "", "resenas_ficha": "",
    "faq_etiqueta": "Dudas habituales",
    "faq_titulo": "Preguntas frecuentes",
    "faq_cta": "¿No está su pregunta? Llámenos",
    "cifras_etiqueta": "", "cifras_titulo": "", "cifras_fecha": "",
    "zona_titulo": "Zona de reparto",
    "zona_etiqueta": "Zona de reparto",
    "zona_resto": "y el resto de la provincia",
    "mapa_titular": "Nuestra sede, en {localidad}",
    "mapa_texto": "La web no es una tienda: llame o escriba antes de acercarse.",
    "privacidad_llamada": "Usamos sus datos solo para llamarle.",
    "privacidad_form": "Usamos sus datos solo para contestarle.",
    "form_ok": "Solicitud recibida. Le respondemos de 8 a 20 h.",
    "form_confianza": "Sin pedido mínimo · De 8 a 20 h · Fuera de horario, cogemos el móvil",
    "form_municipio_ph": "",
    "form_mensaje_label": "Mensaje",
    "form_mensaje_ph": "Qué le interesa: vinos gallegos, vino turbio, licores. Su municipio.",
    "form_boton": "Enviar solicitud de tarifa",
    "contacto_horario_extra": "Fuera de horario, cogemos el móvil.",
    "contacto_etiqueta": "Hable con nosotros",
    "contacto_tambien": "También por WhatsApp, en el mismo número",
    "banda_etiqueta": "", "banda_titulo": "", "banda_texto": "",
    "estado_abierto": "Abierto ahora · hasta las {cierra}",
    "estado_fuera": "Ahora cerrado · de 8 a 20 h",
    "pie_titular": "Pida su tarifa",
    "pie_etiqueta_contacto": "Contacto",
    "pie_tambien_whatsapp": "(también WhatsApp)",
    "pie_legal_titulo": "Legal",
    "catalogo_filtro_todo": "Todos",
    "catalogo_filtro_do": "Por denominación",
    "catalogo_filtro_tipo": "Por tipo",
    "catalogo_sin_do": "Vinos sin denominación",
    "catalogo_turbio": "Vino turbio",
    "catalogo_licores": "Licores y aguardientes",
    "ficha_datos": "Ficha",
    "ficha_tambien": "También le puede interesar",
    "ficha_tarifa_titulo": "Pida la tarifa de {nombre}",
    "ficha_tarifa_texto": "Esta web no vende por internet. Díganos su local y le pasamos el precio de esta referencia y del resto del catálogo.",
    "ficha_sin_foto": "Foto pendiente",
    "do_vinos_titulo": "Los vinos de {nombre}",
    "do_ver_todos": "Ver todo el catálogo",
    "licores_lista_titulo": "Los licores de la casa",
    "error_texto": "Puede que el enlace esté mal o que la página haya cambiado de sitio. Llámenos y lo vemos.",
    "llms_titulo": "# {nombre} · Distribuidor de vinos gallegos para hostelería en Madrid",
    "llms_resumen": "Distribuidor de vinos gallegos, vino turbio y licores para bares y restaurantes de toda la provincia de Madrid, con sede en Alcorcón. Sin pedido mínimo. La web no vende por internet: se pide la tarifa.",
    "llms_horario_extra": "Fuera de horario, cogemos el móvil.",
    "llms_datos": ["- Reparto: toda la provincia de Madrid. Desde cajas hasta palés. Sin pedido mínimo.",
                   # El turbio (barril de 50 litros y botella) va DENTRO de {n_vinos}, no como tercera categoría aparte
                   # de los vinos (paso 38 v3, Turing N4 arrastrado 2 vueltas): misma redacción que ya usa /catalogo/.
                   "- Catálogo: {n_vinos} vinos (Rías Baixas, Ribeiro, Valdeorras, Monterrei, Bierzo, Rueda, Ribera del Duero, Rioja, blancos sin D.O. e incluido el vino turbio en barril de 50 litros) y {n_licores} licores en garrafa de 3 litros. La selección cambia con la temporada.",
                   "- Fundada en 1979 en Alcorcón."],   # sin cifra fija ni padre/abuelo/David (David, 09/10/2026)
    "llms_no_hace": ["- No vende por internet ni publica precios: la tarifa se pide por el formulario, por teléfono o por WhatsApp.",
                     "- No envía fuera de la provincia de Madrid."],
    "llms_no_instala": "",
}
LLMS_PRINCIPALES = ["/", "/distribuidor-vinos-gallegos-hosteleria/", "/catalogo/", "/vino-turbio/", "/licores/", "/nosotros/", "/contacto/"]
LLMS_MARCAS = []


def texto(clave, **extra):
    """Devuelve TEXTOS[clave] con los marcadores rellenos."""
    N = NEGOCIO
    pe = N.get("persona") or {}
    cred = (pe.get("credenciales") or [("", "")])[0][1] or f"{N['anios']} años en el oficio"
    v = dict(nombre=N["nombre"], localidad=N["localidad"], telefono=N["telefono"], horario=N["horario_texto"],
             horario_min=N["horario_texto"][0].lower() + N["horario_texto"][1:], anios=N["anios"],
             anios_marca=N["anios_marca"], abre=N["abre"].lstrip("0"), cierra=N["cierra"].lstrip("0"),
             garantia=N["garantia"] or "", valoracion=N["valoracion"], resenas=N["resenas"], credencial=cred,
             pueblo=N["localidad"], devuelve=N.get("devuelve_llamada") or "en cuanto podamos")
    v.update(extra)
    v["PUEBLO"] = v["pueblo"].upper()
    return TEXTOS[clave].format(**v)


# Nota y número de reseñas: viven en contenido/resenas.json (en la web, /resenas.json). Pousada: vacío hasta tener reales.
import json as _json, os as _os
_R = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "contenido", "resenas.json"), encoding="utf-8"))
NEGOCIO["valoracion"] = str(_R.get("valoracion", "0"))
NEGOCIO["resenas"] = str(_R.get("resenas", 0))
OPINIONES = _R.get("opiniones", [])
FICHA = f"https://maps.google.com/?cid={NEGOCIO['cid']}" if NEGOCIO["cid"] not in ("0", "") else "/contacto/"
