/**
 * Phoenix funnel landing helpers — skip duplicate email gates, flagship hooks.
 */
(function (global) {
  'use strict';

  function initSkipFormIfCaptured(formSectionId, toolSectionId, onUnlock) {
    if (!global.PhoenixLead || global.PhoenixLead.shouldShowEmailGate()) {
      return;
    }
    var formEl = global.document.getElementById(formSectionId || 'form-section');
    var toolEl = global.document.getElementById(toolSectionId || 'tool-section');
    if (formEl) formEl.style.display = 'none';
    if (toolEl) toolEl.style.display = 'block';
    if (typeof onUnlock === 'function') onUnlock();
  }

  function showEmailGate(gateId) {
    var gate = global.document.getElementById(gateId || 'email-gate-section');
    if (gate) gate.style.display = 'block';
  }

  function hideEmailGate(gateId) {
    var gate = global.document.getElementById(gateId || 'email-gate-section');
    if (gate) gate.style.display = 'none';
  }

  function bindEmailBeforeResult(opts) {
    opts = opts || {};
    var gateId = opts.gateId || 'email-gate-section';
    var onSuccess = opts.onSuccess || function () {};

    global.submitEmailGate = function () {
      var nameEl = global.document.getElementById(opts.nameId || 'gate-name');
      var emailEl = global.document.getElementById(opts.emailId || 'gate-email');
      var errEl = global.document.getElementById(opts.errorId || 'gate-error');
      var name = nameEl ? nameEl.value.trim() : '';
      var email = emailEl ? emailEl.value.trim() : '';
      if (!email || !global.PhoenixLead) {
        if (errEl) errEl.style.display = 'block';
        return;
      }
      global.PhoenixLead.captureLead({
        email: email,
        first_name: name,
        topic: opts.topic || '',
        funnel_slug: opts.funnelSlug || opts.funnel_slug || '',
        quiz_id: opts.quizId || opts.quiz_id || '',
        score: opts.pendingScore != null ? opts.pendingScore : null,
        score_band: opts.pendingScoreBand || null,
      })
        .then(function () {
          hideEmailGate(gateId);
          onSuccess();
        })
        .catch(function () {
          if (errEl) errEl.style.display = 'block';
        });
    };
  }

  function injectSomaticResultLink(containerId, appFile, label) {
    var el = global.document.getElementById(containerId);
    if (!el || !global.PhoenixLead) return;
    var url = global.PhoenixLead.somaticAppUrl(appFile);
    el.innerHTML =
      '<a class="btn" href="' +
      url +
      '" rel="noopener" style="display:inline-block;margin-top:16px;text-decoration:none;">' +
      (label || 'Try the 2-minute practice I use') +
      '</a>';
  }

  global.PhoenixFunnel = {
    initSkipFormIfCaptured: initSkipFormIfCaptured,
    showEmailGate: showEmailGate,
    hideEmailGate: hideEmailGate,
    bindEmailBeforeResult: bindEmailBeforeResult,
    injectSomaticResultLink: injectSomaticResultLink,
  };
})(typeof window !== 'undefined' ? window : this);
