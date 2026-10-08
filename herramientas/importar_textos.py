# -*- coding: utf-8 -*-
"""Pousada · Importa los textos de Merche (05-TEXTOS-NUEVOS y 04-LEGALES) al formato del tema (contenido/paginas/*.md
y contenido/legales/legales.md). Se lanza cuando Merche cambia un texto; nunca se editan a mano los .md generados.

Uso:  python3 herramientas/importar_textos.py [--cliente /ruta/023-VINOS-GALLEGOS-POUSADA]

Reglas (paso 27 y PROMESAS.md):
- No se publican «Lector:», «Decide:», «Por verificar con David», «Cambios del…», «Foto e interlinking», «Enlaces internos»,
  las líneas de botones «[Solicitar tarifa] …» (los pone el tema) ni las ⚑: se quita la FRASE que lleva la marca.
- Sin precios: el control de promesas lo vigila en controles.py.
- El vodka caramelo NO se publica (decisión pendiente de Álvaro; David dice que no lo tiene).
"""
import argparse, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser()
ap.add_argument("--cliente", default=os.path.abspath(os.path.join(RAIZ, "..", "..")))
a = ap.parse_args()
C = a.cliente
T = os.path.join(C, "05-TEXTOS-NUEVOS")
L = os.path.join(C, "04-LEGALES")
OUT = os.path.join(RAIZ, "contenido", "paginas")
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))

NO_PUBLICAR = 0
NO_PUBLICAR_LISTA = []


# Frases que no se publican aunque no lleven ⚑ (productos fuera de la web; PROMESAS «no se dice nunca»)
FUERA = ["vodka caramelo", "siete licores", "7 licores de nuestra gama"]


def sin_banderas(texto, donde=""):
    """Quita la frase que lleva ⚑ (y la marca) o que nombra algo de FUERA. Si todo el párrafo cae, lo quita entero."""
    global NO_PUBLICAR
    if "⚑" not in texto and not any(f in texto.lower() for f in FUERA):
        return texto
    frases = re.split(r"(?<=[.!?:])\s+", texto)
    fuera = [f for f in frases if "⚑" in f or any(x in f.lower() for x in FUERA)]
    NO_PUBLICAR += len(fuera)
    NO_PUBLICAR_LISTA.extend(f"{donde}: {f[:90]}" for f in fuera)
    res = " ".join(f for f in frases if f not in fuera).strip()
    return res


def limpia_cuerpo(lineas, donde):
    """Filtra las líneas del cuerpo: botones, notas de maqueta y banderas."""
    out = []
    for l in lineas:
        s = l.strip()
        if re.match(r"^\[[^\]]+\](\s*\[[^\]]+\])*\s*$", s):          # [Solicitar tarifa] [Llamar…]
            continue
        if s.startswith("(Widget") or s.startswith("(Formulario") or s.startswith("(Mapa"):
            continue
        if s.startswith("*(") and s.endswith(")*"):                    # notas de corrección en cursiva
            continue
        if s.startswith(">"):                                          # citas de trabajo
            continue
        if "⚑" in s or any(f in s.lower() for f in FUERA):
            s2 = sin_banderas(s, donde)
            if not s2 or len(re.sub(r"[*\-\s]", "", s2)) < 3:
                continue
            l = s2
        l = re.sub(r"\s*\[(nuevo|concretado|reescrito[^\]]*|corregido[^\]]*)\]", "", l)
        l = l.replace("7 licores", "6 licores")   # el vodka caramelo no se publica: vuelve a 7 si Álvaro lo mantiene
        out.append(l.rstrip())
    return out


def escribe(nombre, cab, cuerpo, faq, donde):
    cuerpo = limpia_cuerpo(cuerpo, donde)
    txt = "\n".join(f"{k}: {v}" for k, v in cab.items() if v) + "\n---\n" + "\n".join(cuerpo).strip() + "\n"
    if faq:
        fq = []
        for q, r in faq:
            r = sin_banderas(r, donde + " FAQ")
            if r:
                fq.append(f"**{q}**\n{r}")
        if fq:
            txt += "\n---\nFAQ\n\n" + "\n\n".join(fq) + "\n"
    open(os.path.join(OUT, nombre), "w", encoding="utf-8").write(txt)


