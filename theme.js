/* Dark-mode toggle.
 *
 * Three states, deliberately: dark, light, and "whatever the system says".
 * A site that ignores the reader's OS setting is annoying, and a site that
 * ignores their explicit choice is worse - so an explicit choice wins and is
 * remembered, and until one is made the system decides and keeps deciding as
 * it changes through the day.
 *
 * The attribute itself is set by a tiny inline snippet in each page's <head>,
 * before anything paints. If it were set from here - a deferred script - every
 * dark-mode reader would get a white flash on every page load.
 *
 * presentation.html is skipped: it is a dark show already.
 *
 * Loaded by nav.js on every page.
 */
(function () {
  'use strict';

  if (/presentation\.html$/.test(location.pathname)) return;

  var KEY = 'ruhama.theme';
  var lang = new URLSearchParams(location.search).get('lang') === 'en' ? 'en' : 'he';
  var L = {
    he: { dark: 'מצב כהה', light: 'מצב בהיר', auto: 'לפי המערכת' },
    en: { dark: 'Dark', light: 'Light', auto: 'System' }
  }[lang];

  var mq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function store(v) {
    try { v ? localStorage.setItem(KEY, v) : localStorage.removeItem(KEY); } catch (e) {}
  }

  function effective() {
    var s = stored();
    if (s === 'dark' || s === 'light') return s;
    return mq && mq.matches ? 'dark' : 'light';
  }

  function apply() {
    document.documentElement.setAttribute('data-theme', effective());
  }

  /* Follow the system while no explicit choice has been made. */
  if (mq && mq.addEventListener) {
    mq.addEventListener('change', function () { if (!stored()) { apply(); paint(); } });
  }

  var btn = null;
  function paint() {
    if (!btn) return;
    var s = stored();
    var now = effective();
    btn.querySelector('.ico').textContent = now === 'dark' ? '☾' : '☀';
    btn.querySelector('.txt').textContent = s ? (s === 'dark' ? L.dark : L.light) : L.auto;
    btn.title = btn.querySelector('.txt').textContent;
    btn.setAttribute('aria-pressed', now === 'dark' ? 'true' : 'false');
  }

  function build() {
    var nav = document.getElementById('sitenav');
    if (!nav) return;
    btn = document.createElement('button');
    btn.id = 'themebtn';
    btn.type = 'button';
    btn.innerHTML = '<span class="ico"></span><span class="txt"></span>';
    btn.addEventListener('click', function () {
      /* cycle: system -> dark -> light -> system */
      var s = stored();
      var next = !s ? (effective() === 'dark' ? 'light' : 'dark')
               : s === 'dark' ? 'light'
               : null;
      store(next);
      apply();
      paint();
      if (window.gtag) gtag('event', 'theme_change', { theme: next || 'system' });
    });
    nav.appendChild(btn);
    paint();
    /* only now allow colour transitions, so the first paint is instant */
    requestAnimationFrame(function () {
      document.documentElement.classList.add('theme-ready');
    });
  }

  apply();
  if (document.getElementById('sitenav')) build();
  else document.addEventListener('DOMContentLoaded', build);
})();
