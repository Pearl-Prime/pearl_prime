# CosyVoice2 Gradio API integration
_Exported on 4/16/2026 at 19:22:42 GMT+8 from Cursor (3.1.15)_

---

**User**

AGENT: Pearl_Dev + Pearl_PM
TASK: Modify scripts/video/generate_body_awareness_tts.py to call CosyVoice2 via Gradio API instead of REST /api/v1/tts, since Pearl Star only exposes Gradio UI at port 9880

Context
CosyVoice2 is running on Pearl Star (192.168.1.112:9880) but only as a Gradio web UI — there is no REST API at /api/v1/tts. The generate_body_awareness_tts.py script calls POST /api/v1/tts and gets 404.

Fix Strategy
Use the gradio_client Python package to call CosyVoice2's Gradio interface programmatically. This is the standard way to call Gradio apps without a REST API.

Step 1 — Discover Gradio API
# Install gradio_client if not present
pip install gradio_client

# Discover the API endpoints
python3 -c "
from gradio_client import Client
client = Client('http://192.168.1.112:9880')
print(client.view_api())
"

This will print the available Gradio API endpoints, their parameter names, and types. CosyVoice2's Gradio UI typically has:

A text input (the text to synthesize)
A speaker/voice dropdown
A language selector
An output audio component
Record the exact endpoint name (e.g., /synthesize, /generate, or a numbered endpoint like fn_index=0).

Step 2 — Update generate_body_awareness_tts.py
Replace the REST POST /api/v1/tts call with a gradio_client call:

from gradio_client import Client

def _call_cosyvoice_gradio(text: str, speaker: str, base_url: str) -> bytes:
    """Call CosyVoice2 via Gradio API."""
    client = Client(base_url)
    # The exact API call depends on Step 1 discovery
    # Typical CosyVoice2 Gradio interface:
    result = client.predict(
        text,           # text input
        speaker,        # speaker/voice selection
        api_name="/synthesize"  # or whatever the endpoint is called
    )
    # result is typically a file path to the generated audio
    with open(result, "rb") as f:
        return f.read()

Key considerations:

gradio_client.predict() returns a file path to the output audio, not raw bytes
Read the file and return bytes (same interface as the REST version)
Handle the case where CosyVoice2's Gradio uses different parameter names for different functions (zero-shot cloning vs built-in voices)
The built-in voices from config/tts/engines.yaml are: chinese_female, chinese_male, japanese_male, cantonese_female, english_female, english_male, korean_female
Step 3 — Keep REST as Fallback
Don't delete the REST code. Make it a fallback:

def _call_cosyvoice(text: str, speaker: str, base_url: str) -> bytes:
    """Try Gradio first, fall back to REST /api/v1/tts."""
    try:
        return _call_cosyvoice_gradio(text, speaker, base_url)
    except Exception as e:
        logger.warning("Gradio call failed (%s), trying REST /api/v1/tts", e)
        return _call_cosyvoice_rest(text, speaker, base_url)

Step 4 — Also Update tiktok_body_awareness_pipeline.py
The main video pipeline script also calls CosyVoice2 for ahjan narration. Apply the same Gradio proxy fix there so it doesn't 404 either.

Step 5 — Test
# Single teacher (ahjan → TTS)
COSYVOICE_URL=http://192.168.1.112:9880 \
python3 scripts/video/generate_body_awareness_tts.py --teacher ahjan

# Verify output
ffprobe -show_entries format=duration -v error \
  artifacts/video/tiktok_body_awareness/ahjan/tts/narration_full.wav

# Play it
afplay artifacts/video/tiktok_body_awareness/ahjan/tts/narration_full.wav

Then run for all teachers:

COSYVOICE_URL=http://192.168.1.112:9880 \
python3 scripts/video/generate_body_awareness_tts.py

