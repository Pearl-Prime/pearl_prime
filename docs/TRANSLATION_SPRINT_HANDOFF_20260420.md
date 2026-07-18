# CJK Atom Translation Sprint — Handoff Doc
**Date:** 2026-04-20  
**Branch:** `agent/browser-translation-scripts-20260416`  
**Owner:** Pearl_GitHub / Pearl_PM  

---

## Coverage Snapshot (as of handoff)

| Locale | Files on Disk | Target | Coverage | Server Done | Server Pending | Server Failed |
|--------|--------------|--------|----------|-------------|----------------|---------------|
| en-US  | 4,531        | 4,531  | **100%** | —           | —              | —             |
| zh-CN  | 2,968        | 4,531  | **65%**  | 2,968       | 398            | 840           |
| zh-TW  | 2,414        | 4,531  | **53%**  | 2,414       | 1,145          | 526           |
| ja-JP  | 790          | 4,531  | **17%**  | 139 (server-tracked) | 4,027 | 0     |

> **ja-JP note:** 790 files were produced before the queue server existed and are not in server state. Server "done" only tracks items dispatched via the queue this sprint.

---

## Infrastructure

### Queue Server
```bash
# Start (from worktree root)
python3 scripts/translation/browser_queue_server.py \
  --port 8765 \
  --ssl-cert artifacts/translation/server.crt \
  --ssl-key artifacts/translation/server.key \
  --locales zh-TW zh-CN ja-JP

# Check status
curl -sk https://127.0.0.1:8765/status | python3 -m json.tool
```
State persists in `artifacts/translation/browser_queues/` — survives restarts.  
Stale timeout: 300s. Max attempts per item: 3.

### Worker Assignment

| Locale | Engine | Worker IDs | Concurrency limit |
|--------|--------|-----------|-------------------|
| zh-TW  | Qwen (chat.qwen.ai) | tw0, tw1 | ≤ 3–4 per account |
| zh-CN  | Qwen (chat.qwen.ai) | cn0–cn4  | ≤ 3–4 per account |
| ja-JP  | Rakuten AI (ai.rakuten.co.jp) | jp0–jp9 | ≤ 10 (slow, ~2 min/item) |

---

## Qwen Rate Limit — Critical Info

**Qwen has a daily per-account usage cap.** Two accounts have already been exhausted:
- Account 1 (original): hit cap on 2026-04-19 morning
- Account 2 (oneteamtech.com Google): hit cap on 2026-04-20

**Symptoms of rate limit:**  
`{"code":"RateLimited","details":"You've reached the upper limit for today's usage."}`  
Workers keep cycling (count goes up) but server `done` count freezes.

**Test before injecting workers:**
```javascript
// Paste in any logged-in chat.qwen.ai tab console
(async()=>{const cr=await fetch('/api/v2/chats/new',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({chat_mode:'normal'})}).then(r=>r.json());const cid=cr.data.id;const fid=crypto.randomUUID();const rp=await fetch('/api/v2/chat/completions?chat_id='+cid,{method:'POST',headers:{'Content-Type':'application/json','X-Platform':'pc_web','X-Requested-With':'XMLHttpRequest'},body:JSON.stringify({stream:true,incremental_output:true,version:'2.1',chat_id:cid,chat_mode:'normal',model:'qwen3.6-plus',parent_id:null,messages:[{fid,parentId:null,childrenIds:[],role:'user',content:'Say hi.',user_action:'chat',files:[],timestamp:Math.floor(Date.now()/1000),models:['qwen3.6-plus'],chat_type:'t2t',feature_config:{thinking_enabled:false,output_schema:'phase'}}]})});const reader=rp.body.getReader();const{value}=await reader.read();reader.cancel();console.log(new TextDecoder().decode(value).slice(0,200));})()
```
- If response starts with `data:` → account is good, inject workers
- If `"code":"RateLimited"` → need fresh account
- If `"code":"Unauthorized"` → not logged in

---

