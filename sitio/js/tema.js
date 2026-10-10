/* GYF · tema.js del tema 010-JESPER (Pousada). Va DESPUÉS de main.js (base GYF + Rayo) y no lo toca: la base dispara
   el evento «gyf:capa» cuando GSAP + ScrollTrigger (y Lenis en ordenador) ya están cargados, y aquí se monta la capa
   de movimiento del tema. Todo es mejora progresiva: sin JS, sin GSAP o con movimiento reducido, la web se ve entera y quieta.

   Piezas (números de la ficha de Jesper, FICHA.md §4, reproducidas con código propio; nivel «como GYF»):
   - A1  Palabras del titular que entran de abajo (yPercent 101 → 0, 0,9 s, power2.out, escalonadas 0,06 s). Solo si la
         página ha cargado rápido: si GSAP no llega en 2,5 s, el titular se muestra sin más (R2 de Rayo: nunca oculto).
   - E1  Paralaje suave de la foto de portada (15 %, scrub), solo ordenador.
   - F1  La estantería: franja clavada que avanza de lado con el scroll (pin + scrub), solo ordenador con ratón;
         en táctil y en pantallas pequeñas es una pista deslizable nativa (CSS).
   - Zoom de imagen al entrar (1,15 → 1, IntersectionObserver, sin GSAP).
   - El grifo del turbio (pieza nueva, FIRMA §4): en ordenador la banda se clava +600 px y el nivel amarillo sube de 0 a 100 %
         con scrub mientras el titular aparece línea a línea. En táctil y con movimiento reducido: quieta y llena.
   - J3  El racimo del pie (y el de las cabeceras de D.O.) se traza (stroke-dashoffset) al entrar en pantalla.
   - Catálogo: filtros por denominación y por tipo (botones que solo aparecen con JS).
   - Formulario: mensaje prerrelleno desde ?interes=…, frase de «particular», botón «Enviando…».
   Scrub y pin solo en ordenador con ratón (≥ 1.025 px de ancho y ≥ 700 px de alto); la cabecera siempre a la vista (los pines empiezan bajo ella). */
