(function () {
  var root = document.documentElement;

  // Isi cangkir (dan progress bar di layar kecil) mengikuti posisi scroll.
  function updateScroll() {
    var max = root.scrollHeight - window.innerHeight;
    var p = max > 0 ? Math.min(1, Math.max(0, window.scrollY / max)) : 0;
    root.style.setProperty("--p", p.toFixed(3));
  }
  window.addEventListener("scroll", updateScroll, { passive: true });
  window.addEventListener("resize", updateScroll);
  updateScroll();

  // Tandai menu yang sesuai dengan bagian yang sedang dibaca.
  var links = document.querySelectorAll(".rail nav a");
  var sections = Array.prototype.map.call(links, function (a) {
    return document.querySelector(a.getAttribute("href"));
  });

  function updateNav() {
    var current = null;
    sections.forEach(function (s, i) {
      if (s && s.getBoundingClientRect().top <= window.innerHeight * 0.35) current = i;
    });
    // Di dasar halaman, bagian terakhir (Kontak) yang dianggap aktif.
    if (window.innerHeight + window.scrollY >= root.scrollHeight - 4) current = sections.length - 1;
    links.forEach(function (a, i) {
      if (i === current) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
  }
  window.addEventListener("scroll", updateNav, { passive: true });
  updateNav();

  // Tahun di footer.
  var year = document.getElementById("tahun");
  if (year) year.textContent = new Date().getFullYear();
})();