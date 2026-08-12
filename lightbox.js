/* Click any picture to see it full size.
 *
 * This is an in-page overlay, not window.open() - nothing for a pop-up blocker
 * to block, no new tab, and the back button still does what the reader expects.
 *
 * Behaviour:
 *   click an image      open it at full size
 *   Esc, or the X,      close
 *     or the backdrop
 *   left / right arrow  step through every picture on the page
 *
 * Two things it is careful about:
 *
 *   THE LABEL TRAVELS WITH THE PICTURE. A drawing opened full-screen still says
 *   it is a drawing. The whole point of the labelling scheme is that it cannot
 *   be separated from the image, and a lightbox that dropped it would be the
 *   easiest place to lose it.
 *
 *   IT LEAVES THE GALLERY ALONE. gallery.html has its own viewer with filters
 *   and its own arrow logic; two lightboxes fighting over one click is worse
 *   than either.
 *
 * Loaded by nav.js on every page.
 */
(function () {
  'use strict';

  if (document.getElementById('lb')) return;                 // already present
  if (/gallery\.html$/.test(location.pathname)) return;      // has its own

  var lang = new URLSearchParams(location.search).get('lang') === 'en' ? 'en' : 'he';
  var rtl = lang === 'he';
  var L = {
    he: { close: 'סגירה', prev: 'הקודם', next: 'הבא', of: 'מתוך' },
    en: { close: 'Close', prev: 'Previous', next: 'Next', of: 'of' }
  }[lang];

  var shots = [];        // every openable picture on the page
  var at = -1;
  var lastFocus = null;

  var css = document.createElement('style');
  css.textContent = [
    'figure img{cursor:zoom-in}',
    '#lb{position:fixed;inset:0;z-index:9999;display:none;',
    '  background:rgba(8,9,11,.94);backdrop-filter:blur(3px)}',
    '#lb.on{display:grid;grid-template-rows:1fr auto;animation:lbin .22s ease}',
    '@keyframes lbin{from{opacity:0}to{opacity:1}}',
    '#lbstage{display:grid;place-items:center;padding:56px 4vw 8px;min-height:0}',
    '#lbimg{max-width:100%;max-height:100%;object-fit:contain;',
    '  background:#f6f2ea;border-radius:3px;box-shadow:0 18px 60px rgba(0,0,0,.6)}',
    '#lbfoot{padding:10px 6vw 26px;text-align:center;color:#d8d4cc;',
    '  font-family:"Assistant","Helvetica Neue",Arial,sans-serif;font-size:14.5px;',
    '  line-height:1.6;max-width:70ch;margin-inline:auto}',
    '#lbfoot .tag{display:inline-block;margin-inline-end:8px;padding:2px 9px;',
    '  border:1px solid #c9a227;border-radius:999px;color:#c9a227;font-size:11.5px;',
    '  letter-spacing:.09em;text-transform:uppercase;white-space:nowrap}',
    '#lbcount{display:block;margin-top:8px;color:#8b867d;font-size:12.5px;',
    '  font-variant-numeric:tabular-nums}',
    '#lb button{position:fixed;background:rgba(20,20,22,.72);color:#f2efe9;',
    '  border:1px solid rgba(255,255,255,.2);border-radius:10px;cursor:pointer;',
    '  font:inherit;font-size:20px;line-height:1;padding:11px 15px;',
    '  backdrop-filter:blur(6px)}',
    '#lb button:hover{border-color:#c9a227;color:#d9b64a}',
    '#lbclose{top:18px;inset-inline-end:18px}',
    '#lbprev{top:50%;transform:translateY(-50%);inset-inline-start:18px}',
    '#lbnext{top:50%;transform:translateY(-50%);inset-inline-end:18px}',
    '@media(max-width:640px){',
    '  #lbstage{padding:52px 2vw 4px}',
    '  #lbprev,#lbnext{top:auto;bottom:16px;transform:none}',
    '  #lbprev{inset-inline-start:16px}#lbnext{inset-inline-end:16px}}',
    'body.lbopen{overflow:hidden}'
  ].join('');
  document.head.appendChild(css);

  var lb = document.createElement('div');
  lb.id = 'lb';
  lb.setAttribute('role', 'dialog');
  lb.setAttribute('aria-modal', 'true');
  lb.innerHTML =
    '<div id="lbstage"><img id="lbimg" alt=""></div>' +
    '<div id="lbfoot"><span id="lbcap"></span><span id="lbcount"></span></div>' +
    '<button id="lbclose" type="button" title="' + L.close + '" aria-label="' + L.close + '">✕</button>' +
    '<button id="lbprev" type="button" title="' + L.prev + '" aria-label="' + L.prev + '">' + (rtl ? '›' : '‹') + '</button>' +
    '<button id="lbnext" type="button" title="' + L.next + '" aria-label="' + L.next + '">' + (rtl ? '‹' : '›') + '</button>';
  document.body.appendChild(lb);

  var img = lb.querySelector('#lbimg');
  var cap = lb.querySelector('#lbcap');
  var count = lb.querySelector('#lbcount');

  function collect() {
    shots = [];
    var figs = document.querySelectorAll('figure img');
    for (var i = 0; i < figs.length; i++) {
      var f = figs[i];
      if (!f.getAttribute('src')) continue;
      shots.push(f);
    }
  }

  /* Rebuild the caption from the figure, so whatever the page says about a
     picture is what the reader sees when it fills the screen - including the
     "drawing, not a photograph" tag. */
  function captionFor(el) {
    var fig = el.closest ? el.closest('figure') : null;
    var fc = fig ? fig.querySelector('figcaption') : null;
    return fc ? fc.innerHTML : (el.getAttribute('alt') || '');
  }

  function show(i) {
    if (!shots.length) return;
    at = (i % shots.length + shots.length) % shots.length;
    var el = shots[at];
    img.src = el.currentSrc || el.src;
    img.alt = el.getAttribute('alt') || '';
    cap.innerHTML = captionFor(el);
    count.textContent = (at + 1) + ' ' + L.of + ' ' + shots.length;
    var many = shots.length > 1;
    lb.querySelector('#lbprev').style.display = many ? '' : 'none';
    lb.querySelector('#lbnext').style.display = many ? '' : 'none';
  }

  function open(el) {
    collect();
    var i = shots.indexOf(el);
    if (i < 0) return;
    lastFocus = document.activeElement;
    lb.classList.add('on');
    document.body.classList.add('lbopen');
    show(i);
    lb.querySelector('#lbclose').focus();
    if (window.gtag) gtag('event', 'image_open', { src: (el.getAttribute('src') || '').split('/').pop() });
  }

  function close() {
    lb.classList.remove('on');
    document.body.classList.remove('lbopen');
    img.removeAttribute('src');
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  document.addEventListener('click', function (e) {
    if (lb.classList.contains('on')) return;
    var t = e.target;
    if (!t || t.tagName !== 'IMG') return;
    if (t.closest('a')) return;                 // a linked image is a link
    if (!t.closest('figure')) return;
    e.preventDefault();
    open(t);
  });

  lb.addEventListener('click', function (e) {
    var id = e.target.id;
    if (id === 'lbclose' || id === 'lb' || id === 'lbstage') return close();
    if (id === 'lbprev') return show(at - 1);
    if (id === 'lbnext') return show(at + 1);
  });

  document.addEventListener('keydown', function (e) {
    if (!lb.classList.contains('on')) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); }
    else if (e.key === 'ArrowRight') show(rtl ? at - 1 : at + 1);
    else if (e.key === 'ArrowLeft') show(rtl ? at + 1 : at - 1);
    else if (e.key === 'Tab') {                 // keep focus inside the dialog
      e.preventDefault();
      lb.querySelector('#lbclose').focus();
    }
  });
})();
