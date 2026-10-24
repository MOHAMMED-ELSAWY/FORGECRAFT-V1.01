/* FORGE site scripts: menu, contact form, WhatsApp. No tracking, no storage. */
(function () {
  var CFG = window.FORGE_CONFIG || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var L = window.FORGE_STRINGS || {};

  /* toast */
  var toastTimer;
  function toast(msg) {
    var el = $("#toast"); if (!el) return;
    el.textContent = msg; el.classList.add("show");
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { el.classList.remove("show"); }, 4500);
  }

  /* mobile menu */
  var btn = $("#menu-btn"), menu = $("#mobile-menu");
  function setMenu(open) {
    if (!btn || !menu) return;
    menu.hidden = !open; btn.setAttribute("aria-expanded", String(open));
    $("#menu-label").textContent = open ? L.menuClose : L.menuOpen;
  }
  if (btn) {
    btn.addEventListener("click", function () { setMenu(btn.getAttribute("aria-expanded") !== "true"); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !menu.hidden) { setMenu(false); btn.focus(); } });
    document.addEventListener("click", function (e) { if (!menu.hidden && !e.target.closest(".site-header")) setMenu(false); });
  }

  /* WhatsApp links */
  function waHref(text) {
    var n = String(CFG.whatsapp || "").replace(/\D/g, "");
    return n ? "https://wa.me/" + n + "?text=" + encodeURIComponent(text) : "";
  }
  $$("[data-whatsapp]").forEach(function (a) {
    var href = waHref(L.waText || "");
    if (href) { a.href = href; a.target = "_blank"; a.rel = "noopener noreferrer"; }
    else a.addEventListener("click", function (e) { e.preventDefault(); toast(L.waMissing); });
  });

  /* contact form */
  var form = $("#contact-form");
  if (!form) return;
  var fields = { name: $("#f-name"), email: $("#f-email"), phone: $("#f-phone"), service: $("#f-service"), message: $("#f-message") };
  var status = $("#form-status");

  /* prefill from ?service=web */
  var params = new URLSearchParams(location.search);
  var svc = params.get("service");
  if (svc && L.prefill && L.prefill[svc]) {
    if (fields.service) fields.service.value = svc;
    if (!fields.message.value) fields.message.value = L.prefill[svc];
  }
  var proj = params.get("project");
  if (proj && L.prefill && L.prefill[proj] && !fields.message.value) fields.message.value = L.prefill[proj];

  function setErr(input, msg) {
    input.setAttribute("aria-invalid", "true");
    var e = $("#" + input.id + "-err"); if (e) e.textContent = msg;
  }
  function clearErr(input) {
    input.removeAttribute("aria-invalid");
    var e = $("#" + input.id + "-err"); if (e) e.textContent = "";
  }
  Object.keys(fields).forEach(function (k) { if (fields[k]) fields[k].addEventListener("input", function () { clearErr(fields[k]); }); });

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    Object.keys(fields).forEach(function (k) { if (fields[k]) clearErr(fields[k]); });
    status.textContent = "";
    var bad = [];
    if (fields.name.value.trim().length < 2) { setErr(fields.name, L.errName); bad.push(fields.name); }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(fields.email.value.trim())) { setErr(fields.email, L.errEmail); bad.push(fields.email); }
    if (fields.phone.value.trim() && !/^[+0-9()\s.-]{7,24}$/.test(fields.phone.value.trim())) { setErr(fields.phone, L.errPhone); bad.push(fields.phone); }
    if (fields.message.value.trim().length < 10) { setErr(fields.message, L.errMessage); bad.push(fields.message); }
    if (bad.length) { status.textContent = L.errSummary; bad[0].focus(); return; }

    var data = {
      name: fields.name.value.trim(), email: fields.email.value.trim(), phone: fields.phone.value.trim(),
      service: fields.service ? fields.service.value : "", message: fields.message.value.trim(), page: location.href
    };

    /* 1) real backend if configured (Formspree, Netlify Forms endpoint, your own API) */
    if (CFG.formEndpoint) {
      var submit = $("button[type=submit]", form); submit.disabled = true;
      fetch(CFG.formEndpoint, { method: "POST", headers: { "Content-Type": "application/json", "Accept": "application/json" }, body: JSON.stringify(data) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); status.textContent = L.sent; form.reset(); })
        .catch(function () { status.textContent = L.sendFailed; })
        .then(function () { submit.disabled = false; });
      return;
    }
    /* 2) fallback: prepare an email in the visitor's mail app */
    var body = [L.bName + ": " + data.name, L.bEmail + ": " + data.email, L.bPhone + ": " + (data.phone || "-"),
      L.bService + ": " + (data.service || "-"), "", L.bMessage + ":", data.message].join("\n");
    status.textContent = L.mailReady;
    location.href = "mailto:" + CFG.email + "?subject=" + encodeURIComponent(L.subject.replace("{name}", data.name)) + "&body=" + encodeURIComponent(body);
  });
})();