CLOSEOUT_RECEIPT required fields
AGENT / TASK / COMMIT_SHA / FILES_WRITTEN / STATUS / NEXT_ACTION
Evidence: ahjan/tts/narration_full.wav plays correctly with CosyVoice2 English male voice
NEXT_ACTION: Run full video pipeline (--all-teachers) with narration tracks integrated



---

**Cursor**

Implementing Gradio-based CosyVoice2 calls with REST fallback. Reading the current scripts and attempting API discovery.



Discovering the Gradio API (if reachable) and checking for requirements that list `gradio_client`.



Fetching component definitions for `generate_audio` inputs:



---

**User**

stop all tts for now. 

---

**Cursor**

Disabling TTS in the body-awareness pipeline so we use ambient-only audio (no CosyVoice calls).



---

**User**

we will do tts later. stop all jobs now

---

**Cursor**

Stopping background jobs and disabling TTS in the pipeline so nothing keeps calling CosyVoice.



Stopping the running pipeline, stuck `curl` requests to CosyVoice, and the related `ffmpeg` job. Disabling TTS in the pipeline (opt-in via env when we're ready).



Here’s what was done:

### Stopped processes
These were terminated (`kill -9`):
- **`tiktok_body_awareness_pipeline.py --all-teachers`** (PID 72029)
- **`ffmpeg`** rendering `adi_da` `hook_01` (PID 72452)
- **Stuck `curl`** calls to `192.168.1.112:9880` (heartbeat / probe) and their shell wrappers (PIDs 72744, 72346, 72724, 72195)

A follow-up check showed **no** remaining `tiktok_body_awareness_pipeline` or `:9880` processes.

If anything else is still hung (e.g. an old Python `Client("http://192.168.1.112:9880")` from an earlier test), run:

`pkill -f '192.168.1.112:9880'`

Your **`tail -f ...pipeline_batch.log`** was left running so you can keep watching the log; stop it with Ctrl+C in that terminal if you want.

### TTS off in code
In `tiktok_body_awareness_pipeline.py`, **`_teacher_uses_tts` now returns `False` unless** you set:

`ENABLE_BODY_AWARENESS_TTS=1` (or `true` / `yes`)

So ahjan runs **ambient-only** like the other teachers until you turn that on for a later CosyVoice/Gradio pass.

The module docstring was updated to match (no default CosyVoice in the usage line).

---

**User**

did you complete any?

---

**Cursor**

Here’s a straight split:

### Completed (the “stop TTS / stop jobs” request)
- **Stopped** the running `tiktok_body_awareness_pipeline.py --all-teachers`, the **ffmpeg** job it had spawned, and the **stuck `curl`** calls to CosyVoice (`:9880`).
- **Turned TTS off by default** in `tiktok_body_awareness_pipeline.py`: narration only runs if you set **`ENABLE_BODY_AWARENESS_TTS=1`** (or `true` / `yes`); otherwise everyone (including ahjan) gets **ambient-only**.
- **Adjusted** the top-of-file **docstring** so it doesn’t imply CosyVoice is always used.

### Not completed (the earlier Pearl_Dev task)
- **Gradio `gradio_client` path** replacing REST `/api/v1/tts` was **not** finished (exploration only; `gradio_client` on Python 3.9 vs Gradio 6 was problematic).
- **`scripts/video/generate_body_awareness_tts.py`** was **not** added/updated as a finished script (it wasn’t in the tree when we looked).
- **`tiktok_body_awareness_pipeline.py` was not** switched to a finished Gradio implementation; the old **`synthesize_cosyvoice` + REST** block is almost certainly still there, it’s just **not used** while TTS is off.
- **Tests** (`ffprobe`, `afplay`, full teacher run) and a **commit / CLOSEOUT_RECEIPT** for that TTS work were **not** done.

So: **yes, the “stop jobs + disable TTS for now” work is done.** The **CosyVoice/Gradio migration** from the first task is **not** complete.

---

**User**

do you have sai_maa_vid.mp4 or ra.mp4 ?
were you helping me move vids? 

