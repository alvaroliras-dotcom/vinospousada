#!/usr/bin/env bash
# Lighthouse móvil (paso 30 del protocolo). Pasa 3 veces cada página, porque la nota varía entre
# pasadas, y da la mediana de rendimiento más accesibilidad, SEO, LCP, TBT y CLS.
# Umbrales medidos en la primera web: home >= 85, landings >= 95, accesibilidad >= 95, SEO 100.
#
# Uso:  bash lighthouse.sh http://localhost:8765 / /fontaneria-villaejemplo/
# Requiere: npm i -g lighthouse  (y CHROME_PATH si Chrome no está en el sitio habitual)
BASE="$1"; shift
[ -z "$BASE" ] && { echo "Uso: bash lighthouse.sh <url-base> <ruta> [<ruta>...]"; exit 1; }
[ -z "$CHROME_PATH" ] && [ -x /opt/pw-browsers/chromium-1194/chrome-linux/chrome ] && export CHROME_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
for RUTA in "${@:-/}"; do
  for i in 1 2 3; do
    lighthouse "$BASE$RUTA" --quiet --form-factor=mobile --chrome-flags="--headless=new --no-sandbox" \
      --output=json --output-path="/tmp/lh-$i.json" >/dev/null 2>&1
  done
  python3 - "$RUTA" <<'EOF'
import json, sys, statistics
r = [json.load(open(f"/tmp/lh-{i}.json")) for i in (1, 2, 3)]
cat = lambda k: [round(x["categories"][k]["score"] * 100) for x in r]
aud = lambda k: [x["audits"][k]["numericValue"] for x in r]
print(f"{sys.argv[1]}  rendimiento {statistics.median(cat('performance'))} ({'/'.join(map(str, cat('performance')))})"
      f" · accesibilidad {statistics.median(cat('accessibility'))} · SEO {statistics.median(cat('seo'))}"
      f" · LCP {statistics.median(aud('largest-contentful-paint'))/1000:.1f} s · TBT {statistics.median(aud('total-blocking-time')):.0f} ms"
      f" · CLS {statistics.median(aud('cumulative-layout-shift')):.3f}")
EOF
done
