#!/usr/bin/env bash
# Genera la web y la sirve en local en http://localhost:8765 (pasos 25 y 28-30 del protocolo).
# Uso (desde la raíz del repositorio del cliente):  bash herramientas/servir.sh
set -e
python3 generador/build.py
python3 generador/rematar.py
python3 generador/controles.py
pkill -f "http.server 8765" 2>/dev/null || true
# build.py borra sitio/ y lo vuelve a crear: el servidor se arranca siempre después, con --directory
(nohup python3 -m http.server 8765 --directory "$(pwd)/sitio" >/dev/null 2>&1 &)
sleep 1
echo "Sirviendo en http://localhost:8765"
