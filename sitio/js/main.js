/* GYF-Rayo · main.js
   Los marcadores con doble guion bajo (Europe/Madrid, []…) los rellena generador/rematar.py con config.py.
   BASE GYF (igual que en 002): estado abierto/cerrado, reseñas desde /resenas.json, formularios (antispam de
   tiempo, recuperar lo escrito, avisos de vuelta), cookies con modo de consentimiento, GTM solo en producción,
   eventos de medición, barra fija del móvil, FAQ con una abierta.
   CAPA DE RAYO (003): cabecera que se esconde y vuelve (R4-B), menú a pantalla completa (R34), apariciones (R18/R20),
   contadores (R32), carrusel de opiniones (R33), foto que sigue al cursor (R23), índice activo, subir (R10) y,
   con GSAP + ScrollTrigger + Lenis (solo ordenador) cargados al terminar la página: cintas que aceleran con el
   scroll (R14), portada fija con salida (R5), palabras que se encienden (R11), banda que se abre (R21),
   paralaje dentro del marco (R22), sello que gira con el scroll (R25) y el objeto 3D diferido.
   Sin JS o con movimiento reducido, todo se ve quieto y completo. */
(function () {
  "use strict";
  var d = document, w = window, html = d.documentElement;
  html.classList.add("js");
  var reducido = w.matchMedia && w.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var raton = w.matchMedia && w.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var ancho = function () { return w.innerWidth; };

  /* ---------- Cabecera (R4, variación B): se esconde al bajar y vuelve al subir, con fondo ---------- */
  var cab = d.querySelector("[data-cab]"), menu = d.querySelector("[data-menu]"), yAnt = 0;
  function alScroll() {
    var y = w.scrollY;
    if (cab && !(menu && menu.classList.contains("abierta"))) {
      cab.classList.remove("oculta");
      cab.classList.toggle("con-fondo", y >= 10); /* siempre a la vista (base GYF, protocolo v11) */
    }
    yAnt = y;
    if (subir) subir.classList.toggle("visible", y > (d.documentElement.scrollHeight - w.innerHeight) * .2 && y > 600);
  }
  var subir = d.querySelector("[data-subir]");
  w.addEventListener("scroll", alScroll, { passive: true }); alScroll();

  /* ---------- Menú a pantalla completa (R34) ---------- */
  var burger = d.querySelector(".cab__burger");
  function toggle(ab) {
    if (!menu) return;
    menu.classList.toggle("abierta", ab);
    menu.setAttribute("aria-hidden", ab ? "false" : "true");
    if (burger) burger.setAttribute("aria-expanded", ab ? "true" : "false");
    d.body.style.overflow = ab ? "hidden" : "";
    if (w.__lenis) { if (ab) w.__lenis.stop(); else w.__lenis.start(); }
    if (ab) { var c = menu.querySelector(".menu__cerrar"); if (c) setTimeout(function () { c.focus(); }, 50); } else if (burger) burger.focus();
  }
  if (burger) burger.addEventListener("click", function () { toggle(true); });
  if (menu) {
    menu.addEventListener("click", function (e) { if (e.target.closest(".menu__cerrar") || e.target.closest("a")) toggle(false); });
    d.addEventListener("keydown", function (e) {
      if (!menu.classList.contains("abierta")) return;
      if (e.key === "Escape") toggle(false);
      if (e.key === "Tab") { /* el foco no sale del menú */
        var f = menu.querySelectorAll("a[href], button"), a = f[0], z = f[f.length - 1];
        if (e.shiftKey && d.activeElement === a) { e.preventDefault(); z.focus(); }
        else if (!e.shiftKey && d.activeElement === z) { e.preventDefault(); a.focus(); }
      }
    });
  }

  /* ---------- Estado en vivo: horario de la ficha (config.py: abre, cierra, dias_schema, zona_horaria) ---------- */
  var FEST = [], PASCUA = [], LABORABLES = [1, 2, 3, 4, 5];
  var DIAS = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"];
  function pascua(y) {
    var a = y % 19, b = Math.floor(y / 100), c = y % 100, dd = Math.floor(b / 4), e = b % 4, f = Math.floor((b + 8) / 25),
      g = Math.floor((b - f + 1) / 3), h = (19 * a + b - dd - g + 15) % 30, i = Math.floor(c / 4), k = c % 4,
      l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451), mes = Math.floor((h + l - 7 * m + 114) / 31);
    return Date.UTC(y, mes - 1, ((h + l - 7 * m + 114) % 31) + 1);
  }
  function esLaborable(dt) {
    var dias = Math.round((dt.getTime() - pascua(dt.getUTCFullYear())) / 864e5);
    return LABORABLES.indexOf(dt.getUTCDay()) > -1 && PASCUA.indexOf(dias) < 0 && FEST.indexOf(dt.getUTCDate() + "/" + (dt.getUTCMonth() + 1)) < 0;
  }
  var ABIERTO = null;
  function estado() {
    var p = {};
    try {
      new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Madrid", year: "numeric", day: "numeric", month: "numeric", hour: "numeric", minute: "numeric", hour12: false })
        .formatToParts(new Date()).forEach(function (x) { p[x.type] = x.value; });
    } catch (e) { return; }
    var h = parseInt(p.hour, 10) % 24;
    var hoy = new Date(Date.UTC(parseInt(p.year, 10), parseInt(p.month, 10) - 1, parseInt(p.day, 10)));
    var laborable = esLaborable(hoy);
    var abierto = ABIERTO = laborable && h >= 8 && h < 20;
    d.querySelectorAll("[data-estado]").forEach(function (el) {
      el.classList.add(abierto ? "abierto" : "fuera");
      var s = el.querySelector("span");
      if (s) s.textContent = abierto ? "Abierto ahora · hasta las 20:00" : "Ahora cerrado · de 8 a 20 h";
    });
    var txt;
    if (abierto) txt = "Le llamamos hoy mismo.";
    else if (laborable && h < 8) txt = "Le llamamos hoy a partir de las 8:00.";
    else {
      var sig = new Date(hoy.getTime()), n = 0;
      do { sig.setUTCDate(sig.getUTCDate() + 1); n++; } while (!esLaborable(sig) && n < 15);
      txt = "Le llamamos {dia} a partir de las 8:00.".replace("{dia}", n === 1 ? "mañana" : "el " + DIAS[sig.getUTCDay()]);
    }
    d.querySelectorAll("[data-promesa]").forEach(function (el) { el.textContent = txt; });
  }
  estado();
  d.querySelectorAll("[data-anio]").forEach(function (e) { e.textContent = new Date().getFullYear(); });

  /* ---------- Reseñas: nota, número y opiniones desde /resenas.json ---------- */
  function esc(x) { return String(x || "").replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function ponOpiniones(ops) {
    var ul = d.querySelector("[data-opiniones]"); if (!ul || !ops || !ops.length) return;
    ul.innerHTML = ops.map(function (o) {
      return '<li class="op' + (o.marcador ? " op--marcador" : "") + '"><span class="estrellas" aria-label="5 estrellas">★★★★★</span>' +
        '<p class="op__tit">' + esc(o.titulo) + '</p><p class="op__txt">«' + esc(o.texto) + '»</p>' +
        '<div class="op__pie"><span class="op__ini" aria-hidden="true">' + esc((o.nombre || "?").charAt(0)) + '</span><span class="op__quien"><strong>' +
        esc(o.nombre) + '</strong><span>' + (esc(o.servicio) + (o.lugar ? " · " + esc(o.lugar) : "") || "Opinión publicada en Google") + '</span></span></div></li>';
    }).join("");
    cuentaOp();
  }
  function ponResenas(r) {
    if (!r || !r.resenas) return;
    ponOpiniones(r.opiniones);
    var nota = String(r.valoracion), num = String(r.resenas);
    d.querySelectorAll("[data-nota]").forEach(function (e) { e.textContent = nota; });
    d.querySelectorAll("[data-resenas]").forEach(function (e) { e.textContent = num; });
    d.querySelectorAll('[data-fuente="valoracion"]').forEach(function (e) { e.setAttribute("data-cuenta", nota); e.textContent = nota; });
    d.querySelectorAll('[data-fuente="resenas"]').forEach(function (e) { e.setAttribute("data-cuenta", num); e.textContent = num; });
    d.querySelectorAll('script[type="application/ld+json"]').forEach(function (s) {
      try {
        var j = JSON.parse(s.textContent), g = j["@graph"] || [j];
        g.forEach(function (n) { if (n.aggregateRating) { n.aggregateRating.ratingValue = nota.replace(",", "."); n.aggregateRating.reviewCount = parseInt(num, 10); } });
        s.textContent = JSON.stringify(j);
      } catch (e) {}
    });
  }
  w.__resenas = ("fetch" in w) ? fetch("/resenas.json", { cache: "no-cache" }).then(function (x) { return x.ok ? x.json() : null; }).then(ponResenas).catch(function () {}) : null;

  /* ---------- Formularios: sello de tiempo, recuperar lo escrito y avisos de vuelta ---------- */
  var q = w.location.search;
  function claveForm(f) { var t = f.querySelector('input[name="tipo"]'); return "gyf-form-" + (t ? t.value : (f.classList.contains("llamada__form") ? "llamada" : "contacto")); }
  function camposForm(f) { return [].filter.call(f.querySelectorAll("input[name], textarea[name]"), function (i) { return i.type !== "hidden" && i.type !== "checkbox" && i.name !== "web"; }); }
  d.addEventListener("submit", function (e) {
    var f = e.target, t = f.querySelector && f.querySelector('input[name="t"]');
    if (t) t.value = Math.round(w.performance && performance.now ? performance.now() : 0);
    if (!f.querySelectorAll) return;
    var datos = {}; camposForm(f).forEach(function (i) { datos[i.name] = i.value; });
    try { sessionStorage.setItem(claveForm(f), JSON.stringify(datos)); } catch (x) {}
  }, true);
  var errForm = /[?&](llamada|enviado)=0/.test(q), okForm = /[?&](llamada|enviado)=1/.test(q);
  if (errForm || okForm) d.querySelectorAll("form").forEach(function (f) {
    var k = claveForm(f);
    try {
      if (okForm) { sessionStorage.removeItem(k); return; }
      var datos = JSON.parse(sessionStorage.getItem(k) || "null"); if (!datos) return;
      camposForm(f).forEach(function (i) { if (datos[i.name] && !i.value) i.value = datos[i.name]; });
    } catch (x) {}
  });
  var ok = d.getElementById("form-ok"), ko = d.getElementById("form-error");
  if (ok && /enviado=1/.test(q)) {
    ok.hidden = false;
    d.querySelectorAll(".formulario").forEach(function (f) {
      if (f.contains(ok)) { [].forEach.call(f.children, function (ch) { if (ch !== ok) ch.hidden = true; }); f.classList.add("formulario--hecho"); }
      else f.hidden = true;
    });
  }
  if (ko && /enviado=0/.test(q)) ko.hidden = false;
  var lok = d.querySelector("[data-llamada-ok]"), lko = d.querySelector("[data-llamada-error]");
  if (lok && /llamada=1/.test(q)) {
    lok.hidden = false;
    var tj = lok.closest(".llamada") || d;
    tj.querySelectorAll(".llamada__form, .llamada__tit, [data-promesa]").forEach(function (x) { x.hidden = true; });
  }
  if (lko && /llamada=0/.test(q)) lko.hidden = false;
  var avisoVuelta = (ok && !ok.hidden && ok) || (ko && !ko.hidden && ko) || (lok && !lok.hidden && lok) || (lko && !lko.hidden && lko);
  if (avisoVuelta) {
    for (var pr = avisoVuelta; pr; pr = pr.parentElement) if (pr.classList && pr.classList.contains("rv")) pr.classList.add("dentro");
    if (w.requestAnimationFrame) requestAnimationFrame(function () { try { avisoVuelta.scrollIntoView({ block: "center" }); } catch (x) {} });
  }

  /* ---------- Cookies + GTM (solo en el dominio de producción) ---------- */
  var PROD = new RegExp("^(vinospousada\\.es|www\\.vinospousada\\.es)$").test(w.location.hostname);
  var GTM = html.getAttribute("data-gtm");
  w.dataLayer = w.dataLayer || [];
  function gtag() { w.dataLayer.push(arguments); }
  var CLAVE = "pousada-cookies";
  function leer() { try { return localStorage.getItem(CLAVE); } catch (e) { return null; } }
  function guardar(v) { try { localStorage.setItem(CLAVE, v); } catch (e) {} }
  var eleccion = leer();
  gtag("consent", "default", { ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied", analytics_storage: "denied", wait_for_update: 500 });
  if (eleccion === "si") aceptar(true);
  function aceptar(silencioso) {
    gtag("consent", "update", { ad_storage: "granted", ad_user_data: "granted", ad_personalization: "granted", analytics_storage: "granted" });
    if (!silencioso) guardar("si");
  }
  if (/llamada=1/.test(q)) w.dataLayer.push({ event: "solicitud_llamada", pagina: w.location.pathname });
  if (/enviado=1/.test(q)) w.dataLayer.push({ event: "formulario_enviado", pagina: w.location.pathname });
  if (/(llamada|enviado)=/.test(q) && w.history && history.replaceState) {
    try { history.replaceState(null, "", w.location.pathname + w.location.hash); } catch (e) {}
  }
  /* Medición: Llamar y WhatsApp (con la zona y si estamos en horario), reseñas de Google, «Déjenos su teléfono» y el CTA extra */
  var PAG = w.location.pathname;
  function ubicacion(a) {
    var zona = a.closest("[data-zona], .cab, .menu, .portada-a, .cab-int, .tarjeta, .llamada, .banda, .horario, .faq, .mapa, .lectura, .pie, .barra-movil, section");
    return zona ? (zona.getAttribute("data-zona") || zona.className.split(" ")[0]) : "otro";
  }
  d.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (!a) return;
    var href = a.getAttribute("href");
    if (/^tel:/.test(href) || /wa\.me\//.test(href)) {
      w.dataLayer.push({ event: /^tel:/.test(href) ? "click_llamar" : "click_whatsapp", ubicacion: ubicacion(a), pagina: PAG, abierto: ABIERTO === true });
    } else if (/maps\.google\.com\/\?cid/.test(href)) {
      w.dataLayer.push({ event: "click_resenas_google", ubicacion: ubicacion(a), pagina: PAG });
    } else if (a.classList.contains("tarjeta__ir")) {
      w.dataLayer.push({ event: "click_te_llamamos", pagina: PAG });
    } else if (a.matches(".tarjeta__extra, .banda__extra, .mini__extra")) {
      w.dataLayer.push({ event: "click_cta_extra", ubicacion: ubicacion(a), destino: href, pagina: PAG });
    }
  }, true);
  function tipoForm(f) { var t = f.querySelector('input[name="tipo"]'); return t ? t.value : (f.classList.contains("llamada__form") ? "llamada" : "contacto"); }
  d.addEventListener("focusin", function (e) {
    var f = e.target.form; if (!f || f._inicio || !/^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName) || e.target.type === "hidden") return;
    f._inicio = true;
    w.dataLayer.push({ event: "form_inicio", formulario: tipoForm(f), campo: e.target.name || "", pagina: PAG });
  });
  d.addEventListener("invalid", function (e) {
    var f = e.target.form; if (!f) return;
    var ahora = Date.now(); if (f._err && ahora - f._err < 800) return;
    f._err = ahora;
    w.dataLayer.push({ event: "form_error", formulario: tipoForm(f), campo: e.target.name || "", motivo: "validacion", pagina: PAG });
  }, true);
  var mq = /[?&](llamada|enviado)=0/.exec(q);
  if (mq) {
    var mm = /[?&]motivo=([a-z_\-]+)/i.exec(q);
    w.dataLayer.push({ event: "form_error", formulario: mq[1] === "llamada" ? "llamada" : "contacto", motivo: mm ? mm[1] : "servidor", pagina: PAG });
  }
  if (PROD && GTM) {
    w.dataLayer.push({ "gtm.start": Date.now(), event: "gtm.js" });
    var s = d.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtm.js?id=" + GTM;
    d.head.appendChild(s);
  }
  var aviso = d.getElementById("cookies");
  if (aviso && !eleccion) aviso.classList.add("visible");
  d.addEventListener("click", function (e) {
    var b = e.target.closest("[data-cookies]");
    if (!b) return;
    if (b.getAttribute("data-cookies") === "si") aceptar(false); else guardar("no");
    if (aviso) aviso.classList.remove("visible");
  });
  d.querySelectorAll("[data-cookies-config]").forEach(function (a) {
    a.addEventListener("click", function (e) { e.preventDefault(); if (aviso) aviso.classList.add("visible"); });
  });

  /* ---------- Barra fija del móvil: fuera mientras se ven los botones de la cabecera de la página ---------- */
  var barra = d.querySelector(".barra-movil"), accPortada = d.querySelector(".portada-a__top .acciones, .cab-int .acciones, [data-acciones]");
  if (barra && accPortada && "IntersectionObserver" in w) {
    new IntersectionObserver(function (ents) {
      barra.classList.toggle("barra-movil--fuera", ents[ents.length - 1].isIntersecting);
    }, { rootMargin: "0px 0px -88px 0px" }).observe(accPortada);
  }

  /* ---------- FAQ: una abierta a la vez (respaldo de <details name>) ---------- */
  d.querySelectorAll(".faq__lista").forEach(function (l) {
    l.addEventListener("toggle", function (e) {
      if (!e.target.open) return;
      l.querySelectorAll("details[open]").forEach(function (x) { if (x !== e.target) x.open = false; });
    }, true);
  });

  /* ---------- Índice de las interiores: plegado en móvil y enlace activo al leer ---------- */
  var indice = d.querySelector("[data-indice]");
  if (indice) {
    if (ancho() < 1200) indice.open = false;
    var enl = [].slice.call(indice.querySelectorAll("a[href^='#']"));
    if ("IntersectionObserver" in w) {
      var ioI = new IntersectionObserver(function (ents) {
        ents.forEach(function (en) {
          if (!en.isIntersecting) return;
          enl.forEach(function (a) { a.classList.toggle("activo", a.getAttribute("href") === "#" + en.target.id); });
        });
      }, { rootMargin: "-30% 0px -60% 0px" });
      enl.forEach(function (a) { var t = d.getElementById(a.getAttribute("href").slice(1)); if (t) ioI.observe(t); });
    }
  }

  /* ---------- Opiniones: flechas y contador «1 / N» (R33, sin automático) ---------- */
  var opl = d.querySelector("[data-opiniones]"), opc = d.querySelector("[data-op-cuenta]");
  function cuentaOp() {
    if (!opl || !opc) return;
    var li = opl.querySelector(".op"); if (!li) return;
    var n = opl.querySelectorAll(".op").length, i = Math.round(opl.scrollLeft / (li.offsetWidth + 24));
    opc.textContent = Math.min(n, i + 1) + " / " + n;
  }
  if (opl) opl.addEventListener("scroll", function () { w.requestAnimationFrame(cuentaOp); }, { passive: true });
  d.querySelectorAll("[data-op]").forEach(function (b) {
    b.addEventListener("click", function () {
      var li = opl && opl.querySelector(".op");
      if (li) opl.scrollBy({ left: parseInt(b.getAttribute("data-op"), 10) * (li.offsetWidth + 24), behavior: reducido ? "auto" : "smooth" });
    });
  });

  /* ---------- R23 · La foto sigue al cursor en las filas de servicios (solo ordenador) ---------- */
  var cf = d.querySelector("[data-cursor-foto]");
  if (cf && raton && !reducido && ancho() >= 1000) {
    var actual = null;
    d.querySelectorAll("[data-sigue] .fila.con-foto").forEach(function (li) {
      li.addEventListener("mouseenter", function () {
        var pic = li.querySelector(".fila__foto picture");
        if (pic && actual !== li) { cf.innerHTML = ""; cf.appendChild(pic.cloneNode(true)); actual = li; }
        cf.classList.add("visible");
      });
      li.addEventListener("mouseleave", function () { cf.classList.remove("visible"); });
      li.addEventListener("mousemove", function (e) {
        cf.style.setProperty("--x", (e.clientX - 140) + "px");
        cf.style.setProperty("--y", (e.clientY - 272) + "px");
      });
    });
  }

  /* ---------- R32 · Contadores: cuentan al entrar (sin odómetro); respetan la coma decimal ---------- */
  function cuenta(el) {
    var v = el.getAttribute("data-cuenta") || "", n = parseFloat(v.replace(",", ".")), dec = (v.split(/[.,]/)[1] || "").length;
    if (isNaN(n) || reducido) return;
    var t0 = null, dur = 1400;
    function paso(t) {
      if (!t0) t0 = t;
      var k = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = (n * e).toFixed(dec).replace(".", ",");
      if (k < 1) requestAnimationFrame(paso); else el.textContent = v;
    }
    requestAnimationFrame(paso);
  }

  /* ---------- R18 / R20 · Apariciones: una sola vez; las que entran juntas, escalonadas ---------- */
  var rv = d.querySelectorAll(".rv");
  if (reducido || !("IntersectionObserver" in w)) {
    rv.forEach(function (el) { el.classList.add("dentro"); });
  } else {
    var io = new IntersectionObserver(function (ents) {
      var k = 0;
      ents.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.style.setProperty("--d", (k++ * .08) + "s");
        en.target.classList.add("dentro"); io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    rv.forEach(function (el) { io.observe(el); });
    var ioC = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) { if (en.isIntersecting) { cuenta(en.target); ioC.unobserve(en.target); } });
    }, { threshold: .6 });
    var arrancaCuentas = function () { d.querySelectorAll("[data-cuenta]").forEach(function (el) { ioC.observe(el); }); };
    if (w.__resenas) w.__resenas.then(arrancaCuentas, arrancaCuentas); else arrancaCuentas();
  }

  /* =================== Carga diferida: GSAP (capa de Rayo) y el objeto 3D ===================
     Se cargan cuando la página ya ha terminado de cargar, para no quitarle ancho de banda a la portada. */
  function carga(lista, fin) {
    if (!lista.length) return fin();
    var sc = d.createElement("script"); sc.src = lista[0]; sc.async = false;
    sc.onload = function () { carga(lista.slice(1), fin); }; sc.onerror = function () { carga(lista.slice(1), fin); };
    d.body.appendChild(sc);
  }
  function arranca() {
    if (!reducido) carga(["/js/vendor/gsap.min.js", "/js/vendor/ScrollTrigger.min.js", "/js/vendor/lenis.min.js"], capa);
    objeto3d();
  }
  if (d.readyState === "complete") arranca(); else w.addEventListener("load", arranca);

  /* Objeto 3D (tipo «3d» en config.py): solo ordenador, sin movimiento reducido y con WebGL. La imagen fija
     de debajo es el LCP; el lienzo se funde encima cuando ya ha pintado el primer fotograma. */
  function objeto3d() {
    var el = d.querySelector("[data-objeto3d]");
    if (!el || reducido || !raton || ancho() < 900) return;
    try { var cv = d.createElement("canvas"); if (!(cv.getContext("webgl2") || cv.getContext("webgl"))) return; } catch (e) { return; }
    var ya = function () {
      carga(["/js/vendor/objeto3d.min.js"], function () {
        if (!w.Objeto3D) return;
        w.Objeto3D.montar(el.querySelector(".objeto__lienzo"), {
          svg: el.getAttribute("data-objeto3d"), color: el.getAttribute("data-color") || null,
          listo: function () { requestAnimationFrame(function () { el.classList.add("con-3d"); }); }
        }).catch(function () {});
      });
    };
    if ("requestIdleCallback" in w) w.requestIdleCallback(ya, { timeout: 2500 }); else setTimeout(ya, 800);
  }

  /* Divide en palabras los nodos de texto de un elemento (conserva enlaces y negritas) */
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
        } else if (c.nodeType === 1) rec(c);
      });
    })(el);
    return out;
  }

  function capa() {
    var G = w.gsap, ST = w.ScrollTrigger;
    if (!G || !ST) return;
    G.registerPlugin(ST);

    /* R3 · Scroll suave solo en ordenador. En táctil, el nativo. */
    if (raton && w.Lenis && ancho() > 1080) {
      var lenis = w.__lenis = new w.Lenis({ lerp: .1 });
      lenis.on("scroll", ST.update);
      G.ticker.add(function (t) { lenis.raf(t * 1000); });
      G.ticker.lagSmoothing(0);
      d.querySelectorAll('a[href^="#"]').forEach(function (a) {
        a.addEventListener("click", function (e) {
          var id = a.getAttribute("href"); if (id.length < 2) return;
          var t = d.querySelector(id); if (!t) return;
          e.preventDefault(); lenis.scrollTo(t, { offset: -100, duration: 1 });
        });
      });
    }

    /* R14 · Cintas: avanzan solas (30 s por grupo) y se aceleran con la velocidad del scroll (×1 a ×6) */
    d.querySelectorAll("[data-cinta]").forEach(function (p) {
      var dir = parseFloat(p.getAttribute("data-cinta")) || -1;
      var tw = dir < 0 ? G.to(p, { xPercent: -50, duration: 30, ease: "none", repeat: -1 })
                       : G.fromTo(p, { xPercent: -50 }, { xPercent: 0, duration: 30, ease: "none", repeat: -1 });
      var vuelta;
      ST.create({
        trigger: p.parentNode, start: "top bottom", end: "bottom top",
        onToggle: function (s) { tw.paused(!s.isActive); },
        onUpdate: function (s) {
          var v = Math.min(6, Math.max(1, Math.abs(s.getVelocity()) / 200));
          G.to(tw, { timeScale: v, duration: .2, overwrite: true });
          if (vuelta) vuelta.kill();
          vuelta = G.to(tw, { timeScale: 1, duration: 1.5, delay: .25 });
        }
      });
    });

    /* R5 · Portada fija: la galería sube por encima; la frase, los servicios y la tarjeta salen hacia arriba
       estirándose y, al final, toda la capa se funde. Solo con la portada fija (ordenador con altura suficiente). */
    var hero = d.querySelector(".hero--galeria"), gal = hero && hero.querySelector("[data-galeria]");
    if (gal && w.matchMedia("(min-width: 900px) and (min-height: 800px)").matches) {
      G.to(hero.querySelectorAll("[data-sale]"), { y: -80, scaleY: 1.3, opacity: 0, transformOrigin: "50% 0%", ease: "sine.in",
        scrollTrigger: { trigger: gal, start: "top 92%", end: "top 38%", scrub: true } });
      G.to(hero.querySelector(".portada-a__centro"), { opacity: 0, ease: "none",
        scrollTrigger: { trigger: gal, start: "bottom 150%", end: "bottom 100%", scrub: true } });
    }
    /* R22 · Paralaje de las fotos dentro de su marco (×1,2) */
    d.querySelectorAll(".caso__foto img").forEach(function (im) {
      G.fromTo(im, { yPercent: -7 }, { yPercent: 7, ease: "none", scrollTrigger: { trigger: im.closest(".caso"), start: "top bottom", end: "bottom top", scrub: true } });
    });

    /* R11 · Palabras que se encienden: la segunda mitad gris de los H2 y el manifiesto. En táctil, sin scrub. */
    d.querySelectorAll(".enciende").forEach(function (el) {
      var obj = el.classList.contains("h2") ? el.querySelector(".gris") : el;
      if (!obj) return;
      var pals = palabras(obj);
      var larga = !el.classList.contains("h2");
      if (raton) {
        G.fromTo(pals, { opacity: .2 }, { opacity: 1, stagger: .1, ease: "none",
          scrollTrigger: { trigger: el, start: "top 85%", end: larga ? "bottom 55%" : "top 40%", scrub: true } });
      } else {
        G.fromTo(pals, { opacity: .2 }, { opacity: 1, stagger: .05, duration: .5, ease: "power1.out", scrollTrigger: { trigger: el, start: "top 80%" } });
      }
    });

    /* R21 · La banda final se abre: el fondo pasa de scaleX 1,14 y radio 200 a su sitio (el texto no se deforma) */
    d.querySelectorAll("[data-abre] .banda__fondo").forEach(function (f) {
      var r = getComputedStyle(f).borderTopLeftRadius;
      G.fromTo(f, { scaleX: 1.14, borderRadius: 200 }, { scaleX: 1, borderRadius: r, ease: "power4.inOut",
        scrollTrigger: { trigger: f.parentNode, start: "top 82%", end: "top 14%", scrub: true } });
    });

    /* R25 · El sello de Google gira con el scroll */
    d.querySelectorAll("[data-gira]").forEach(function (s) {
      G.to(s, { rotation: 300, transformOrigin: "50% 50%", ease: "none", scrollTrigger: { trigger: s, start: "top bottom", end: "bottom top", scrub: true } });
    });

    ST.refresh();
    /* El tema (cliente/js/tema.js) engancha aquí su capa de movimiento: ya hay GSAP + ScrollTrigger (y Lenis si toca) */
    html.classList.add("con-gsap");
    try { d.dispatchEvent(new CustomEvent("gyf:capa", { detail: { gsap: G, ScrollTrigger: ST, lenis: w.__lenis || null, raton: raton } })); } catch (e) {}
  }
})();
