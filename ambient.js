/* Ambient music for ruhama1946.site.
 *
 * ON BY DEFAULT, QUIETLY. The bed plays when someone lands. Browsers refuse
 * sound before a user gesture, so if the immediate attempt is blocked we begin
 * on the reader's first click, key or scroll. It fades in rather than starting
 * hard, and the volume is deliberately low: music that starts by itself has to
 * earn its place quietly.
 *
 * PAUSE, NOT STOP. The track loops and resumes where it left off. A pause is
 * remembered across pages and visits.
 *
 * IT GETS OUT OF THE WAY. When a narration segment plays, the music ducks to a
 * quarter of its volume and comes back afterwards.
 *
 * ---------------------------------------------------------------------------
 * ON STATE, which is what this file gets wrong if you are not careful:
 *
 * The first version kept its own `playing` flag and set it inside the promise
 * returned by audio.play(). The click handler then repainted the button
 * immediately - before that promise resolved - so the icon always showed the
 * previous state and looked stuck.
 *
 * There are now two variables and a strict rule about which is authoritative:
 *
 *   want   - what the reader asked for. Set synchronously on click. The button
 *            paints from this, so the icon flips the instant it is pressed.
 *   audio  - what is actually happening. Its own play/pause events call paint()
 *            again, which reconciles the button with reality if the browser
 *            refused, or if playback stopped for any reason we did not cause.
 *
 * Every path that changes either one ends in paint(). No state is ever set
 * inside a promise callback.
 * ---------------------------------------------------------------------------
 *
 * Loaded by nav.js on every page.
 */
