# Herramientas (GYF-Rayo)

Se lanzan todas desde la raíz del tema (o del repositorio del cliente).

| Herramienta | Paso | Qué hace |
|---|---|---|
| `servir.sh` | 28-30 | build → rematar → controles y sirve `sitio/` en `http://localhost:8765` |
| `capturas.py` | 29 | Playwright para Python con SwiftShader (WebGL sin GPU): primera pantalla y página entera a 390, 1.024 y 1.440 px, desborde horizontal y errores JS. `python3 herramientas/capturas.py --salida capturas / /contacto/` (`--solo-primera` para ir rápido) |
| `capturas.js` | 29 | La de 002 en Node (misma idea, sin SwiftShader) |
| `lighthouse.sh` | 30 | Lighthouse móvil tres veces por página y la mediana |
| `entrega.py` | 27 | Tandas < 100 archivos y < 25 MB (comprueba los dos límites) en `08-WEB/SUBIR-A-GITHUB/` + zips + `LEEME.txt` con el alta de Vercel. Sin git por defecto; `--desde <commit>` si lo hay |
| `importar_textos.py` | 27 | (Pousada) Textos de Merche (05-TEXTOS-NUEVOS, 04-LEGALES) → `contenido/paginas/*.md` y `legales.md`; deja `contenido/NO-PUBLICADO.txt` |
| `objeto3d/construir.sh` | 48 | Compila `objeto3d.js` (three.js 0.160) a `cliente/js/vendor/objeto3d.min.js` con esbuild |
| `objeto3d/foto_fija.py` | 33 | Pinta la imagen fija del objeto 3D (el LCP y el respaldo) con el mismo módulo, sobre fondo transparente, en `recursos/objeto/` |