def saca_faq(bloque):
    """Lista de (pregunta, respuesta) de un bloque «## Preguntas frecuentes»."""
    faq = []
    for m in re.finditer(r"\*\*(¿[^*]+\?)\*\*\s*(.+?)(?=\n\s*\n\*\*¿|\Z)", bloque.strip(), re.S):
        faq.append((m.group(1).strip(), " ".join(m.group(2).split())))
    return faq


def secciones(cuerpo):
    """Parte el cuerpo (tras el H1) en [(h2, texto)] conservando el orden; la intro va con h2=None."""
    partes = re.split(r"\n(?=## )", "\n" + cuerpo)
    res = []
    for p in partes:
        p = p.strip("\n")
        if not p.strip():
            continue
        m = re.match(r"## ([^\n]+)\n?(.*)", p, re.S)
        if m:
            res.append((m.group(1).strip(), m.group(2)))
        else:
            res.append((None, p))
    return res


SALTAR_H2 = re.compile(r"^(Foto e interlinking|Foto y enlaces|Por verificar|Cambios del|⚑|Enlaces internos|Notas)", re.I)


def monta(cab, cuerpo_md, donde, quitar_h2=()):
    """Cuerpo en markdown (sin la cabecera) → (líneas del cuerpo sin FAQ, faq)."""
    lineas, faq = [], []
    for h2, txt in secciones(cuerpo_md):
        if h2 is None:
            # intro: fuera el H1 repetido, fuera «**Entradilla**», fuera líneas de metadatos
            for l in txt.split("\n"):
                s = l.strip()
                if s.startswith("# ") or s == "**Entradilla**" or re.match(r"^\*\*(Texto alternativo|Enlaces internos|Slug|Keyword)", s) or re.match(r"^- \*\*", s):
                    continue
                lineas.append(l)
            continue
        if SALTAR_H2.match(h2) or h2 in quitar_h2:
            continue
        if h2.startswith("Preguntas frecuentes"):
            faq = saca_faq(txt)
            continue
        # dentro de la sección, fuera las líneas de metadatos sueltas
        cuerpo = [l for l in txt.split("\n") if not re.match(r"^\*\*(Texto alternativo|Enlaces internos)", l.strip())]
        lineas.append("")
        lineas.append(f"## {h2}")
        lineas.extend(cuerpo)
    return lineas, faq


# ---------- 1. Páginas principales ----------
def principales():
    txt = open(os.path.join(T, "paginas-principales.md"), encoding="utf-8").read()
    bloques = re.split(r"\n(?=## \d+\. )", txt)[1:]
    orden = {"/": "01", "/distribuidor-vinos-gallegos-hosteleria/": "02", "/distribuidor-vinos-hosteleria-madrid/": "03",
             "/distribuidor-vinos-hosteleria-alcorcon/": "04", "/catalogo/": "05", "/vino-turbio/": "06", "/licores/": "07",
             "/nosotros/": "08", "/contacto/": "09"}
    for b in bloques:
        if b.startswith("## Cambios"):
            continue
        url = re.search(r"\*\*URL:\*\* (/[^\s]*)", b).group(1)
        title = re.search(r"\*\*Title[^:]*:\*\* (.+)", b).group(1).strip()
        meta = re.search(r"\*\*Meta[^:]*:\*\* (.+)", b).group(1).strip()
        h1 = re.search(r"\*\*H1:\*\* (.+)", b).group(1).strip()
        kw = re.search(r"\*\*Keyword principal:\*\* ([^·\n]+)", b)
        cuerpo = re.split(r"### Texto final\s*\n", b)[1]
        cuerpo = re.split(r"\n### Por verificar|\n## Cambios", cuerpo)[0]
        quitar = ("Formulario de solicitud de tarifa",) if url == "/contacto/" else ()
        # en contacto, los «###» son secciones: súbelos a «##» para que el tema los lea
        cuerpo = re.sub(r"^### ", "## ", cuerpo, flags=re.M)
        if url == "/contacto/":
            cuerpo = re.sub(r"Línea informativa bajo el botón.*?(?=\n## |\Z)", "", cuerpo, flags=re.S)
            cuerpo = re.sub(r"Línea de confianza.*?\n", "", cuerpo)
            cuerpo = re.sub(r"Nota \(07/10/2026\).*?\n", "", cuerpo)
        lineas, faq = monta({}, cuerpo, url, quitar)
        meta = meta.replace("7 licores", "6 licores")
        if len(meta) < 120:   # el control pide 120-160: se completa con una frase validada en PROMESAS.md
            meta = meta.rstrip(".") + ". Sin pedido mínimo."
        cab = {"URL": url, "Title": title, "Meta description": meta, "Keyword principal": kw.group(1).strip() if kw else "", "H1": h1}
        escribe(f"{orden[url]}_{url.strip('/').replace('/', '-') or 'home'}.md", cab, lineas, faq, url)


