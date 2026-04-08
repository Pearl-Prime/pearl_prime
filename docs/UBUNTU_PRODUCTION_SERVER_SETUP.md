# Phoenix Omega — Ubuntu Production Server Setup

**Purpose:** Reference for the Ubuntu content-production server running image generation, TTS, and LLM services for Phoenix Omega.  
**Last updated:** 2026-04-07  
**Setup date:** 2026-04-07  
**OS:** Ubuntu 24.04 (Noble)  

---

## Overview

This server runs all local AI inference for Phoenix Omega content production:

| Service | Port | Purpose |
|---------|------|---------|
| Ollama (Qwen3:14b) | 11434 | CJK content writing / LLM |
| ComfyUI | 8188 | Image generation (FLUX.1-dev) |
| CosyVoice2 | 9880 | Chinese / Japanese / Korean TTS |

Content is written to `~/content_bank/` and scripts live in `~/phoenix_server/phoenix_omega/`.

---

## Directory Layout

```
~/phoenix_server/
  ComfyUI/               # Image generation (FLUX.1-dev)
    venv/                # Python venv with PyTorch 2.11 (CUDA 13.0)
    models/
      unet/              # FLUX.1-dev unet — requires HF auth (see below)
      clip/              # clip_l.safetensors (235MB) ✓
                         # t5xxl_fp16.safetensors (9.2GB) ✓
      vae/               # ae.safetensors — requires HF auth (see below)
  CosyVoice2/            # CJK TTS server
    venv/                # Python venv
    pretrained_models/
      CosyVoice2-0.5B/   # ~2GB pretrained model ✓
  phoenix_omega/         # This repo

~/content_bank/
  covers/
  manga_panels/
  manga_covers/
  video_bank/
  tts_audio/
  books/
  epubs/
  videos/
    youtube/
    tiktok/
```

---

## Installed Components

### System packages
All installed via `apt` (Ubuntu 24.04 already had these):
- `git`, `git-lfs`, `python3`, `python3-pip`, `python3-venv`
- `ffmpeg` 6.1.1, `imagemagick`
- `build-essential`, `cmake`
- `libsndfile1`, `libsox-dev`, `sox`
- `wget`, `unzip`

### Ollama + Qwen3:14b
- Ollama v0.20.3 at `/usr/local/bin/ollama`
- Model: `qwen3:14b` (9.3GB, ID `bdbd181c33f2`)
- Auto-starts via Ollama's own systemd service
- API endpoint: `http://localhost:11434/v1`

### ComfyUI
- Cloned from `https://github.com/comfyanonymous/ComfyUI`
- Python venv at `~/phoenix_server/ComfyUI/venv/`
- PyTorch 2.11.0+cu130 (CUDA 13.0)
- Start: `cd ~/phoenix_server/ComfyUI && source venv/bin/activate && python main.py --listen 0.0.0.0 --port 8188`
- systemd service: `comfyui.service` (enabled, starts on boot)

### FLUX.1-dev Models (ComfyUI)
FLUX.1-dev is a **gated model** on HuggingFace — requires authentication:

```bash
# Install HF CLI and log in first:
pip install huggingface_hub
huggingface-cli login   # enter your HF token

# Then download:
wget --header="Authorization: Bearer <HF_TOKEN>" \
  https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors \
  -P ~/phoenix_server/ComfyUI/models/unet/

wget --header="Authorization: Bearer <HF_TOKEN>" \
  https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors \
  -P ~/phoenix_server/ComfyUI/models/vae/
```

Already downloaded (no auth required):
- `models/clip/clip_l.safetensors` (235MB)
- `models/clip/t5xxl_fp16.safetensors` (9.2GB)

### CosyVoice2 (CJK TTS)
- Cloned from `https://github.com/FunAudioLLM/CosyVoice`
- Python venv at `~/phoenix_server/CosyVoice2/venv/`
- Pretrained model: `FunAudioLLM/CosyVoice2-0.5B` downloaded to `pretrained_models/CosyVoice2-0.5B/`
- Start: `cd ~/phoenix_server/CosyVoice2 && source venv/bin/activate && python webui.py --port 9880`
- systemd service: `cosyvoice.service` (enabled, starts on boot)

### Edge-TTS (backup TTS)
- `edge-tts` 7.2.8 installed system-wide (`--break-system-packages`)
- Tested voices:
  - Chinese: `zh-CN-XiaoxiaoNeural`
  - Japanese: `ja-JP-NanamiNeural`
  - Korean: `ko-KR-SunHiNeural`

---

## Environment Variables

Added to `~/.bashrc`:

```bash
export QWEN_BASE_URL="http://localhost:11434/v1"
export QWEN_MODEL="qwen3:14b"
export COMFYUI_URL="http://localhost:8188"
export COSYVOICE_URL="http://localhost:9880"
export PHOENIX_SERVER_ROOT="$HOME/phoenix_server"
export CONTENT_BANK="$HOME/content_bank"
```

---

## systemd Services

Both services are **enabled** (auto-start on boot):

```bash
# Start
sudo systemctl start comfyui cosyvoice

# Stop
sudo systemctl stop comfyui cosyvoice

# Status / logs
sudo systemctl status comfyui
journalctl -u comfyui -f

sudo systemctl status cosyvoice
journalctl -u cosyvoice -f
```

Service files:
- `/etc/systemd/system/comfyui.service`
- `/etc/systemd/system/cosyvoice.service`

Ollama auto-starts via its own installer-created service (`ollama.service`).

---

## Connecting from Mac

Replace `localhost` with the server's LAN IP address:

| Service | URL |
|---------|-----|
| ComfyUI | `http://<server-ip>:8188` |
| Ollama API | `http://<server-ip>:11434` |
| CosyVoice2 | `http://<server-ip>:9880` |

The `QWEN_BASE_URL`, `COMFYUI_URL`, and `COSYVOICE_URL` env vars in Phoenix Omega scripts should be updated to use the server IP when running from the Mac.

---

## Outstanding Steps

- [ ] Download FLUX.1-dev unet (`flux1-dev.safetensors`, ~12GB) — requires HF token
- [ ] Download FLUX VAE (`ae.safetensors`) — requires HF token
- [ ] Verify ComfyUI generates images end-to-end once FLUX models are present
- [ ] Verify CosyVoice2 webui loads without errors after full requirements install

---

## Quick Health Check

```bash
# Ollama
ollama list

# ComfyUI models present
ls ~/phoenix_server/ComfyUI/models/unet/
ls ~/phoenix_server/ComfyUI/models/vae/

# Edge-TTS
edge-tts --voice zh-CN-XiaoxiaoNeural --text "测试" --write-media /tmp/test.mp3

# Services
sudo systemctl status comfyui cosyvoice
```
