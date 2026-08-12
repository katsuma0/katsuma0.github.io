/* appearance.js: the shared dress for every site on the origin.
   Loaded synchronously in <head> so the data attributes land on <html>
   before first paint. Reads the one shared localStorage key
   'outdoors-appearance' and stamps only the non-default values:
     data-theme     light | dark          (auto stamps nothing)
     data-glass     off                   (on is the default)
     data-palette   field | granite       (shore is the default)
     data-face      rounded | serif | avenir | mono
     data-textsize  s | l | xl            (m is the default)
   With JavaScript off, or localStorage unavailable, nothing is stamped
   and the CSS defaults stand: auto theme, glass on, shore, system, m.
   The second half wires the blended header: .ios-header and .nav get
   the 'scrolled' class past 8px of scroll and lose it back at the top. */
(function () {
  var root = document.documentElement;
  try {
    var s = JSON.parse(localStorage.getItem('outdoors-appearance')) || {};
    if (s.theme === 'light' || s.theme === 'dark') root.setAttribute('data-theme', s.theme);
    if (s.glass === 'off') root.setAttribute('data-glass', 'off');
    if (s.palette === 'field' || s.palette === 'granite') root.setAttribute('data-palette', s.palette);
    if (s.face === 'rounded' || s.face === 'serif' || s.face === 'avenir' || s.face === 'mono') root.setAttribute('data-face', s.face);
    if (s.size === 's' || s.size === 'l' || s.size === 'xl') root.setAttribute('data-textsize', s.size);
  } catch (e) { /* no storage: the defaults stand */ }

  function wire() {
    var bars = document.querySelectorAll('.ios-header, .nav');
    if (!bars.length) return;
    var update = function () {
      var on = (window.scrollY || root.scrollTop || 0) > 8;
      for (var i = 0; i < bars.length; i++) bars[i].classList.toggle('scrolled', on);
    };
    window.addEventListener('scroll', update, { passive: true });
    update();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wire);
  } else {
    wire();
  }
})();
