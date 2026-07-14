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
  var CAMPAIGN_SCRIPT_ID = 'phoenix-evergreen-campaign-plan';
  var CAMPAIGN_REQUIRED_FIELDS = [
    'brand_id',
    'freebie_id',
    'quiz_id',
    'topic',
    'funnel_variant',
    'source_page_slug',
    'campaign_plan_id',
  ];
  var CAMPAIGN_SLOT_FIELDS = [
    'title',
    'url',
    'cta',
    'tool_name',
    'short_description',
    'benefit',
    'microcopy',
  ];
  var CAMPAIGN_SPECIAL_FIELDS = [
    'e3_story_body',
    'e4_book_title',
    'e5_book1_title',
    'e5_book1_url',
    'e5_book1_note',
    'e5_book2_title',
    'e5_book2_url',
    'e5_book2_note',
    'e5_book3_title',
    'e5_book3_url',
    'e5_book3_note',
    'e6_book_title',
    'e7_bundle_title',
    'e8_last_chance_note',
  ];
  var CAMPAIGN_BONUS_FIELDS = [
    'bonus_pre_e3_title',
    'bonus_pre_e3_url',
    'bonus_pre_e3_cta',
    'bonus_pre_e3_tool_name',
    'bonus_pre_e3_short_description',
    'bonus_pre_e3_benefit',
    'bonus_pre_e3_microcopy',
    'bonus_pre_e3_html_template',
    'bonus_pre_e3_send_if_welcome_depth_missing',
  ];
  var REPORT_PAYLOAD_FIELDS = [
    'delivery_channel',
    'delivery_address',
    'channel_consent',
    'report_id',
    'report_variant',
    'report_summary',
    'completed_at',
    'completion_duration_seconds',
    'ab_variant',
    'source_page_slug',
    'freebie_id',
    'result_summary',
  ];
  for (var campaignIndex = 1; campaignIndex <= 9; campaignIndex += 1) {
    CAMPAIGN_SLOT_FIELDS.forEach(function (field) {
      CAMPAIGN_REQUIRED_FIELDS.push('e' + campaignIndex + '_' + field);
    });
  }
  CAMPAIGN_SPECIAL_FIELDS.forEach(function (field) {
    CAMPAIGN_REQUIRED_FIELDS.push(field);
  });
  CAMPAIGN_BONUS_FIELDS.forEach(function (field) {
    CAMPAIGN_REQUIRED_FIELDS.push(field);
  });

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

  function normalizeDeliveryChannel(channel) {
    channel = String(channel || '').trim().toLowerCase();
    if (channel === 'whatsapp' || channel === 'telegram' || channel === 'email' || channel === 'line' || channel === 'messenger') {
      return channel;
    }
    return '';
  }

  function validateDeliveryAddress(channel, value) {
    channel = normalizeDeliveryChannel(channel);
    value = String(value || '').trim();
    if (!channel || !value) return false;
    if (channel === 'email') return isValidEmail(value);
    if (channel === 'whatsapp') return /^\+?[0-9().\-\s]{7,24}$/.test(value);
    if (channel === 'telegram') return /^@?[A-Za-z0-9_]{5,32}$/.test(value);
    if (channel === 'line') return /^[A-Za-z0-9_.\-]{3,40}$/.test(value);
    if (channel === 'messenger') return /^@?[A-Za-z0-9_.\-]{3,80}$/.test(value);
    return false;
  }

  function isWaystreamPostExperienceCapture() {
    var brandId = bodyData('brand-id');
    var enabled = bodyData('post-experience-capture');
    if (enabled === '1' || enabled === 'true') return true;
    return brandId === 'way_stream_sanctuary' && currentPageSlug();
  }

  function shouldShowEmailGate() {
    if (getQueryParam('unlock') === '1' || getQueryParam('cid')) {
      return false;
    }
    if (isWaystreamPostExperienceCapture()) {
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

  function readOptionalPhone(opts) {
    var phone = opts.phone || opts.phone_number || opts.phoneNumber || '';
    if (!phone && global.document) {
      var phoneEl = global.document.querySelector(
        'input[type="tel"], input[name="phone"], input[name="phone_number"], #phone, #gate-phone'
      );
      phone = phoneEl ? phoneEl.value : '';
    }
    return String(phone || '').trim();
  }

  function showSafeCampaignError(reason) {
    if (global.console && typeof global.console.error === 'function') {
      global.console.error('[PhoenixLead] Evergreen campaign plan blocked submit: ' + reason);
    }
    if (!global.document) return;
    var message = 'We could not prepare this email sequence. Please refresh and try again.';
    ['gate-error', 'form-error', 'capture-error'].forEach(function (id) {
      var el = global.document.getElementById(id);
      if (el) {
        el.textContent = message;
        el.style.display = 'block';
      }
    });
  }

  function blockCampaignSubmit(reason) {
    showSafeCampaignError(reason);
    var err = new Error('evergreen_campaign_plan_' + reason);
    err.code = 'evergreen_campaign_plan_' + reason;
    throw err;
  }

  function readEmbeddedCampaignPlan() {
    if (!global.document) return null;
    var el = global.document.getElementById(CAMPAIGN_SCRIPT_ID);
    if (!el || !el.textContent.trim()) return null;
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      blockCampaignSubmit('invalid_json');
    }
    return null;
  }

  function isHttpUrl(value) {
    try {
      var parsed = new URL(String(value || ''));
      return parsed.protocol === 'http:' || parsed.protocol === 'https:';
    } catch (e) {
      return false;
    }
  }

  function resolveCampaignPayload(opts) {
    var brandId = opts.brand_id || opts.brandId || bodyData('brand-id') || '';
    var sourcePageSlug =
      opts.source_page_slug ||
      opts.sourcePageSlug ||
      opts.funnel_slug ||
      opts.funnelSlug ||
      currentPageSlug();
    var requirePlan =
      brandId === 'way_stream_sanctuary' ||
      opts.require_campaign_plan === true ||
      opts.requireCampaignPlan === true;
    var plan = readEmbeddedCampaignPlan();
    if (!plan) {
      if (requirePlan) blockCampaignSubmit('missing');
      return {};
    }
    CAMPAIGN_REQUIRED_FIELDS.forEach(function (field) {
      if (plan[field] === null || plan[field] === undefined || String(plan[field]).trim() === '') {
        blockCampaignSubmit('incomplete_' + field);
      }
    });
    for (var i = 1; i <= 9; i += 1) {
      if (!isHttpUrl(plan['e' + i + '_url'])) {
        blockCampaignSubmit('invalid_url_e' + i);
      }
    }
    if (!isHttpUrl(plan.bonus_pre_e3_url)) {
      blockCampaignSubmit('invalid_url_bonus_pre_e3');
    }
    if (brandId && plan.brand_id !== brandId) {
      blockCampaignSubmit('brand_mismatch');
    }
    if (sourcePageSlug && plan.source_page_slug !== sourcePageSlug) {
      blockCampaignSubmit('page_mismatch');
    }
    var campaign = {
      brand_id: plan.brand_id,
      freebie_id: plan.freebie_id,
      quiz_id: plan.quiz_id,
      topic: plan.topic,
      funnel_variant: plan.funnel_variant,
      source_page_slug: plan.source_page_slug,
      campaign_plan_id: plan.campaign_plan_id,
    };
    for (var slot = 1; slot <= 9; slot += 1) {
      CAMPAIGN_SLOT_FIELDS.forEach(function (field) {
        campaign['phoenix_e' + slot + '_' + field] = plan['e' + slot + '_' + field];
      });
    }
    CAMPAIGN_SPECIAL_FIELDS.forEach(function (field) {
      campaign['phoenix_' + field] = plan[field];
    });
    CAMPAIGN_BONUS_FIELDS.forEach(function (field) {
      campaign['phoenix_' + field] = plan[field];
    });
    return campaign;
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
    var phone = readOptionalPhone(opts);
    var deliveryChannel = normalizeDeliveryChannel(opts.delivery_channel || opts.deliveryChannel);
    var deliveryAddress = String(opts.delivery_address || opts.deliveryAddress || '').trim();
    if (!deliveryAddress && deliveryChannel === 'email') deliveryAddress = email;
    if (!deliveryAddress && deliveryChannel === 'whatsapp') deliveryAddress = phone;
    var isReportUnlock = !!(opts.report_id || opts.reportId || deliveryChannel || opts.channel_consent !== undefined);
    var hasValidEmail = isValidEmail(email);
    var hasValidDelivery = validateDeliveryAddress(deliveryChannel, deliveryAddress);
    if (!hasValidEmail && !(isReportUnlock && hasValidDelivery)) {
      return Promise.reject(new Error(isReportUnlock ? 'invalid_delivery_address' : 'invalid_email'));
    }
    if (isReportUnlock && opts.channel_consent !== true && opts.channelConsent !== true) {
      return Promise.reject(new Error('missing_channel_consent'));
    }
    var payload = {
      name: opts.name || firstName,
      email: email || (deliveryChannel === 'email' ? deliveryAddress : ''),
      phone: phone || undefined,
      first_name: firstName,
      quiz_id: opts.quiz_id || opts.quizId || '',
      topic: opts.topic || '',
      funnel_slug: opts.funnel_slug || opts.funnelSlug || '',
      score: opts.score != null ? opts.score : null,
      score_band: opts.score_band || opts.scoreBand || null,
      answers_json: opts.answers_json || opts.answersJson || null,
      tags: opts.tags || [],
    };
    if (deliveryChannel) {
      payload.delivery_channel = deliveryChannel;
      payload.delivery_address = deliveryAddress;
      payload.channel_consent = true;
      if (deliveryChannel === 'whatsapp' && !payload.phone) payload.phone = deliveryAddress;
    }
    REPORT_PAYLOAD_FIELDS.forEach(function (field) {
      var camel = field.replace(/_([a-z])/g, function (_, ch) { return ch.toUpperCase(); });
      var value = opts[field] !== undefined ? opts[field] : opts[camel];
      if (value !== undefined && value !== null && value !== '') {
        payload[field] = value;
      }
    });
    var campaignPayload = resolveCampaignPayload(opts);
    Object.keys(campaignPayload).forEach(function (key) {
      payload[key] = campaignPayload[key];
    });
    markCaptured({ email: email, first_name: firstName, cid: opts.cid });
    trackLeadSubmit(payload.funnel_slug, payload.topic);
    return postToGhl(payload).then(function () {
      return payload;
    });
  }

  function captureReportUnlock(opts) {
    opts = opts || {};
    opts.channel_consent = opts.channel_consent !== undefined ? opts.channel_consent : opts.channelConsent;
    opts.tags = opts.tags || ['source_freebie_quiz', 'freebie_report_requested'];
    return captureLead(opts);
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
    captureReportUnlock: captureReportUnlock,
    validateDeliveryAddress: validateDeliveryAddress,
    initBreathworkLanding: initBreathworkLanding,
    initToolPage: initToolPage,
    somaticAppUrl: somaticAppUrl,
    scoreBand: scoreBand,
    trackLeadSubmit: trackLeadSubmit,
  };
})(typeof window !== 'undefined' ? window : this);
