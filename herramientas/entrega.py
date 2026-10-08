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
"""
import argparse, os, shutil, subprocess, sys, zipfile

MAX_ARCHIVOS = 60          # archivos + carpetas por tanda: < 100 (a Álvaro le cuenta también las carpetas al arrastrar)
MAX_BYTES = 24 * 1024 * 1024   # < 25 MB
EXCLUIR = ("__pycache__", ".cache-img", ".git/", ".DS_Store")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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
    a = ap.parse_args()
    repo, sal = os.path.abspath(a.repo), os.path.abspath(a.salida)
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
               "EL DÍA DE PUBLICAR EN EL HOSTING DEL CLIENTE (paso 44+): se sube el contenido de sitio/ (incluido .htaccess y enviar.php) "
               "y se confirma el buzón del formulario (info@vinospousada.es) y el GTM."]
    open(os.path.join(sal, "LEEME.txt"), "w", encoding="utf-8").write("\n".join(lineas) + "\n")
    print(f"entrega: {len(lista)} archivos en {len(grupos)} tandas → {dest} · LEEME.txt")


if __name__ == "__main__":
    main()
