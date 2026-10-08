#!/usr/bin/env bash
# Compila el módulo 3D del objeto de portada (paso 48 si se cambia). Desde la raíz del tema:
#   bash herramientas/objeto3d/construir.sh
# Necesita three@0.160 (npm i three@0.160.0 en herramientas/objeto3d/) y esbuild (npx lo descarga).
set -e
cd "$(dirname "$0")"
[ -d node_modules/three ] || npm i --no-save three@0.160.0 >/dev/null
npx --yes esbuild objeto3d.js --bundle --minify --format=iife --global-name=Objeto3D --target=es2019 \
  --legal-comments=none --outfile=../../cliente/js/vendor/objeto3d.min.js
ls -l ../../cliente/js/vendor/objeto3d.min.js
gzip -c ../../cliente/js/vendor/objeto3d.min.js | wc -c | awk '{printf "comprimido (gzip): %.0f KB\n", $1/1024}'