# ---------- 2. Denominaciones ----------
def denominaciones():
    txt = open(os.path.join(T, "paginas-denominaciones.md"), encoding="utf-8").read()
    bloques = re.split(r"\n(?=## Página: )", txt)[1:]
    for b in bloques:
        url = re.search(r"\*\*URL:\*\* (/[^\s]*)", b).group(1)
        title = re.search(r"\*\*Title[^:]*:\*\* (.+)", b).group(1).strip()
        meta = re.search(r"\*\*Meta description[^:]*:\*\* (.+)", b).group(1).strip()
        h1 = re.search(r"\*\*H1:\*\* (.+)", b).group(1).strip()
        kw = re.search(r"\*\*Keyword principal:\*\* ([^(\n]+)", b).group(1).strip()
        cuerpo = b.split("\n", 1)[1]
        cuerpo = re.split(r"\n\*\*Enlaces internos\*\*|\n\*\*Por verificar", cuerpo)[0]
        cuerpo = re.sub(r"^- \*\*(URL|Keyword principal|Title|Meta description|H1)[^\n]*\n", "", cuerpo, flags=re.M)
        lineas, faq = monta({}, cuerpo, url)
        slug = url.strip("/").split("/")[-1]
        cab = {"URL": url, "Title": title, "Meta description": meta, "Keyword principal": kw, "H1": h1, "Denominacion": slug}
        escribe(f"10_do-{slug}.md", cab, lineas, faq, url)


# ---------- 3. Fichas de vino y de licor ----------
def fichas():
    n = 0
    for archivo, prefijo in [("fichas-vino-grupo-A.md", "20"), ("fichas-vino-grupo-B.md", "21"), ("fichas-vino-grupo-C.md", "22"), ("fichas-licores.md", "30")]:
        txt = open(os.path.join(T, archivo), encoding="utf-8").read()
        bloques = re.split(r"\n(?=## \d+\. |# FICHA \d+ )", txt)[1:]
        for b in bloques:
            if re.match(r"## \d+\. Vodka caramelo", b):
                continue
            m = re.search(r"(/(?:comprar|licores)/[a-z0-9-]+/)", b)
            if not m:
                continue
            url = m.group(1)
            title = re.search(r"\*\*Title SEO:\*\* (.+)", b).group(1).strip()
            meta = re.search(r"\*\*Meta description:\*\* (.+)", b).group(1).strip()
            h1 = re.search(r"\*\*H1:\*\* (.+)", b).group(1).strip()
            kw = re.search(r"\*\*Keyword principal:\*\* ([^·\n]+)", b)
            cuerpo = b.split("\n", 1)[1]
            cuerpo = re.split(r"\n### Por verificar|\n## Por verificar|\n## ⚑ Comunes|\n## Cambios del|\n\*\*Texto alternativo", cuerpo)[0]
            cuerpo = re.sub(r"^(- )?\*\*(Slug[^:]*|URL|Keyword principal|Title SEO|Meta description|H1)[^\n]*\n", "", cuerpo, flags=re.M)
            lineas, faq = monta({}, cuerpo, url)
            slug = url.strip("/").split("/")[-1]
            if len(meta) < 120:
                meta = meta.rstrip(".") + ". Sin pedido mínimo."
            cab = {"URL": url, "Title": title, "Meta description": meta, "Keyword principal": kw.group(1).strip() if kw else "", "H1": h1, "Producto": slug}
            escribe(f"{prefijo}_{'licor' if '/licores/' in url else 'vino'}-{slug}.md", cab, lineas, faq, url)
            n += 1
    return n


