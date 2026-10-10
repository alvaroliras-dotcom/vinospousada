#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepara la entrega de una versión en 08-WEB (paso 27 del protocolo v12): tandas de MENOS de 100 archivos y MENOS de 25 MB
para subirlas por la web de GitHub, más el LEEME.txt con el orden de arrastre y la lista de alta de Vercel.

Dos modos:
  - Sin git (por defecto; en las carpetas conectadas no se usa git): entra TODO el repositorio (menos __pycache__ y la caché
    de imágenes). Es la primera entrega de un repositorio nuevo o una entrega completa.
  - --desde <commit> (si el repositorio tiene git): solo los archivos que cambian desde ese commit.

Salida en <salida>/SUBIR-A-GITHUB/:
  TANDA-1/, TANDA-2/…      carpetas con el árbol del repositorio (se arrastran las carpetas que se ven al abrir la TANDA, juntas)
  <cliente>-vN-tandaN.zip  lo mismo, en zip (para guardar o para subir desde otro ordenador)
  y <salida>/LEEME.txt

Uso:  python3 herramientas/entrega.py --cliente pousada --version 1 [--salida ../] [--desde <commit>]
Se para si una tanda no cumple los dos límites (no debería: se parte hasta cumplirlos).

Tercer modo, para el día de publicar (Bruno A4, Turing M1):
  --produccion   genera <salida>/HOSTING/ con SOLO el contenido de sitio/ (incluidos .htaccess y enviar.php, que GitHub no sube
                 o no sirve) y SIN vercel.json (su X-Robots-Tag noindex es solo de la vista previa), más <cliente>-vN-hosting.zip
                 y HOSTING-LEEME.txt. Lo que se sube a httpdocs/ es el contenido de HOSTING/. La lista de comprobación por HTTP
                 está en herramientas/PUBLICAR.md (se copia al lado).
