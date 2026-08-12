/* appearance.js: the shared dress for every site on the origin.
   Loaded synchronously in <head> so the data attributes land on <html>
   before first paint. Reads the one shared localStorage key
   'outdoors-appearance' and stamps only the non-default values:
     data-theme     light | dark          (auto stamps nothing)
     data-glass     off                   (on is the default)
     data-palette   field | granite       (parks is the default)
     data-face      system | rounded | serif | avenir | mono
                                          (parks is the default)
     data-textsize  s | l | xl            (m is the default)
   With JavaScript off, or localStorage unavailable, nothing is stamped
   and the CSS defaults stand: auto theme, glass on, the parks palette
   and face, m.
   The second half wires the blended header: .ios-header and .nav get
   the 'scrolled' class past 8px of scroll and lose it back at the top. */
(function () {
  var root = document.documentElement;
  try {
    var key = 'outdoors-appearance';
    var s = JSON.parse(localStorage.getItem(key)) || {};
    /* one-time moves. the last round saved face:"system" as the default
       for anyone who touched a panel; those users follow the new parks
       default. a system choice made after this round carries v2, so it
       sticks. the shore palette is renamed parks. */
    var moved = false;
    if (s.face === 'system' && !s.v2) { delete s.face; s.v2 = 1; moved = true; }
    if (s.palette === 'shore') { s.palette = 'parks'; moved = true; }
    if (moved) localStorage.setItem(key, JSON.stringify(s));
    if (s.theme === 'light' || s.theme === 'dark') root.setAttribute('data-theme', s.theme);
    if (s.glass === 'off') root.setAttribute('data-glass', 'off');
    if (s.palette === 'field' || s.palette === 'granite') root.setAttribute('data-palette', s.palette);
    if (s.face === 'system' || s.face === 'rounded' || s.face === 'serif' || s.face === 'avenir' || s.face === 'mono') root.setAttribute('data-face', s.face);
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
