# Tool Catalog

URLs, input patterns, and quota detection for each research engine.

---

## 1. Gemini Deep Research

| Field            | Value |
|------------------|-------|
| URL              | `https://gemini.google.com/` |
| Deep research    | Select "Deep Research" mode from the model/mode picker (look for a dropdown or toggle near the input area) |
| Input selector   | Main text input area at bottom of page |
| Submit           | Press Enter or click send button |
| Results timing   | 2–5 minutes for deep research mode |

### Quota detection patterns
- "You've reached your usage limit"
- "Deep Research is temporarily unavailable"
- "Try again in a few hours"
- Model picker grayed out / deep research option missing
- Redirect to sign-in when previously signed in

### Tips
- If deep research mode is not visible, the account may not have access or quota
  is already exhausted. Fall through immediately.
- Gemini shows a "researching" animation with a progress indicator. Wait for it
  to show final results with source links.
- Sources appear as numbered footnotes and/or a "Sources" expandable section.

---

## 2. ChatGPT Deep Research

| Field            | Value |
|------------------|-------|
| URL              | `https://chatgpt.com/` |
| Deep research    | Select "Deep Research" from the model picker dropdown (may show as "o3 + deep research" or similar) |
| Input selector   | Main text input area |
| Submit           | Press Enter or click send button |
| Results timing   | 2–5 minutes |

### Quota detection patterns
- "You've reached your limit for deep research"
- "Deep research is available X times per month"
- "Upgrade to Plus" or "Upgrade to Pro"
- Counter showing "0 remaining" near the model picker
- 429 or rate limit toast notification

### Tips
- ChatGPT deep research shows a multi-step "Researching..." panel with a list
  of searches it's performing. Wait for the final compiled answer.
- Sources appear as inline linked citations `[source title](url)` and sometimes
  a "Sources" list at the bottom.
- If deep research is exhausted, do NOT use this tab for the regular ChatGPT
  fallback. The regular fallback (Priority 4) should open a fresh tab and use
  the standard GPT-4o model with "Search the web" enabled.

---

## 3. Claude Deep Research

| Field            | Value |
|------------------|-------|
| URL              | `https://claude.ai/` |
| Deep research    | Look for "Research" or "Deep Research" mode toggle if available |
| Input selector   | Main text input area |
| Submit           | Press Enter or click send button |
| Results timing   | 1–5 minutes |

### Quota detection patterns
- "You've reached your message limit"
- "You've used your daily allowance"
- "Please wait before sending more messages"
- "Usage limit reached"
- Redirect to upgrade page

### Tips
- Claude may present research as a structured document with inline citations.
- If Claude does not have a dedicated "deep research" toggle, use the standard
  chat with an explicit research prompt: "Please search the web and research
  [topic]. Provide all source URLs."
- Check if web search / research features are enabled for the account.

---

## 4. ChatGPT Regular (Web Search Fallback)

| Field            | Value |
|------------------|-------|
| URL              | `https://chatgpt.com/` |
| Mode             | Standard model (GPT-4o or latest) with web browsing enabled |
| Input selector   | Main text input area |
| Submit           | Press Enter |
| Results timing   | 30–90 seconds |

### Quota detection patterns
- "You've reached your limit"
- Rate limit toast
- Login wall / session expired

### Tips
- This is the final fallback for the default cascade. If this is also exhausted,
  report to the user that all tools are quota-limited.
- Prompt with: "Search the web for [topic]. Provide source URLs for every claim."
- Enable web search explicitly if there's a toggle (magnifying glass or "Search"
  icon near the input).

---

## 5. DeepSeek Deep Research

| Field            | Value |
|------------------|-------|
| URL              | `https://chat.deepseek.com/` |
| Deep research    | Select "DeepThink" or "Deep Research" mode if available in the model picker |
| Input selector   | Main text input area |
| Submit           | Press Enter or click send button |
| Results timing   | 1–5 minutes |

### Quota detection patterns
- "Server is busy"
- "Too many requests, please try again later"
- "You've reached today's limit"
- "Service temporarily unavailable"
- Queue position indicator that doesn't advance

### Regular search fallback
If deep research quota is hit, switch to standard DeepSeek chat mode with search
enabled (look for a "Search" toggle). Use that before falling through to the
default cascade.

### Tips
- DeepSeek is especially strong for Chinese market data, regulations, consumer
  trends, and business intelligence in mainland China.
- For mainland China topics, consider submitting the query in Chinese for better
  source coverage. Translate the findings back to English in the output report.
- Sources may appear as footnotes or inline references.

---

## 6. Rakuten AI Deep Research

| Field            | Value |
|------------------|-------|
| URL              | `https://rakuten.ai/` |
| Deep research    | Look for deep research or advanced search mode |
| Input selector   | Main text input or search area |
| Submit           | Press Enter or click search/send |
| Results timing   | 1–3 minutes |

### Quota detection patterns
- "Rate limit reached"
- "Please try again later"
- "Service temporarily unavailable"
- Login requirement when previously accessible

### Regular search fallback
If deep research is exhausted, switch to standard Rakuten AI search mode before
falling through to the default cascade.

### Tips
- Rakuten AI is strong for Japanese, Korean, and Taiwanese market data.
- For Japan-specific topics, consider submitting in Japanese for better local
  source coverage.
- Cross-reference with default cascade tools for English-language sources.

---

## General quota handling

When you detect quota exhaustion on any tool:

1. **Screenshot** the quota message
2. **Log** it in your working notes: `QUOTA_HIT: [tool] at [time]`
3. **Do not retry** the same tool in this research session
4. **Move to next** tool in the cascade immediately
5. If ALL tools in the cascade are exhausted, report to the user:
   "All research tools have hit their daily quotas. Results below are from
   [list tools that worked]. Remaining tools can be tried tomorrow."