## What's Left

### zh-CN — **398 items** (~30–40 min at full Qwen speed)
Practically done. One fresh Qwen account with 3–5 workers will finish it in a single session.

### zh-TW — **1,145 items** (~1.5–2 hrs at full Qwen speed)
About halfway through. Needs 2–3 Qwen sessions (daily cap) or multiple accounts.

### ja-JP — **~3,741 untranslated** (4,531 − 790 pre-queue)
Rakuten AI is the only engine. At 10 workers × ~2 min/item = ~30 items/hr.  
Estimated time to complete: **125+ hours** of Rakuten runtime.  
**This needs either:** a faster engine (DashScope API, GPT-4o API) or sustained Rakuten sessions over many days.

### Failed Items
- zh-CN: 840 failed (exhausted 3 retries — likely very short atoms or API timeouts)
- zh-TW: 526 failed
- These are logged in `artifacts/translation/browser_failures/{locale}.jsonl`
- Retry strategy: reset failed items in state JSON, re-queue manually

---

## Open Tabs (as of handoff)

### Qwen tabs (rate-limited — new account needed to use)
- 730344308, 730344309–730344315 (8 tabs at chat.qwen.ai)

### Rakuten tabs (10 workers, jp0–jp9)
- 730344129, 730344277, 730344276, 730344305
- 730344278, 730344279, 730344280, 730344281, 730344306, 730344283

---

## How to Resume

### Step 1 — Start server
```bash
cd /Users/ahjan/phoenix_omega/.claude/worktrees/crazy-clarke
python3 scripts/translation/browser_queue_server.py \
  --port 8765 --ssl-cert artifacts/translation/server.crt \
  --ssl-key artifacts/translation/server.key --locales zh-TW zh-CN ja-JP &
curl -sk https://127.0.0.1:8765/status | python3 -m json.tool
```

### Step 2 — Test Qwen account
Open a fresh Chrome window, log into chat.qwen.ai with a fresh account, run the test snippet above.

### Step 3 — Inject Qwen workers
Use worker JS from `docs/CJK_ATOM_TRANSLATION_QUEUE.md`. Change locale/worker ID per tab:
- tw0/tw1 → `'zh-TW'`
- cn0/cn1/cn2 → `'zh-CN'`
- Keep ≤ 4 concurrent per account

### Step 4 — Rakuten workers (ja-JP)
Already have tabs open. Re-inject jp0–jp9 using worker JS from `docs/CJK_ATOM_TRANSLATION_QUEUE.md`.

### Step 5 — Monitor
```bash
watch -n 30 'curl -sk https://127.0.0.1:8765/status | python3 -m json.tool'
# Disk counts:
find atoms -path "*/locales/zh-CN/CANONICAL.txt" | wc -l
find atoms -path "*/locales/zh-TW/CANONICAL.txt" | wc -l
find atoms -path "*/locales/ja-JP/CANONICAL.txt" | wc -l
```

---

## Recommended Next Steps (Priority Order)

1. **Finish zh-CN** (398 items) — one fresh Qwen account, ~30 min
2. **Finish zh-TW** (1,145 items) — 2 fresh Qwen accounts across 2 days
3. **Accelerate ja-JP** — consider DashScope API (key in `docs/INTEGRATION_CREDENTIALS_REGISTRY.md`, Singapore endpoint) to replace Rakuten for bulk speed
4. **Retry failed items** — 1,366 combined zh-CN+zh-TW failures worth retrying once queue is clear
5. **Commit translations** — stage and commit all new `atoms/*/locales/` files to branch, then PR to main

---

## Worker JS Quick Reference

Full JS for Qwen and Rakuten workers is in:  
`docs/CJK_ATOM_TRANSLATION_QUEUE.md` → "Worker JS" sections

Key variables to change per tab:
- Qwen: last line `})('zh-TW','tw0');` — change locale and worker ID
- Rakuten: `const LOCALE='ja-JP';const wid='jp0';` — change wid only
