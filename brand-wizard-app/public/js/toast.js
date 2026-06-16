/**
 * Vanilla toast notifications — bottom-right stack, max 3, click to dismiss.
 * API: toast.success(msg, duration_ms?), toast.error(...), toast.info(...)
 */
(function (global) {
  'use strict';

  var MAX_TOASTS = 3;
  var DEFAULT_SUCCESS_MS = 4000;
  var DEFAULT_ERROR_MS = 8000;
  var DEFAULT_INFO_MS = 4000;

  var container = null;

  function ensureContainer() {
    if (container && document.body.contains(container)) return container;
    container = document.createElement('div');
    container.id = 'pp-toast-container';
    container.setAttribute('aria-live', 'polite');
    container.setAttribute('aria-relevant', 'additions');
    document.body.appendChild(container);
    injectStyles();
    return container;
  }

  function injectStyles() {
    if (document.getElementById('pp-toast-styles')) return;
    var style = document.createElement('style');
    style.id = 'pp-toast-styles';
    style.textContent =
      '#pp-toast-container{position:fixed;bottom:20px;right:20px;z-index:10000;display:flex;flex-direction:column-reverse;gap:10px;max-width:min(420px,calc(100vw - 40px));pointer-events:none}' +
      '.pp-toast{pointer-events:auto;font-family:"DM Mono",ui-monospace,monospace;font-size:.72rem;line-height:1.45;padding:12px 16px 12px 14px;border-radius:6px;border:1px solid rgba(255,255,255,.12);color:#faf6f0;box-shadow:0 8px 24px rgba(0,0,0,.45);cursor:pointer;animation:pp-toast-in .28s ease-out;transition:opacity .2s,transform .2s}' +
      '.pp-toast.pp-toast-out{opacity:0;transform:translateY(8px)}' +
      '.pp-toast-success{background:rgba(22,101,52,.92);border-color:rgba(74,222,128,.35)}' +
      '.pp-toast-error{background:rgba(127,29,29,.94);border-color:rgba(248,113,113,.4)}' +
      '.pp-toast-info{background:rgba(30,58,138,.92);border-color:rgba(96,165,250,.35)}' +
      '@keyframes pp-toast-in{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}';
    document.head.appendChild(style);
  }

  function trimStack(root) {
    var items = root.querySelectorAll('.pp-toast');
    while (items.length > MAX_TOASTS) dismissToast(items[0]);
  }

  function dismissToast(el) {
    if (!el || el._ppDismissed) return;
    el._ppDismissed = true;
    clearTimeout(el._ppTimer);
    el.classList.add('pp-toast-out');
    setTimeout(function () {
      if (el.parentNode) el.parentNode.removeChild(el);
    }, 220);
  }

  function show(kind, message, durationMs) {
    var root = ensureContainer();
    trimStack(root);

    var el = document.createElement('div');
    el.className = 'pp-toast pp-toast-' + kind;
    el.setAttribute('role', kind === 'error' ? 'alert' : 'status');
    el.textContent = String(message == null ? '' : message);

    el.addEventListener('click', function () {
      dismissToast(el);
    });

    root.appendChild(el);
    trimStack(root);

    var ms =
      durationMs != null
        ? Number(durationMs)
        : kind === 'error'
          ? DEFAULT_ERROR_MS
          : kind === 'info'
            ? DEFAULT_INFO_MS
            : DEFAULT_SUCCESS_MS;
    if (!isFinite(ms) || ms < 0) ms = DEFAULT_SUCCESS_MS;
    if (ms > 0) {
      el._ppTimer = setTimeout(function () {
        dismissToast(el);
      }, ms);
    }
    return el;
  }

  global.toast = {
    success: function (message, duration_ms) {
      return show('success', message, duration_ms);
    },
    error: function (message, duration_ms) {
      return show('error', message, duration_ms);
    },
    info: function (message, duration_ms) {
      return show('info', message, duration_ms);
    },
  };
})(typeof window !== 'undefined' ? window : this);
