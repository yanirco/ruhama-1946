/* Shared navigation for every page on ruhama1946.site.
 *
 * Before this, each page did its own thing: the article had a link bar, the
 * gallery had a single "back" link, and the timeline, slides and presentation
 * had no way out at all except the browser's back button. This puts the same
 * bar on all of them, from one file, so adding a page means editing one list.
 *
 * Include near the end of <body>:   <script src="nav.js" defer></script>
 *
 * Language: the pages are Hebrew by default and English on ?lang=en. Every
 * link built here carries the current language forward, so switching page
 * never silently switches language back to Hebrew.
 */
(function () {
  'use strict';

  var PAGES = [
    { href: '/',                 he: 'הסיפור',          en: 'The story' },
    { href: 'gallery.html',      he: 'גלריה',           en: 'Gallery' },
    { href: 'timeline.html',     he: 'ציר זמן',         en: 'Timeline' },
    { href: 'slides.html',       he: 'סדרת הסיפור',     en: 'Story slides' },
    { href: 'presentation.html', he: 'מצגת למסך גדול',  en: 'Presentation' }
  ];

  var params = new URLSearchParams(location.search);
  var lang = params.get('lang') === 'en' ? 'en' : 'he';
  var rtl = lang === 'he';

  /* Which page are we on? Compare the last path segment, treating "" and
     "index.html" as the same thing. */
  var here = location.pathname.replace(/^.*\//, '') || 'index.html';
  function isCurrent(href) {
    var t = href.replace(/^\//, '').replace(/\?.*$/, '') || 'index.html';
    return t === here;
  }
  function withLang(href) {
    return lang === 'en' ? href + (href.indexOf('?') > -1 ? '&' : '?') + 'lang=en'
                         : href;
  }

  var css = document.createElement('style');
  css.textContent = [
    '#sitenav{position:sticky;top:0;z-index:40;display:flex;align-items:center;',
    '  gap:4px;padding:9px 16px;background:rgba(10,11,13,.92);',
    '  backdrop-filter:blur(10px);border-bottom:1px solid rgba(255,255,255,.10);',
    '  font-family:"Assistant","Helvetica Neue",Arial,sans-serif;font-size:14px;',
    '  overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}',
    '#sitenav::-webkit-scrollbar{display:none}',
    '#sitenav .home{font-weight:600;color:#f2efe9;text-decoration:none;',
    '  white-space:nowrap;margin-inline-end:14px;letter-spacing:.01em}',
    '#sitenav a{color:#a8a49c;text-decoration:none;white-space:nowrap;',
    '  padding:6px 11px;border-radius:8px;transition:color .15s,background .15s}',
    '#sitenav a:hover{color:#d9b64a;background:rgba(255,255,255,.06)}',
    '#sitenav a[aria-current="page"]{color:#c9a227;background:rgba(201,162,39,.13)}',
    '#sitenav .spacer{flex:1 1 auto;min-width:8px}',
    '#sitenav .lang{border:1px solid rgba(255,255,255,.2);color:#f2efe9}',
    '#sitenav .lang:hover{border-color:#c9a227}',
    /* the presentation is a full-bleed show - let its idle timer hide this too */
    'body.idle #sitenav{opacity:0;pointer-events:none;transition:opacity .45s}',
    '@media print{#sitenav{display:none}}'
  ].join('');
  document.head.appendChild(css);

  var nav = document.createElement('nav');
  nav.id = 'sitenav';
  nav.setAttribute('aria-label', rtl ? 'ניווט באתר' : 'Site navigation');
  nav.dir = rtl ? 'rtl' : 'ltr';

  var home = document.createElement('a');
  home.className = 'home';
  home.href = withLang('/');
  home.textContent = rtl ? 'רוחמה 1946' : 'Ruhama 1946';
  nav.appendChild(home);

  PAGES.forEach(function (p) {
    var a = document.createElement('a');
    a.href = withLang(p.href);
    a.textContent = p[lang];
    if (isCurrent(p.href)) a.setAttribute('aria-current', 'page');
    nav.appendChild(a);
  });

  var sp = document.createElement('span');
  sp.className = 'spacer';
  nav.appendChild(sp);

  /* Language toggle: same page, other language. */
  var alt = document.createElement('a');
  alt.className = 'lang';
  var q = new URLSearchParams(location.search);
  if (lang === 'en') { q.delete('lang'); } else { q.set('lang', 'en'); }
  var qs = q.toString();
  alt.href = location.pathname + (qs ? '?' + qs : '');
  alt.textContent = lang === 'en' ? 'עברית' : 'English';
  alt.setAttribute('rel', 'alternate');
  nav.appendChild(alt);

  document.body.insertBefore(nav, document.body.firstChild);

  /* The ambient-music toggle appends itself to this bar, once it has confirmed
     the track exists. Loaded after the nav so it always has somewhere to go. */
  var amb = document.createElement('script');
  amb.src = 'ambient.js';
  amb.defer = true;
  document.body.appendChild(amb);
})();