(function () {
  "use strict";
  var d = document, w = window, html = d.documentElement;
  var reducido = w.matchMedia && w.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var raton = w.matchMedia && w.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var escritorio = function () { return raton && w.innerWidth >= 1025 && w.innerHeight >= 700; };   // Emil (auditoría 08/10): sin pin en portátiles bajos
  var cabAlto = function () { var c = d.querySelector("[data-cab]"); return c ? c.offsetHeight : 84; };

  /* ---------- Palabras y líneas (sin SplitText) ---------- */
  function palabras(el) {
    var out = [];
    (function rec(n) {
      [].slice.call(n.childNodes).forEach(function (c) {
        if (c.nodeType === 3) {
          var f = d.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach(function (t) {
            if (!t) return;
            if (/^\s+$/.test(t)) { f.appendChild(d.createTextNode(t)); return; }
            var s = d.createElement("span"); s.className = "pal"; s.textContent = t; f.appendChild(s); out.push(s);
          });
          c.parentNode.replaceChild(f, c);
        } else if (c.nodeType === 1 && !c.classList.contains("pal")) rec(c);
      });
    })(el);
    return out;
  }
  function lineas(el) {
    /* agrupa las palabras por su línea (offsetTop) y las envuelve en .lin */
    var pals = palabras(el), grupos = [], ultimo = null, actual = null;
    pals.forEach(function (p) {
      var top = p.offsetTop;
      if (ultimo === null || Math.abs(top - ultimo) > 4) { actual = []; grupos.push(actual); ultimo = top; }
      actual.push(p);
    });
    return grupos.map(function (g) {
      var lin = d.createElement("span"); lin.className = "lin";
      g[0].parentNode.insertBefore(lin, g[0]);
      g.forEach(function (p, i) { lin.appendChild(p); if (i < g.length - 1) lin.appendChild(d.createTextNode(" ")); });
      return lin;
    });
  }

  /* ---------- Titular: se oculta solo si la página va rápida; si GSAP no llega, se enseña ---------- */
  var titulares = [].slice.call(d.querySelectorAll("[data-palabras]"));
  var ocultoPronto = false;
  if (titulares.length && !reducido && d.readyState !== "complete" && (w.performance && performance.now() < 1500)) {
    html.classList.add("con-gsap"); ocultoPronto = true;
    setTimeout(function () { if (!w.gsap) { html.classList.remove("con-gsap"); } }, 2500);
  }
  titulares.forEach(function (h) { h._pals = palabras(h); });

  /* ---------- Zoom de imagen al entrar (sin GSAP) ---------- */
  var zooms = d.querySelectorAll("[data-zoom]");
  if (zooms.length) {
    if (reducido || !("IntersectionObserver" in w)) zooms.forEach(function (z) { z.classList.add("listo"); });
    else {
      var ioZ = new IntersectionObserver(function (ents) {
        ents.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("listo"); ioZ.unobserve(en.target); } });
      }, { rootMargin: "0px 0px -10% 0px" });
      zooms.forEach(function (z) { ioZ.observe(z); });
    }
  }

  /* ---------- Catálogo: filtros ---------- */
  var filtros = d.querySelector("[data-filtros]"), rejilla = d.querySelector("[data-rejilla]");
  if (filtros && rejilla) {
    filtros.hidden = false;
    var cuenta = filtros.querySelector("[data-cuenta]"), estado = { do: null, tipo: null };
    function aplica() {
      var n = 0;
      rejilla.querySelectorAll(".prod").forEach(function (li) {
        var ok = (!estado.do || li.getAttribute("data-do") === estado.do) && (!estado.tipo || li.getAttribute("data-tipo") === estado.tipo);
        li.classList.toggle("oculto", !ok); if (ok) n++;
      });
      filtros.querySelectorAll("[data-filtro]").forEach(function (b) {
        var f = b.getAttribute("data-filtro"), v = b.getAttribute("data-valor");
        b.setAttribute("aria-pressed", f === "todo" ? String(!estado.do && !estado.tipo) : String(estado[f] === v));
      });
      if (cuenta) cuenta.textContent = n + (n === 1 ? " referencia" : " referencias");
      w.dataLayer = w.dataLayer || [];
      w.dataLayer.push({ event: "filtro_catalogo", do: estado.do || "", tipo: estado.tipo || "", resultados: n });
    }
    filtros.addEventListener("click", function (e) {
      var b = e.target.closest("[data-filtro]"); if (!b) return;
      var f = b.getAttribute("data-filtro"), v = b.getAttribute("data-valor");
      if (f === "todo") { estado.do = estado.tipo = null; } else { estado[f] = estado[f] === v ? null : v; }
      aplica();
    });
    if (cuenta) cuenta.textContent = rejilla.querySelectorAll(".prod").length + " referencias";
  }

  /* ---------- Formulario: ?interes=, «particular», «Enviando…» ---------- */
  d.querySelectorAll("form.formulario").forEach(function (f) {
    var pag = f.querySelector('input[name="pagina"]'); if (pag && !pag.value) pag.value = w.location.pathname;
    var msg = f.querySelector("[data-mensaje]"), q = /[?&]interes=([a-z0-9-]+)/i.exec(w.location.search);
    if (msg && q && !msg.value) {
      try { var mapa = JSON.parse(f.getAttribute("data-intereses") || "{}"); if (mapa[q[1]]) msg.value = "Me interesa: " + mapa[q[1]] + "."; } catch (e) {}
    }
    var sel = f.querySelector("[data-tipo-negocio]"), part = f.querySelector("[data-particular]");
    if (sel && part) sel.addEventListener("change", function () { part.hidden = sel.value !== "Particular"; });
    f.addEventListener("submit", function () {
      var b = f.querySelector('button[type="submit"]'); if (!b) return;
      setTimeout(function () { b.disabled = true; var sr = b.querySelector(".sr"); if (sr) sr.textContent = "Enviando…"; var a = b.querySelector(".btn__a"); if (a) a.textContent = "Enviando…"; }, 0);
    });
    var ok = f.querySelector("#form-ok");
  });

  /* ---------- Capa con GSAP (la dispara main.js al cargar GSAP + ScrollTrigger) ---------- */
  function trazar(G, ST, svg, start) {
    var paths = [].slice.call(svg.querySelectorAll("path"));
    if (!paths.length) return;
    paths.forEach(function (p) { var L = p.getTotalLength(); p.style.strokeDasharray = L; p.style.strokeDashoffset = L; });
    svg.classList.add("listo");
    G.to(paths, { strokeDashoffset: 0, duration: 1.6, stagger: 0.12, ease: "power2.inOut", scrollTrigger: { trigger: svg, start: start || "top 85%" } });
  }

  function capa(ev) {
    var G = w.gsap, ST = w.ScrollTrigger;
    if (!G || !ST) return;
    html.classList.add("con-gsap");

    /* A1 · Titular por palabras */
    titulares.forEach(function (h) {
      var pals = h._pals || palabras(h);
      h.classList.add("listo");
      if (ocultoPronto) G.fromTo(pals, { yPercent: 101, opacity: 0 }, { yPercent: 0, opacity: 1, duration: 0.9, ease: "power2.out", stagger: 0.06, clearProps: "transform,opacity" });
    });

    /* E1 · Paralaje de la foto de portada (15 %) */
    var pf = d.querySelector("[data-paralaje] img");
    if (pf && escritorio()) G.fromTo(pf, { yPercent: -7 }, { yPercent: 7, ease: "none", scrollTrigger: { trigger: pf.closest("[data-paralaje]"), start: "top bottom", end: "bottom top", scrub: true } });

    /* F1 · La estantería clavada que avanza de lado */
    var est = d.querySelector("[data-estanteria]"), clavo = d.querySelector("[data-estanteria-clavo]"), pista = d.querySelector("[data-estanteria-pista]");
    if (est && clavo && pista && escritorio()) {
      var recorrido = function () { return Math.max(0, pista.scrollWidth - clavo.clientWidth); };
      if (recorrido() > 80) {
        // v3 (paso 38, Emil N-1): con-clavo solo se añade aquí, cuando el pin se crea de verdad; así el CSS
        // (tema.css, .js.con-clavo .estanteria__*) nunca extiende la pista sin que el JS la mueva — antes dependía
        // de con-gsap a secas, que ganaba la condición de ancho pero no la de alto, y dejaba la pista recortada
        // e inalcanzable en portátiles de ≥1025px de ancho y <700px de alto.
        html.classList.add("con-clavo");
        G.to(pista, { x: function () { return -recorrido(); }, ease: "none",
          scrollTrigger: { trigger: est, start: function () { return "top " + (cabAlto() + 8); }, end: function () { return "+=" + (recorrido() + 200); },
            pin: true, scrub: 1, invalidateOnRefresh: true, anticipatePin: 1 } });
      }
    }

    /* El grifo del turbio: banda clavada, nivel que sube, titular línea a línea */
    var grifo = d.querySelector("[data-grifo]");
    if (grifo) {
      var nivel = grifo.querySelector("[data-nivel]"), tit = grifo.querySelector("[data-lineas]");
      var lins = tit ? lineas(tit) : [];
      if (tit) tit.classList.add("listo");
      if (escritorio()) {
        var tl = G.timeline({ scrollTrigger: { trigger: grifo, start: function () { return "top " + (cabAlto() + 8); }, end: "+=600", pin: true, scrub: 1, anticipatePin: 1 } });
        if (nivel) tl.fromTo(nivel, { scaleY: 0 }, { scaleY: 1, ease: "none" }, 0);
        if (lins.length) tl.fromTo(lins, { opacity: 0, y: 24 }, { opacity: 1, y: 0, stagger: 0.25, ease: "power2.out" }, 0);
      } else if (lins.length && !reducido) {
        G.fromTo(lins, { opacity: 0, y: 20 }, { opacity: 1, y: 0, stagger: 0.15, duration: 0.7, ease: "power2.out", scrollTrigger: { trigger: grifo, start: "top 75%" } });
      }
    }

    /* J3 · Racimo que se traza: pie y cabeceras de D.O. */
    d.querySelectorAll("[data-traza]").forEach(function (svg) { trazar(G, ST, svg, svg.closest(".pie") ? "top 92%" : "top 80%"); });

    ST.refresh();
  }
  if (!reducido) {
    if (w.gsap && w.ScrollTrigger && html.classList.contains("con-gsap") && d.readyState === "complete") capa();
    else d.addEventListener("gyf:capa", capa);
  } else {
    html.classList.remove("con-gsap");
    d.querySelectorAll("[data-palabras], [data-lineas], [data-traza]").forEach(function (e) { e.classList.add("listo"); });
  }
})();
