/**
 * Phoenix funnel landing helpers — Waystream tool-first + report unlock flow.
 */
(function (global) {
  'use strict';

  var REPORT_OFFER_ID = 'phoenix-report-offer';
  var COMPLETION_CTA_ID = 'phoenix-completion-cta';
  var START_KEY_PREFIX = 'phoenix_tool_started_at:';
  var DEFAULT_CHANNEL_ORDER = ['whatsapp', 'telegram', 'email'];
  var JAPAN_CHANNEL_ORDER = ['line', 'messenger', 'whatsapp', 'telegram', 'email'];
  var CHANNEL_LABELS = {
    whatsapp: 'WhatsApp',
    telegram: 'Telegram',
    email: 'Email',
    line: 'LINE',
    messenger: 'Messenger',
  };
  var CHANNEL_PLACEHOLDERS = {
    whatsapp: '+1 555 010 0199',
    telegram: '@yourhandle',
    email: 'you@example.com',
    line: 'Your LINE ID',
    messenger: 'Your Messenger username',
  };
  var CHANNEL_CONSENT = {
    whatsapp: 'I consent to receive my Waystream report and related follow-up by WhatsApp.',
    telegram: 'I consent to receive my Waystream report and related follow-up by Telegram.',
    email: 'I consent to receive my Waystream report and related follow-up by email.',
    line: 'I consent to receive my Waystream report and related follow-up by LINE.',
    messenger: 'I consent to receive my Waystream report and related follow-up by Messenger.',
  };
  var REPORT_META = {
    'anxiety-nervous-system-reset': {
      title: 'Your Nervous System Reset Report',
      promise: 'See what your breath pattern may reveal about your stress response, your next-week regulation cue, and the one practice to repeat when anxiety starts to lead.',
      completion: 'You completed the reset.',
      topic: 'anxiety',
    },
    'boundaries-script-kit': {
      title: 'Your Boundary Language Report',
      promise: 'Turn the script you chose into a practical language map: what you tend to protect, where you soften too quickly, and a next conversation starter.',
      completion: 'You completed the script kit.',
      topic: 'boundaries',
    },
    'burnout-energy-audit': {
      title: 'Your Energy Pattern Report',
      promise: 'Get a personalized read on where your energy leaks, what your nervous system may be asking for, and the simplest recovery move for the next week.',
      completion: 'You completed the audit.',
      topic: 'burnout',
    },
    'compassion-fatigue-audit': {
      title: 'Your Capacity Report',
      promise: 'Understand your capacity score, the care pattern underneath it, and the boundary or recovery practice most likely to be useful next.',
      completion: 'You completed the audit.',
      topic: 'compassion_fatigue',
    },
    'courage-decision-map': {
      title: 'Your Decision Courage Report',
      promise: 'Receive a clear reflection on your fear pattern, your smallest honest next move, and the future-facing question to carry for seven days.',
      completion: 'You completed the map.',
      topic: 'courage',
    },
    'depression-momentum-kit': {
      title: 'Your Momentum Report',
      promise: 'Translate your selected micro-actions into a gentle next-step map with somatic, psychological, and spiritual reflection cues.',
      completion: 'You completed the kit.',
      topic: 'depression',
    },
    'financial-anxiety-check-in': {
      title: 'Your Money Anxiety Report',
      promise: 'See the difference between the money signal and the story around it, plus a grounding practice and one action for the next week.',
      completion: 'You completed the check-in.',
      topic: 'financial_anxiety',
    },
    'financial-stress-audit': {
      title: 'Your Financial Stress Report',
      promise: 'Receive a reflective map of your money stress origin, worst-case story, and one practical stabilizing action without shame or pressure.',
      completion: 'You completed the audit.',
      topic: 'financial_stress',
    },
    'grief-letter-template': {
      title: 'Your Grief Integration Report',
      promise: 'Hold what you wrote with care: a report on the emotional thread, the unfinished sentence, and a gentle practice for the next week.',
      completion: 'You completed the letter.',
      topic: 'grief',
    },
    'imposter-evidence-log': {
      title: 'Your Evidence Report',
      promise: 'Turn your evidence log into a steadier self-trust map with the pattern your doubt uses and the proof your body can remember.',
      completion: 'You completed the log.',
      topic: 'imposter_syndrome',
    },
    'overthinking-thought-sorter': {
      title: 'Your Thought Pattern Report',
      promise: 'Receive the meaning of your sorted thought pattern, what it may be trying to protect, and one practice for interrupting the loop.',
      completion: 'You completed the sorter.',
      topic: 'overthinking',
    },
    'self-worth-inventory': {
      title: 'Your Worth Inventory Report',
      promise: 'See the worth signals inside your answers, the old measurement system you may be outgrowing, and a next-week self-worth practice.',
      completion: 'You completed the inventory.',
      topic: 'self_worth',
    },
    'sleep-anxiety-wind-down': {
      title: 'Your Wind-Down Report',
      promise: 'Understand which bedtime loop is loudest, what may help your body downshift, and the evening cue to test for the next seven nights.',
      completion: 'You completed the wind-down.',
      topic: 'sleep_anxiety',
    },
    'social-anxiety-toolkit': {
      title: 'Your Social Energy Report',
      promise: 'Get a reflection on your before/during/after pattern, your energy protection cue, and one phrase to use before the next event.',
      completion: 'You completed the toolkit.',
      topic: 'social_anxiety',
    },
    'somatic-body-scan': {
      title: 'Your Body Scan Report',
      promise: 'Receive a body-based reflection on what stood out, what may need care, and the next grounding practice to keep close.',
      completion: 'You completed the scan.',
      topic: 'somatic_healing',
    },
  };

  function getQueryParam(name) {
    try {
      return new URLSearchParams(global.location.search).get(name);
    } catch (e) {
      return null;
    }
  }

  function bodyData(name) {
    if (!global.document || !global.document.body) return '';
    return global.document.body.getAttribute('data-' + name) || '';
  }

  function currentPageSlug() {
    var fromBody = bodyData('funnel-slug');
    if (fromBody) return fromBody;
    try {
      var parts = global.location.pathname.split('/').filter(Boolean);
      return parts[parts.length - 1] === 'index.html' ? parts[parts.length - 2] || '' : parts[parts.length - 1] || '';
    } catch (e) {
      return '';
    }
  }

  function isWaystreamPage() {
    return bodyData('brand-id') === 'way_stream_sanctuary' && !!REPORT_META[currentPageSlug()];
  }

  function initSkipFormIfCaptured(formSectionId, toolSectionId, onUnlock) {
    if (!global.PhoenixLead || global.PhoenixLead.shouldShowEmailGate()) {
      return;
    }
    var formEl = global.document.getElementById(formSectionId || 'form-section');
    var toolEl = global.document.getElementById(toolSectionId || 'tool-section');
    if (formEl) formEl.style.display = 'none';
    if (toolEl) {
      toolEl.style.display = 'block';
      toolEl.classList.add('visible');
    }
    if (typeof onUnlock === 'function') onUnlock();
  }

  function showEmailGate(gateId) {
    if (isWaystreamPage()) return;
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
      if (isWaystreamPage()) {
        hideEmailGate(gateId);
        onSuccess();
        markToolComplete({ source: 'legacy-email-gate-bypass' });
        return;
      }
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

  function readEmbeddedCampaignPlan() {
    var el = global.document.getElementById('phoenix-evergreen-campaign-plan');
    if (!el || !el.textContent.trim()) return {};
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      return {};
    }
  }

  function assignAbVariant(slug) {
    var override = getQueryParam('ab_variant');
    if (override && /^[A-Za-z0-9_-]{1,40}$/.test(override)) return override;
    var key = 'phoenix_freebie_ab_variant:' + slug;
    try {
      var existing = global.localStorage.getItem(key);
      if (existing) return existing;
    } catch (e) { /* ignore */ }
    var seed = getQueryParam('cid') || slug || 'freebie';
    var hash = 0;
    for (var i = 0; i < seed.length; i += 1) hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
    var variant = hash % 10 < 6 ? 'whatsapp_first_a' : hash % 10 < 8 ? 'whatsapp_first_b' : 'email_fallback_a';
    try {
      global.localStorage.setItem(key, variant);
    } catch (e) { /* ignore */ }
    return variant;
  }

  function trackFreebieEvent(name, detail) {
    detail = detail || {};
    var payload = {
      freebie_slug: currentPageSlug(),
      topic: bodyData('topic') || (REPORT_META[currentPageSlug()] || {}).topic || '',
      ab_variant: assignAbVariant(currentPageSlug()),
    };
    ['channel', 'score_band', 'source'].forEach(function (key) {
      if (detail[key]) payload[key] = detail[key];
    });
    if (typeof global.gtag === 'function') {
      global.gtag('event', name, payload);
    }
  }

  function setStartedAt(slug) {
    try {
      if (!global.localStorage.getItem(START_KEY_PREFIX + slug)) {
        global.localStorage.setItem(START_KEY_PREFIX + slug, String(Date.now()));
      }
    } catch (e) { /* ignore */ }
  }

  function completionDurationSeconds(slug) {
    try {
      var started = parseInt(global.localStorage.getItem(START_KEY_PREFIX + slug), 10);
      if (started) return Math.max(1, Math.round((Date.now() - started) / 1000));
    } catch (e) { /* ignore */ }
    return null;
  }

  function collectAnswers() {
    var answers = [];
    var root = global.document.getElementById('tool-section') || global.document.body;
    if (!root) return answers;
    root.querySelectorAll('textarea, input[type="text"], input[type="radio"]:checked, input[type="checkbox"]:checked').forEach(function (el, index) {
      var value = String(el.value || '').trim();
      if (!value && el.type !== 'checkbox') return;
      var label = '';
      var block = el.closest('.prompt-block, .question-block, .part-section, .zone, .phase-card, label, .checklist-item');
      if (block) label = String(block.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 180);
      answers.push({
        index: index,
        field: el.name || el.id || el.type || 'answer',
        label: label,
        value: el.type === 'checkbox' ? 'checked' : value.slice(0, 1200),
      });
    });
    return answers;
  }

  function getChannelOrder(plan) {
    var locale = String((plan && plan.locale) || bodyData('locale') || '').toLowerCase();
    var region = String(bodyData('region') || getQueryParam('region') || '').toLowerCase();
    if (locale.indexOf('ja') === 0 || region === 'jp' || region === 'japan') return JAPAN_CHANNEL_ORDER.slice();
    return DEFAULT_CHANNEL_ORDER.slice();
  }

  function channelButton(channel, idx) {
    var checked = idx === 0 ? ' checked' : '';
    return (
      '<label class="phoenix-report-channel">' +
      '<input type="radio" name="phoenix-report-channel" value="' + channel + '"' + checked + '>' +
      '<span>' + CHANNEL_LABELS[channel] + '</span>' +
      '</label>'
    );
  }

  function ensureCompletionCta() {
    if (global.document.getElementById(COMPLETION_CTA_ID)) return;
    var tool = global.document.getElementById('tool-section');
    if (!tool) return;
    var cta = global.document.createElement('div');
    cta.id = COMPLETION_CTA_ID;
    cta.className = 'phoenix-completion-cta';
    cta.innerHTML =
      '<p>Finished the tool?</p>' +
      '<button type="button" class="phoenix-report-submit">See my personalized report options</button>';
    cta.querySelector('button').addEventListener('click', function () {
      markToolComplete({ source: 'completion-cta' });
    });
    tool.appendChild(cta);
  }

  function ensureReportOffer() {
    var existing = global.document.getElementById(REPORT_OFFER_ID);
    if (existing) return existing;
    var slug = currentPageSlug();
    var meta = REPORT_META[slug] || {};
    var plan = readEmbeddedCampaignPlan();
    var channels = getChannelOrder(plan);
    var offer = global.document.createElement('section');
    offer.id = REPORT_OFFER_ID;
    offer.className = 'phoenix-report-offer';
    offer.setAttribute('aria-live', 'polite');
    offer.style.display = 'none';
    offer.innerHTML =
      '<div class="phoenix-report-kicker">You did it</div>' +
      '<h2>' + (meta.title || 'Your Waystream Report') + '</h2>' +
      '<p class="phoenix-report-promise">' + (meta.promise || 'Unlock a personalized report based on the tool you just completed.') + '</p>' +
      '<ul class="phoenix-report-benefits">' +
      '<li>Somatic signal: what your body may be asking for next.</li>' +
      '<li>Nervous-system cue: one repeatable practice for the next week.</li>' +
      '<li>Psychological reflection: the pattern your answers point toward.</li>' +
      '<li>Spiritual question: a gentle inquiry to keep close without forcing certainty.</li>' +
      '</ul>' +
      '<form id="phoenix-report-form" class="phoenix-report-form">' +
      '<div class="phoenix-report-channels">' + channels.map(channelButton).join('') + '</div>' +
      '<label class="phoenix-report-field">Where should we send it?<input id="phoenix-report-address" autocomplete="off" required></label>' +
      '<label class="phoenix-report-field">First name <span>(optional)</span><input id="phoenix-report-name" autocomplete="given-name"></label>' +
      '<label class="phoenix-report-consent"><input id="phoenix-report-consent" type="checkbox" required> <span id="phoenix-report-consent-copy"></span></label>' +
      '<p class="phoenix-report-privacy">Your tool answers and delivery handle are used to prepare and send this report. No diagnosis, no medical promise, and you can opt out in the channel you choose.</p>' +
      '<p id="phoenix-report-error" class="phoenix-report-error" hidden></p>' +
      '<button type="submit" class="phoenix-report-submit">Send my report</button>' +
      '<p id="phoenix-report-success" class="phoenix-report-success" hidden>Done. Your report request was captured.</p>' +
      '</form>';
    var tool = global.document.getElementById('tool-section');
    if (tool && tool.parentNode) {
      tool.parentNode.insertBefore(offer, tool.nextSibling);
    } else {
      global.document.body.appendChild(offer);
    }
    bindReportOfferForm(offer);
    return offer;
  }

  function selectedChannel(offer) {
    var checked = offer.querySelector('input[name="phoenix-report-channel"]:checked');
    return checked ? checked.value : 'email';
  }

  function updateAddressField(offer) {
    var channel = selectedChannel(offer);
    var address = offer.querySelector('#phoenix-report-address');
    var consent = offer.querySelector('#phoenix-report-consent-copy');
    if (address) {
      address.type = channel === 'email' ? 'email' : channel === 'whatsapp' ? 'tel' : 'text';
      address.placeholder = CHANNEL_PLACEHOLDERS[channel] || '';
      address.setAttribute('aria-label', CHANNEL_LABELS[channel] + ' delivery address');
    }
    if (consent) consent.textContent = CHANNEL_CONSENT[channel] || CHANNEL_CONSENT.email;
  }

  function bindReportOfferForm(offer) {
    updateAddressField(offer);
    offer.querySelectorAll('input[name="phoenix-report-channel"]').forEach(function (input) {
      input.addEventListener('change', function () {
        updateAddressField(offer);
        trackFreebieEvent('channel_selected', { channel: selectedChannel(offer) });
      });
    });
    var form = offer.querySelector('#phoenix-report-form');
    form.addEventListener('submit', function (evt) {
      evt.preventDefault();
      var channel = selectedChannel(offer);
      var address = String(offer.querySelector('#phoenix-report-address').value || '').trim();
      var name = String(offer.querySelector('#phoenix-report-name').value || '').trim();
      var consent = offer.querySelector('#phoenix-report-consent').checked;
      var error = offer.querySelector('#phoenix-report-error');
      var success = offer.querySelector('#phoenix-report-success');
      error.hidden = true;
      success.hidden = true;
      if (!global.PhoenixLead || !global.PhoenixLead.validateDeliveryAddress(channel, address)) {
        error.textContent = 'Please enter a valid ' + CHANNEL_LABELS[channel] + ' destination.';
        error.hidden = false;
        return;
      }
      if (!consent) {
        error.textContent = 'Please confirm consent for this delivery channel.';
        error.hidden = false;
        return;
      }
      var slug = currentPageSlug();
      var plan = readEmbeddedCampaignPlan();
      var meta = REPORT_META[slug] || {};
      var answers = collectAnswers();
      var payload = {
        first_name: name,
        email: channel === 'email' ? address : '',
        phone: channel === 'whatsapp' ? address : '',
        delivery_channel: channel,
        delivery_address: address,
        channel_consent: true,
        topic: bodyData('topic') || meta.topic || plan.topic || '',
        funnel_slug: slug,
        source_page_slug: slug,
        freebie_id: plan.freebie_id || slug,
        quiz_id: plan.quiz_id || '',
        answers_json: JSON.stringify(answers),
        result_summary: meta.completion || 'Tool completed.',
        report_id: 'waystream_' + slug + '_report_v1',
        report_variant: assignAbVariant(slug),
        report_summary: meta.promise || '',
        completed_at: new Date().toISOString(),
        completion_duration_seconds: completionDurationSeconds(slug),
        ab_variant: assignAbVariant(slug),
        tags: ['source_freebie_quiz', 'freebie_report_requested', 'delivery_' + channel],
        require_campaign_plan: true,
      };
      trackFreebieEvent('report_capture_submit', { channel: channel });
      global.PhoenixLead.captureReportUnlock(payload)
        .then(function () {
          success.hidden = false;
          form.classList.add('is-submitted');
          trackFreebieEvent('report_delivery_success', { channel: channel });
        })
        .catch(function (err) {
          error.textContent = err && err.message ? err.message.replace(/_/g, ' ') : 'Report request failed.';
          error.hidden = false;
          trackFreebieEvent('report_delivery_fail', { channel: channel });
        });
    });
  }

  function showReportOffer(source) {
    if (!isWaystreamPage()) return;
    var offer = ensureReportOffer();
    offer.style.display = 'block';
    offer.classList.add('visible');
    var cta = global.document.getElementById(COMPLETION_CTA_ID);
    if (cta) cta.style.display = 'none';
    trackFreebieEvent('report_offer_view', { source: source || 'tool_complete' });
    if (offer.scrollIntoView) offer.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function markToolComplete(detail) {
    detail = detail || {};
    if (!isWaystreamPage()) return;
    trackFreebieEvent('tool_complete', detail);
    showReportOffer(detail.source);
  }

  function wrapCompletionFunctions() {
    [
      'finishSession',
      'revealResults',
      'showResult',
      'revealPendingResult',
      'completeMap',
      'completeLetter',
      'showCompletion',
      'copyScript',
    ].forEach(function (name) {
      var original = global[name];
      if (typeof original !== 'function' || original.__phoenixWrapped) return;
      var wrapped = function () {
        var result = original.apply(this, arguments);
        setTimeout(function () {
          markToolComplete({ source: name });
        }, 0);
        return result;
      };
      wrapped.__phoenixWrapped = true;
      global[name] = wrapped;
    });
  }

  function watchCompletionSurfaces() {
    var surfaces = ['results-block', 'result-card', 'letter-complete'];
    if (!global.MutationObserver) return;
    surfaces.forEach(function (id) {
      var el = global.document.getElementById(id);
      if (!el) return;
      var observer = new MutationObserver(function () {
        var visible = el.classList.contains('visible') || el.style.display === 'block';
        if (visible) markToolComplete({ source: id });
      });
      observer.observe(el, { attributes: true, attributeFilter: ['class', 'style'] });
    });
  }

  function initPostExperienceCapture() {
    if (!isWaystreamPage()) return;
    var slug = currentPageSlug();
    setStartedAt(slug);
    trackFreebieEvent('tool_view');
    ['form-section', 'capture-section', 'email-gate-section'].forEach(function (id) {
      var el = global.document.getElementById(id);
      if (el) el.style.display = 'none';
    });
    var tool = global.document.getElementById('tool-section');
    if (tool) {
      tool.style.display = 'block';
      tool.classList.add('visible');
    }
    ensureReportOffer();
    ensureCompletionCta();
    wrapCompletionFunctions();
    watchCompletionSurfaces();
    global.document.addEventListener('change', function (evt) {
      var target = evt.target;
      if (target && target.closest && target.closest('#tool-section')) {
        trackFreebieEvent('tool_step_complete', { source: target.name || target.id || target.type });
      }
    });
  }

  function autoInit() {
    if (!global.document) return;
    if (global.document.readyState === 'loading') {
      global.document.addEventListener('DOMContentLoaded', initPostExperienceCapture);
    } else {
      setTimeout(initPostExperienceCapture, 0);
    }
  }

  global.PhoenixFunnel = {
    initSkipFormIfCaptured: initSkipFormIfCaptured,
    initPostExperienceCapture: initPostExperienceCapture,
    showEmailGate: showEmailGate,
    hideEmailGate: hideEmailGate,
    bindEmailBeforeResult: bindEmailBeforeResult,
    injectSomaticResultLink: injectSomaticResultLink,
    markToolComplete: markToolComplete,
    collectAnswers: collectAnswers,
    assignAbVariant: assignAbVariant,
    trackFreebieEvent: trackFreebieEvent,
  };

  autoInit();
})(typeof window !== 'undefined' ? window : this);
