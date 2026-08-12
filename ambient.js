/* Optional ambient music for ruhama1946.site.
 *
 * Design decisions, all deliberate:
 *
 * OFF BY DEFAULT, ALWAYS. This site is about a search of a children's house.
 * Music that starts on its own scores somebody's grief without being asked.
 * The reader turns it on or it never plays.
 *
 * IT REMEMBERS. Once you choose, the choice persists across pages and visits,
 * so nobody has to keep switching it off.
 *
 * IT GETS OUT OF THE WAY. When a narration segment plays, the music ducks to a
 * fifth of its volume and comes back afterwards. Two voices competing is worse
 * than either alone.
 *
 * IT DISAPPEARS IF IT ISN'T THERE. The button only renders once the audio file
 * answers a HEAD request, so a missing or unpushed track leaves no dead control
 * on the page - the same fail-safe the narration player uses.
 *
 * Loaded by nav.js on every page.
 */
(function () {
  'use strict';

  var SRC = 'audio/ambient.mp3';
  var KEY = 'ruhama.ambient';
  /* The track is mastered to -20 LUFS on the way in (see scripts note in
     NOTICE.md), well under the -16 LUFS narration, so the browser gain can sit
     higher than it would for a commercial master without ever competing. */
  var FULL = 0.38;
  var DUCKED = FULL * 0.25;
  var lang = new URLSearchParams(location.search).get('lang') === 'en' ? 'en' : 'he';

  var L = {
    he: { on: 'מוזיקה', off: 'מוזיקה', titleOn: 'כיבוי מוזיקת רקע',
          titleOff: 'הפעלת מוזיקת רקע (כבויה כברירת מחדל)' },
    en: { on: 'Music', off: 'Music', titleOn: 'Turn background music off',
          titleOff: 'Turn background music on (off by default)' }
  }[lang];

  var audio = null, playing = false, fadeTimer = null;

  function make() {
    audio = new Audio(SRC);
    audio.loop = true;
    audio.preload = 'none';
    audio.volume = 0;
    return audio;
  }

  function fadeTo(target, ms) {
    if (!audio) return;
    clearInterval(fadeTimer);
    var from = audio.volume, steps = Math.max(1, Math.round(ms / 40)), i = 0;
    fadeTimer = setInterval(function () {
      i++;
      audio.volume = Math.min(1, Math.max(0, from + (target - from) * (i / steps)));
      if (i >= steps) {
        clearInterval(fadeTimer);
        if (target === 0 && audio) audio.pause();
      }
    }, 40);
  }

  function start() {
    if (!audio) make();
    audio.play().then(function () {
      playing = true;
      fadeTo(FULL, 1800);          // ease in; a hard start is jarring
    }).catch(function () { playing = false; });
  }

  function stop() {
    playing = false;
    fadeTo(0, 900);
  }

  function paint(btn) {
    btn.setAttribute('aria-pressed', playing ? 'true' : 'false');
    btn.title = playing ? L.titleOn : L.titleOff;
    btn.querySelector('.dot').style.opacity = playing ? '1' : '.28';
  }

  function build() {
    var nav = document.getElementById('sitenav');
    if (!nav) return;

    var css = document.createElement('style');
    css.textContent =
      '#ambientbtn{display:inline-flex;align-items:center;gap:7px;background:none;' +
      '  border:1px solid rgba(255,255,255,.2);color:#a8a49c;border-radius:8px;' +
      '  padding:6px 11px;font:inherit;font-size:13.5px;cursor:pointer;' +
      '  white-space:nowrap;margin-inline-start:4px;transition:color .15s,border-color .15s}' +
      '#ambientbtn:hover{color:#d9b64a;border-color:#c9a227}' +
      '#ambientbtn[aria-pressed="true"]{color:#c9a227;border-color:#c9a227}' +
      '#ambientbtn .dot{width:7px;height:7px;border-radius:50%;background:currentColor;' +
      '  transition:opacity .3s}';
    document.head.appendChild(css);

    var btn = document.createElement('button');
    btn.id = 'ambientbtn';
    btn.type = 'button';
    btn.innerHTML = '<span class="dot"></span><span>' + L.on + '</span>';
    btn.onclick = function () {
      if (playing) { stop(); store('off'); } else { start(); store('on'); }
      paint(btn);
    };
    nav.appendChild(btn);
    paint(btn);

    /* Restore a previous choice. Browsers block sound before a gesture, so if
       the first play() is refused the button simply stays off - no error, and
       the next click works. */
    if (read() === 'on') { start(); setTimeout(function () { paint(btn); }, 300); }

    /* Duck under any narration on the page. */
    document.addEventListener('play', function (e) {
      if (audio && playing && e.target !== audio && e.target.tagName === 'AUDIO') {
        fadeTo(DUCKED, 600);
      }
    }, true);
    ['pause', 'ended'].forEach(function (ev) {
      document.addEventListener(ev, function (e) {
        if (audio && playing && e.target !== audio && e.target.tagName === 'AUDIO') {
          fadeTo(FULL, 1200);
        }
      }, true);
    });
  }

  function store(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }

  /* Only offer the control if the track actually exists. */
  fetch(SRC, { method: 'HEAD' })
    .then(function (r) { if (r.ok) build(); })
    .catch(function () { /* no track, no button */ });
})();