(function () {
  'use strict';

  var SRC = 'audio/ambient.mp3';
  var KEY = 'ruhama.ambient';
  var VKEY = 'ruhama.ambient.vol';
  var DEFAULT_VOL = 0.20;     // unchanged: what it plays at if nobody touches it
  var DUCK_RATIO = 0.25;      // how far it drops under a narration voice
  var vol = DEFAULT_VOL;
  var lang = new URLSearchParams(location.search).get('lang') === 'en' ? 'en' : 'he';

  var L = {
    he: { label: 'מוזיקה', titlePlaying: 'השהיית המוזיקה', titlePaused: 'המשך המוזיקה',
          vol: 'עוצמת המוזיקה' },
    en: { label: 'Music', titlePlaying: 'Pause the music', titlePaused: 'Resume the music',
          vol: 'Music volume' }
  }[lang];

  var audio = null;
  var btn = null;
  var want = false;          // the reader's intent - authoritative for the icon
  var fadeTimer = null;
  var ducked = false;

  function make() {
    audio = new Audio(SRC);
    audio.loop = true;
    audio.preload = 'auto';
    audio.volume = 0;
    // Reality reports back here. Both handlers repaint, so the button can never
    // drift from what the audio element is actually doing.
    audio.addEventListener('play', paint);
    audio.addEventListener('playing', paint);
    audio.addEventListener('pause', paint);
    audio.addEventListener('error', function () { want = false; paint(); });
    return audio;
  }

  function fadeTo(target, ms, thenPause) {
    if (!audio) return;
    clearInterval(fadeTimer);
    var from = audio.volume;
    var steps = Math.max(1, Math.round(ms / 40));
    var i = 0;
    fadeTimer = setInterval(function () {
      i++;
      audio.volume = Math.min(1, Math.max(0, from + (target - from) * (i / steps)));
      if (i >= steps) {
        clearInterval(fadeTimer);
        if (thenPause && audio) audio.pause();   // fires 'pause' -> paint()
      }
    }, 40);
  }

  /* The one place that decides how loud it should be right now. */
  function target() { return ducked ? vol * DUCK_RATIO : vol; }

  function play() {
    if (!audio) make();
    want = true;
    paint();                                     // immediate feedback
    var p = audio.play();
    if (p && p.catch) {
      p.catch(function () {
        // blocked, or interrupted. Reality wins.
        want = false;
        paint();
      });
    }
    fadeTo(target(), 1800);
  }

  function pause() {
    want = false;
    paint();                                     // immediate feedback
    fadeTo(0, 700, true);
  }

  function paint() {
    if (!btn) return;
    // The icon follows intent; once the audio settles, its own events repaint
    // and any disagreement resolves in favour of what is really happening.
    var on = want && (!audio || !audio.error);
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    btn.title = on ? L.titlePlaying : L.titlePaused;
    btn.querySelector('.ico').textContent = on ? '❚❚' : '▶';
    btn.querySelector('.txt').textContent = L.label;
  }

  function build() {
    var nav = document.getElementById('sitenav');
    if (!nav) return;

    var css = document.createElement('style');
    css.textContent =
      '#ambientbtn{display:inline-flex;align-items:center;gap:7px;background:none;' +
      '  border:1px solid rgba(255,255,255,.2);color:#a8a49c;border-radius:8px;' +
      '  padding:6px 11px;font:inherit;font-size:13.5px;cursor:pointer;' +
      '  white-space:nowrap;margin-inline-start:4px;' +
      '  transition:color .15s,border-color .15s}' +
      '#ambientbtn:hover{color:#d9b64a;border-color:#c9a227}' +
      '#ambientbtn[aria-pressed="true"]{color:#c9a227;border-color:#c9a227}' +
      '#ambientbtn .ico{font-size:10px;line-height:1;letter-spacing:1px;' +
      '  display:inline-block;min-width:12px;text-align:center}' +
      '#ambientvol{-webkit-appearance:none;appearance:none;width:72px;height:18px;' +
      '  background:none;cursor:pointer;margin-inline-start:6px;vertical-align:middle}' +
      '#ambientvol::-webkit-slider-runnable-track{height:3px;border-radius:2px;' +
      '  background:rgba(255,255,255,.25)}' +
      '#ambientvol::-moz-range-track{height:3px;border-radius:2px;' +
      '  background:rgba(255,255,255,.25)}' +
      '#ambientvol::-webkit-slider-thumb{-webkit-appearance:none;width:11px;height:11px;' +
      '  border-radius:50%;background:#c9a227;margin-top:-4px}' +
      '#ambientvol::-moz-range-thumb{width:11px;height:11px;border:0;' +
      '  border-radius:50%;background:#c9a227}' +
      '#ambientvol:hover::-webkit-slider-thumb{background:#d9b64a}';
    document.head.appendChild(css);

    btn = document.createElement('button');
    btn.id = 'ambientbtn';
    btn.type = 'button';
    btn.innerHTML = '<span class="ico"></span><span class="txt"></span>';
    btn.addEventListener('click', function () {
      if (want) { pause(); store('off'); } else { play(); store('on'); }
      if (window.gtag) gtag('event', 'music_toggle', { state: want ? 'on' : 'off' });
    });
    nav.appendChild(btn);

    /* Volume. Default is untouched at 20%; this only lets someone move it. */
    var slider = document.createElement('input');
    slider.id = 'ambientvol';
    slider.type = 'range';
    slider.min = '0'; slider.max = '100'; slider.step = '1';
    slider.value = String(Math.round(vol * 100));
    slider.title = L.vol;
    slider.setAttribute('aria-label', L.vol);
    slider.addEventListener('input', function () {
      vol = Math.max(0, Math.min(1, Number(slider.value) / 100));
      storeVol(vol);
      // move immediately rather than fading - a slider that lags feels broken
      if (audio && want) { clearInterval(fadeTimer); audio.volume = target(); }
    });
    nav.appendChild(slider);

    paint();

    if (read() !== 'off') {
      play();
      // If the browser refused, wait for the reader's first gesture.
      setTimeout(function () {
        if (audio && audio.paused && read() !== 'off') arm();
      }, 500);
    }

    duck();
  }

  function arm() {
    var events = ['pointerdown', 'keydown', 'wheel', 'touchstart'];
    function unarm() {
      events.forEach(function (ev) { document.removeEventListener(ev, kick); });
    }
    function kick() {
      unarm();
      if (read() !== 'off') play();
    }
    events.forEach(function (ev) {
      document.addEventListener(ev, kick, { passive: true });
    });
  }

  /* Duck under narration. Volume only - never touches play state, so it can
     never fight the button. */
  function duck() {
    document.addEventListener('play', function (e) {
      if (audio && e.target !== audio && e.target.tagName === 'AUDIO') {
        ducked = true;
        if (want) fadeTo(target(), 600);
      }
    }, true);
    ['pause', 'ended'].forEach(function (ev) {
      document.addEventListener(ev, function (e) {
        if (audio && e.target !== audio && e.target.tagName === 'AUDIO') {
          ducked = false;
          if (want) fadeTo(target(), 1200);
        }
      }, true);
    });
  }

  function store(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function storeVol(v) { try { localStorage.setItem(VKEY, String(v)); } catch (e) {} }
  function readVol() {
    try {
      var v = parseFloat(localStorage.getItem(VKEY));
      return isFinite(v) && v >= 0 && v <= 1 ? v : DEFAULT_VOL;
    } catch (e) { return DEFAULT_VOL; }
  }

  /* Only offer the control if the track actually exists. */
  vol = readVol();
  fetch(SRC, { method: 'HEAD' })
    .then(function (r) { if (r.ok) build(); })
    .catch(function () { /* no track, no button */ });
})();
