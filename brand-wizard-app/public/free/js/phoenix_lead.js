/**
 * Phoenix freebie lead capture — single email gate, unlock somatic tools without re-ask.
 * Authority: freebie build plan (interactive first, capture once).
 */
(function (global) {
  'use strict';

  var STORAGE_CAPTURED = 'phoenix_lead_captured';
  var STORAGE_EMAIL = 'phoenix_lead_email';
  var STORAGE_CID = 'phoenix_cid';
  var STORAGE_NAME = 'phoenix_lead_name';

  function getQueryParam(name) {
    try {
      return new URLSearchParams(global.location.search).get(name);
    } catch (e) {
      return null;
    }
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(email || '').trim());
  }

  function shouldShowEmailGate() {
    if (getQueryParam('unlock') === '1' || getQueryParam('cid')) {
      return false;
    }
    try {
      if (global.localStorage.getItem(STORAGE_CAPTURED) === '1') {
        return false;
      }
    } catch (e) { /* ignore */ }
    return true;
  }

  function markCaptured(payload) {
    payload = payload || {};
    try {
      global.localStorage.setItem(STORAGE_CAPTURED, '1');
      if (payload.email) global.localStorage.setItem(STORAGE_EMAIL, payload.email);
      if (payload.cid) global.localStorage.setItem(STORAGE_CID, payload.cid);
      if (payload.first_name) global.localStorage.setItem(STORAGE_NAME, payload.first_name);
    } catch (e) { /* ignore */ }
  }

  function getLeadContext() {
    var ctx = {
      email: getQueryParam('email') || null,
      cid: getQueryParam('cid') || null,
      first_name: getQueryParam('first_name') || null,
    };
    try {
      if (!ctx.email) ctx.email = global.localStorage.getItem(STORAGE_EMAIL);
      if (!ctx.cid) ctx.cid = global.localStorage.getItem(STORAGE_CID);
      if (!ctx.first_name) ctx.first_name = global.localStorage.getItem(STORAGE_NAME);
    } catch (e) { /* ignore */ }
    return ctx;
  }

  function appendUnlockParams(url) {
    if (!url) return url;
    var ctx = getLeadContext();
    var sep = url.indexOf('?') >= 0 ? '&' : '?';
    var parts = ['unlock=1'];
    if (ctx.cid) parts.push('cid=' + encodeURIComponent(ctx.cid));
    if (ctx.email) parts.push('email=' + encodeURIComponent(ctx.email));
    return url + sep + parts.join('&');
  }

  function scoreBand(normalized) {
    if (normalized <= 0.33) return 'low';
    if (normalized <= 0.66) return 'medium';
    return 'high';
  }

  function postToGhl(payload) {
    var webhook =
      global.PHOENIX_GHL_WEBHOOK ||
      (global.document && global.document.body && global.document.body.getAttribute('data-ghl-webhook')) ||
      '';
    if (!webhook) {
      return Promise.resolve({ ok: true, skipped: true });
    }
    return fetch(webhook, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).catch(function () {
      return { ok: false };
    });
  }

  function trackLeadSubmit(funnelSlug, topic) {
    if (typeof global.gtag === 'function') {
      global.gtag('event', 'lead_submit', {
        event_category: 'funnel',
        event_label: funnelSlug || topic || 'freebie',
        topic: topic || '',
        value: 0,
      });
    }
  }

  /**
   * Capture lead at interactive gate (before result reveal).
   */
  function captureLead(opts) {
    opts = opts || {};
    var email = String(opts.email || '').trim();
    var firstName = String(opts.first_name || opts.firstName || '').trim();
    if (!isValidEmail(email)) {
      return Promise.reject(new Error('invalid_email'));
    }
    var payload = {
      email: email,
      first_name: firstName,
      quiz_id: opts.quiz_id || opts.quizId || '',
      topic: opts.topic || '',
      funnel_slug: opts.funnel_slug || opts.funnelSlug || '',
      score: opts.score != null ? opts.score : null,
      score_band: opts.score_band || opts.scoreBand || null,
      answers_json: opts.answers_json || opts.answersJson || null,
      tags: opts.tags || [],
    };
    markCaptured({ email: email, first_name: firstName, cid: opts.cid });
    trackLeadSubmit(payload.funnel_slug, payload.topic);
    return postToGhl(payload).then(function () {
      return payload;
    });
  }

  /**
   * Breathwork LP: skip form when lead already known.
   */
  function initBreathworkLanding(opts) {
    opts = opts || {};
    var toolUrl = opts.toolUrl || opts.tool_url || '#';
    var formView = global.document.getElementById('formView');
    var successView = global.document.getElementById('successView');
    var toolLink = global.document.getElementById('toolLink');

    if (!shouldShowEmailGate()) {
      if (formView) formView.style.display = 'none';
      if (successView) successView.style.display = 'block';
      if (toolLink) toolLink.href = appendUnlockParams(toolUrl);
      return;
    }

    var form = formView && formView.querySelector('form');
    if (form && typeof global.handleSubmit === 'function') {
      return;
    }
  }

  /**
   * Somatic tool page footer + optional book CTA.
   */
  function initToolPage(opts) {
    opts = opts || {};
    var footerId = opts.footerId || 'phoenix-tool-footer';
    var existing = global.document.getElementById(footerId);
    if (!existing) {
      existing = global.document.createElement('div');
      existing.id = footerId;
      existing.className = 'phoenix-tool-footer';
      global.document.body.appendChild(existing);
    }
    var bookUrl = opts.bookUrl || opts.book_url || '';
    var ctaText =
      opts.footerCta ||
      'This reset works for me every time. The full system is in the book — try it and see.';
    existing.innerHTML =
      '<p class="phoenix-tool-footer-text">' +
      ctaText +
      '</p>' +
      (bookUrl
        ? '<a class="phoenix-tool-footer-link" href="' +
          bookUrl +
          '" rel="noopener">Get the book</a>'
        : '');
  }

  function somaticAppUrl(filename) {
    var base = global.PHOENIX_SOMATIC_BASE || '/somatic_exercise_freebee_apps/';
    if (base.charAt(base.length - 1) !== '/') base += '/';
    return appendUnlockParams(base + filename);
  }

  global.PhoenixLead = {
    shouldShowEmailGate: shouldShowEmailGate,
    markCaptured: markCaptured,
    getLeadContext: getLeadContext,
    appendUnlockParams: appendUnlockParams,
    captureLead: captureLead,
    initBreathworkLanding: initBreathworkLanding,
    initToolPage: initToolPage,
    somaticAppUrl: somaticAppUrl,
    scoreBand: scoreBand,
    trackLeadSubmit: trackLeadSubmit,
  };
})(typeof window !== 'undefined' ? window : this);
