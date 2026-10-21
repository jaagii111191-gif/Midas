// Shared fill-in helpers for the Midas Motors poster templates.
// Each template defines window.renderPoster(data) with these and sets window.posterReady when done.
(function () {
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }
  // Fill a .ph frame with a photo (path/URL), cropped with object-position and optional zoom.
  // fit "contain" shows the whole photo (no crop) over a blurred, darkened copy of itself;
  // useful for tightly framed 4:3 auction photos in wide frames.
  async function photo(frame, src, pos, scale, fit) {
    frame.innerHTML = "";
    if (!src) { frame.innerHTML = '<span class="missing">ЗУРАГ</span>'; return; }
    const imgs = [];
    if (fit === "contain") {
      const bg = document.createElement("img");
      bg.alt = ""; bg.className = "bg"; bg.src = src;
      frame.appendChild(bg); imgs.push(bg);
    }
    const img = document.createElement("img");
    img.alt = "";
    if (fit === "contain") img.className = "fg";
    img.style.objectPosition = pos || "50% 55%";
    if (scale && scale !== 1) { img.style.transform = "scale(" + scale + ")"; img.style.transformOrigin = pos || "50% 55%"; }
    img.src = src;
    frame.appendChild(img); imgs.push(img);
    try { await Promise.all(imgs.map(i => i.decode())); } catch (e) { window.posterErrors = (window.posterErrors || 0) + 1; console.error("photo failed to load: " + src); }
  }
  // Photos may be given as strings or {src, pos, scale, label}.
  function photoList(d) {
    const list = d.photos && d.photos.length ? d.photos : (d.photo ? [d.photo] : []);
    return list.map(p => (typeof p === "string" ? { src: p } : p));
  }
  function badge(el, type, text) {
    el.className = "badge chamfer " + (type || "new");
    el.textContent = text || "";
    el.hidden = !text;
  }
  function modelHtml(d) { return esc(d.model) + (d.gen ? ' <span class="gen">' + esc(d.gen) + "</span>" : ""); }
  function years(d) { return [d.year_made, d.year_import].filter(Boolean).join("/"); }
  function subHtml(d) {
    return [d.trim ? "<b>" + esc(d.trim) + "</b>" : "", esc(years(d)), esc(d.color)].filter(Boolean).join(" · ");
  }
  function specsHtml(list) {
    return (list || []).slice(0, 4).map(s => '<div><span class="k">' + esc(s[0]) + '</span><span class="v">' + esc(s[1]) + "</span></div>").join("");
  }
  function priceHtml(d) {
    return (d.price_old ? '<span class="was">' + esc(d.price_old) + " сая₮</span>" : '<span class="k">Үнэ</span>') +
      '<span class="v">' + esc(d.price) + "<small>сая₮</small></span>";
  }
  function lease(el, d) {
    el.innerHTML = "<b>" + esc(d.lease_title) + "</b><span>" + esc(d.lease_sub) + "</span>";
    el.hidden = !d.lease_title;
  }
  // Optional d.credit, e.g. the site example photos came from.
  async function done(d) {
    const poster = document.getElementById("poster");
    const old = poster && poster.querySelector(".credit");
    if (old) old.remove();
    if (poster && d && d.credit) poster.insertAdjacentHTML("beforeend", '<div class="credit">' + esc(d.credit) + "</div>");
    await document.fonts.ready;
    window.posterReady = true;
  }
  window.MM = { esc, photo, photoList, badge, modelHtml, years, subHtml, specsHtml, priceHtml, lease, done };
})();