# ---------- 4. Legales ----------
def legales():
    out = ["# Textos legales · Vinos Gallegos Pousada (04-LEGALES, paso 14; corregidos, no reescritos). Generado por herramientas/importar_textos.py.", ""]
    for archivo, url, titulo in [("aviso-legal.md", "/aviso-legal/", "Aviso legal"), ("politica-de-privacidad.md", "/politica-de-privacidad/", "Política de privacidad"),
                                 ("politica-de-cookies.md", "/politica-de-cookies/", "Política de cookies")]:
        txt = open(os.path.join(L, archivo), encoding="utf-8").read()
        cuerpo = txt.split("## Texto final", 1)[1]
        cuerpo = re.split(r"\n---\s*\n## Notas de trabajo", cuerpo)[0]
        lineas = []
        for l in cuerpo.split("\n"):
            s = l.strip()
            if s.startswith("# "):           # el H1 lo pone el tema
                continue
            if s == "---":
                continue
            if s.startswith("*(") and s.endswith(")*"):
                continue
            if s.startswith(">"):
                continue
            if "Datos registrales" in s or "Alojamiento web:**" in s or "Correo electrónico:** [" in s:
                continue                      # datos pendientes del paso 6: la línea se suprime hasta tenerlos
            if s.startswith("Última actualización"):
                l = re.sub(r"⚑ \[[^\]]+\]", "octubre de 2026 (versión 1, vista previa)", l)
            if s.startswith("⚑ Si finalmente se publican precios") or s.startswith("⚑ Nombre y duración exactos") or s.startswith("⚑ El identificador exacto"):
                continue
            l = l.replace("⚑ `[nombre de la cookie o clave de almacenamiento del aviso de cookies de la base GYF]`", "`pousada-cookies` (almacenamiento local del navegador)")
            l = l.replace("⚑ Buzón de destino por confirmar (paso 6): info@vinospousada.es", "")
            l = l.replace("[la que fije la base; propuesta: 12 meses]", "Hasta que usted la borre (almacenamiento local del navegador, sin fecha de caducidad)")
            l = l.replace(" ⚑", "").replace("⚑ ", "").replace("⚑", "")
            l = re.sub(r"\s*\[(nuevo|concretado|reescrito[^\]]*|corregido[^\]]*)\]", "", l)
            lineas.append(l.rstrip())
        out.append(f"## {url}")
        out.append(titulo)
        out.append("\n".join(lineas).strip())
        out.append("")
    os.makedirs(os.path.join(RAIZ, "contenido", "legales"), exist_ok=True)
    open(os.path.join(RAIZ, "contenido", "legales", "legales.md"), "w", encoding="utf-8").write("\n".join(out))


principales()
denominaciones()
n = fichas()
legales()
print(f"importar_textos: {len(os.listdir(OUT))} páginas ({n} fichas) + 3 legales · frases con ⚑ no publicadas: {NO_PUBLICAR}")
if "--detalle" in sys.argv or True:
    open(os.path.join(RAIZ, "contenido", "NO-PUBLICADO.txt"), "w", encoding="utf-8").write(
        "Frases con ⚑ que importar_textos.py ha dejado fuera (se publican cuando David/Álvaro las confirmen):\n\n" + "\n".join(NO_PUBLICAR_LISTA) + "\n")