"""
import argparse, os, shutil, subprocess, sys, zipfile

MAX_ARCHIVOS = 90          # archivos + carpetas por tanda: límite real de GitHub = 100 por subida web
MAX_BYTES = 80 * 1024 * 1024   # margen de sobra bajo el límite real de GitHub para subida por arrastre
EXCLUIR = ("__pycache__", ".cache-img", ".git/", ".DS_Store")
NO_PRODUCCION = ("vercel.json",)   # archivos de sitio/ que NO van al hosting del cliente
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def produccion(repo, sal, cliente, version):
    """HOSTING/: el contenido de sitio/ tal cual se sube a la raíz pública del hosting, sin los archivos de la vista previa."""
    sitio = os.path.join(repo, "sitio")
    if not os.path.isdir(sitio):
        sys.exit("entrega: no existe sitio/ (antes: python3 generador/build.py && python3 generador/rematar.py)")
    dest = os.path.join(sal, "HOSTING")
    if os.path.exists(dest):
        shutil.rmtree(dest)
    n, peso, fuera = 0, 0, []
    for r, ds, fs in os.walk(sitio):
        ds[:] = [d for d in ds if d not in ("__pycache__",)]
        for f in sorted(fs):
            rel = os.path.relpath(os.path.join(r, f), sitio).replace(os.sep, "/")
            if rel in NO_PRODUCCION or f == ".DS_Store":
                fuera.append(rel); continue
            d = os.path.join(dest, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(os.path.join(r, f), d)
            n += 1; peso += os.path.getsize(d)
    # Comprobaciones antes de entregar: lo que tiene que estar y lo que no puede estar
    faltan = [f for f in (".htaccess", "enviar.php", "robots.txt", "sitemap.xml", "llms.txt", "index.html", "404.html", "og-image.jpg", "site.webmanifest") if not os.path.exists(os.path.join(dest, f))]
    if faltan:
        sys.exit(f"entrega: HOSTING/ incompleto, faltan {faltan}")
    for f in NO_PRODUCCION:
        if os.path.exists(os.path.join(dest, f)):
            sys.exit(f"entrega: {f} no puede ir a producción")
    ht = open(os.path.join(dest, ".htaccess"), encoding="utf-8").read()
    if "X-Robots-Tag" in ht:
        sys.exit("entrega: el .htaccess lleva X-Robots-Tag (el noindex es solo de la vista previa)")
    for raiz, _, fs in os.walk(dest):
        for f in fs:
            if f.endswith((".md", ".py", ".csv", ".bak", ".log")):
                sys.exit(f"entrega: {os.path.relpath(os.path.join(raiz, f), dest)} no es un archivo de la web pública")
    zp = os.path.join(sal, f"{cliente}-v{version}-hosting.zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for raiz, _, fs in os.walk(dest):
            for f in sorted(fs):
                p = os.path.join(raiz, f)
                z.write(p, os.path.relpath(p, dest))
    publicar = os.path.join(repo, "herramientas", "PUBLICAR.md")
    if os.path.exists(publicar):
        shutil.copy2(publicar, os.path.join(sal, "PUBLICAR.md"))
    puntos = sorted(f for f in os.listdir(dest) if f.startswith("."))
    lineas = [f"08-WEB · {cliente.upper()} · v{version} · HOSTING: {n} archivos, {peso / 1048576:.1f} MB", "",
              "QUÉ ES: el contenido de sitio/ tal cual se sube a la raíz pública del hosting del cliente (httpdocs/). Nada más.",
              f"Fuera a propósito: {', '.join(fuera) or '(nada)'} (solo valen para la vista previa de Vercel; vercel.json lleva noindex).",
              f"Archivos que empiezan por punto (los gestores de archivos los esconden; comprobar que han subido): {', '.join(puntos) or '(ninguno)'}.", "",
              "CÓMO: subir el CONTENIDO de HOSTING/ (o descomprimir el zip de al lado en httpdocs/). Después, la lista de",
              "comprobación por HTTP de PUBLICAR.md, punto por punto: HTTPS y sin www, las 29 URLs viejas en 301 → 200, 410 y 404,",
              "cabeceras sin X-Robots-Tag, compresión y caché, archivos que no deben verse, formulario con envíos reales,",
              "medición con la vista previa de GTM y Search Console (sitemap).", "",
              "ANTES de generar la versión que se publica, en generador/config.py: GTM_ID, NEGOCIO[\"email_aviso\"], FORMULARIO[\"buzon\"]",
              "confirmado y, si ya existe, el CID de la ficha de Google con las coordenadas del pin (geo_aproximado = False)."]
    open(os.path.join(sal, "HOSTING-LEEME.txt"), "w", encoding="utf-8").write("\n".join(lineas) + "\n")
    print(f"entrega: HOSTING/ con {n} archivos ({peso / 1048576:.1f} MB) · fuera: {', '.join(fuera) or '(nada)'} → {dest} · {os.path.basename(zp)} · HOSTING-LEEME.txt · PUBLICAR.md")


def archivos_repo(repo):
    out = []
    for r, ds, fs in os.walk(repo):
        ds[:] = [d for d in ds if d not in ("__pycache__", ".cache-img", ".git")]
        for f in fs:
            rel = os.path.relpath(os.path.join(r, f), repo).replace(os.sep, "/")
            if any(x in rel for x in EXCLUIR):
                continue
            out.append(rel)
    return sorted(out)


def archivos_git(repo, desde):
    r = subprocess.run(["git", "-C", repo, "diff", "--name-only", desde, "HEAD"], capture_output=True, text=True, check=True)
    return sorted(f for f in r.stdout.splitlines() if f and os.path.exists(os.path.join(repo, f)))


def _elementos(f):
    """Carpetas que cuelgan de un archivo (cada una cuenta como un elemento al arrastrar)."""
    partes = f.split("/")[:-1]
    return {"/".join(partes[:i + 1]) for i in range(len(partes))}


def tandas(repo, lista):
    """Parte la lista: en cada tanda, archivos + carpetas < 100 y menos de 25 MB. Primero el código, luego sitio/."""
    grupos, actual, carpetas, bytes_ = [], [], set(), 0
    orden = sorted(lista, key=lambda f: (f.startswith("sitio/"), f))
    for f in orden:
        t = os.path.getsize(os.path.join(repo, f))
        if t >= MAX_BYTES:
            sys.exit(f"entrega: {f} pesa {t / 1048576:.1f} MB; no cabe en una tanda")
        nuevas = _elementos(f) - carpetas
        if actual and (len(actual) + len(carpetas) + 1 + len(nuevas) > MAX_ARCHIVOS or bytes_ + t > MAX_BYTES):
            grupos.append(actual); actual, carpetas, bytes_ = [], set(), 0
            nuevas = _elementos(f)
        actual.append(f); carpetas |= nuevas; bytes_ += t
    if actual:
        grupos.append(actual)
    return grupos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=RAIZ)
    ap.add_argument("--cliente", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--desde", default=None, help="commit de la última versión subida (solo si hay git)")
    ap.add_argument("--salida", default=os.path.join(RAIZ, ".."), help="carpeta 08-WEB")
    ap.add_argument("--produccion", action="store_true", help="solo HOSTING/ (contenido de sitio/ con .htaccess y enviar.php, sin vercel.json) para el hosting del cliente")
    a = ap.parse_args()
    repo, sal = os.path.abspath(a.repo), os.path.abspath(a.salida)
    if a.produccion:
        produccion(repo, sal, a.cliente, a.version)
        return
    lista = archivos_git(repo, a.desde) if a.desde else archivos_repo(repo)
    dest = os.path.join(sal, "SUBIR-A-GITHUB")
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    grupos = tandas(repo, lista)
    lineas = [f"08-WEB · {a.cliente.upper()} · v{a.version} · {len(lista)} archivos en {len(grupos)} tanda(s)", "",
              "QUÉ ES: la web generada (sitio/) y el código que la genera (generador/, contenido/, recursos/, cliente/, base/, herramientas/).",
              f"Carpeta de trabajo completa: 08-WEB/repositorio-v{a.version}/ (no se sube; es la copia al día).", "",
              "CÓMO SUBIRLO A GITHUB (página principal del repositorio > Add file > Upload files), tanda por tanda y en este orden:"]
    for i, g in enumerate(grupos, 1):
        carpeta = os.path.join(dest, f"TANDA-{i}")
        peso = 0
        for f in g:
            d = os.path.join(carpeta, f)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(os.path.join(repo, f), d)
            peso += os.path.getsize(d)
        assert len(g) + len({c for f in g for c in _elementos(f)}) < 100 and peso < 25 * 1048576, f"TANDA-{i} se pasa de los límites"
        zp = os.path.join(dest, f"{a.cliente}-v{a.version}-tanda{i}.zip")
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for f in g:
                z.write(os.path.join(repo, f), f"TANDA-{i}/{f}")
        raices = sorted({f.split("/")[0] for f in g})
        puntos = [f for f in g if os.path.basename(f).startswith(".") and f.startswith("sitio/")]
        lineas.append(f"  {i}. Abre SUBIR-A-GITHUB/TANDA-{i} ({len(g)} archivos, {peso / 1048576:.1f} MB). Selecciona lo que ves al abrirla "
                      f"({', '.join(raices)}), arrástralo JUNTO a la zona de subida y pulsa «Commit changes». "
                      f"Espera a que termine antes de la siguiente.")
        if puntos:
            lineas.append(f"     Ojo: GitHub no sube archivos que empiezan por punto ({', '.join(os.path.basename(p) for p in puntos)}): "
                          "van al hosting a mano el día de publicar (están en el zip).")
    lineas += ["", "Los zip de al lado son lo mismo por tandas, por si se sube desde otro ordenador o para guardar.", "",
               "ALTA DEL PROYECTO EN VERCEL (vista previa, la primera vez):",
               "  1. vercel.com > Add New > Project > Import del repositorio de GitHub.",
               "  2. En «Root Directory» pulsa Edit y escribe:  sitio   (si no, sale un 404, como en Solvento).",
               "  3. Framework Preset: «Other». Build Command: vacío. Output Directory: vacío. Install Command: vacío.",
               f"  4. Deploy. La vista previa sale en https://<proyecto>.vercel.app con noindex (sitio/vercel.json) y se revisa con ?v={a.version}.",
               "  5. Cada subida nueva a GitHub vuelve a desplegar sola.", "",
               "EL DÍA DE PUBLICAR EN EL HOSTING DEL CLIENTE (paso 44+): python3 herramientas/entrega.py --cliente … --version … --produccion",
               "genera HOSTING/ (contenido de sitio/ con .htaccess y enviar.php, SIN vercel.json) y se sigue herramientas/PUBLICAR.md:",
               "lista de comprobación por HTTP (301, HTTPS, cabeceras, formulario, GTM, Search Console). Antes: buzón del formulario",
               "confirmado, email_aviso y GTM_ID en config.py."]
    open(os.path.join(sal, "LEEME.txt"), "w", encoding="utf-8").write("\n".join(lineas) + "\n")
    print(f"entrega: {len(lista)} archivos en {len(grupos)} tandas → {dest} · LEEME.txt")


if __name__ == "__main__":
    main()
