# JP/CN Specific Finds — Phoenix Omega Manga AI Asset Audit

**Date:** 2026-04-29
**Surface scope:** Rakuten AI / Qwen Chat / Tongyi Wanxiang / ModelScope / Pixiv / note.com / Zenn / Qiita / Bilibili / Zhihu
**WebFetch calls used:** 4 / 12 (rest covered via WebSearch snippets)
**Method:** Free WebSearch triage first, WebFetch reserved for highest-value confirmations. No paid API calls. No image generation. URLs only — citation-grade, not deep-dive.

---

## TL;DR

- **Biggest miss in the English ecosystem:** the **Qwen-Image / Qwen-Image-Edit** ecosystem (Alibaba, 2025–2026) has shipped a flood of manga-relevant LoRAs and ComfyUI workflows on **ModelScope** and Bilibili that English-only searches barely surface. This is the asset-tier worth forking. Specifically: `Qwen-Image-Edit-2511`-based **manga colorization** and **photo-to-comic** LoRAs, plus `Qwen-Image-i2L` (one-image-to-LoRA), all 2025–2026.
- **Rakuten AI Studio is not a manga asset surface.** `ai.rakuten.co.jp` / `corp.rakuten.co.jp/ai` is a B2B LLM-agent / RMS-assistant product (Rakuten AI 3.0, GENIAC project, March 2026). No public template gallery or manga LoRA hub. Confirmed CONTENT_NOT_FOUND for the operator's specific framing.
- **note.com and Zenn have a real, dateable JP creator cookbook tradition** for manga generation — the workflow `Stable Diffusion → Anime Lineart LoRA → CLIP STUDIO assembly` is documented end-to-end in JP and would save Phoenix months if forked rather than rebuilt. note.com 2025 articles also document Qwen-Image-Edit manga colorization with explicit commercial-license caveats (local-only for copyrighted works).
- **CN side: Bilibili is the dominant tutorial surface, Zhihu is the dominant text-tutorial surface.** Both have CONTENT for FLUX + LoRA + 漫画 workflows. Civitai/Shakker hosts the actual `MonoManga 黑白漫画` LoRA the CN community uses; ModelScope mirrors many.
- **Qwen-VL as manga reverse-prompt QA: SPARSE.** No public benchmark vs WD-EVA02 specifically on manga. General Qwen-VL captioning benchmarks exist (98.4% cheaper than OpenAI on plain images), but published evidence notes Qwen-class VLMs **misreport panel counts and panel content** on comics. WD-EVA02 remains the community-default manga tagger. Phoenix should not assume Qwen-VL replaces WD-EVA02 without an in-house bench.

---

## Rakuten AI Studio (ai-studio.rakuten.co.jp)

**Status: NOT_FOUND (for manga assets) / CONFIRMED_AS_DIFFERENT_PRODUCT**

- The domain `ai-studio.rakuten.co.jp` does not surface in any search snippet. The actual Rakuten AI product lives at `ai.rakuten.co.jp` and `corp.rakuten.co.jp/ai`.
- Rakuten AI 3.0 (announced March 2026, GENIAC project) is a **Japan-specialized LLM agent** for business — chatbot, prompt templates by profession, RMS review-reply assistant, "Friendly/Business" tone presets. No image-generation template gallery, no manga LoRAs.
- The "templates" that Rakuten AI for Business surfaces are **prompt templates for professional text tasks**, not image-style templates.

**Manga-relevant findings:** none.
**URLs cited:**
- https://ai.rakuten.co.jp/
- https://corp.rakuten.co.jp/ai/
- https://weel.co.jp/media/innovator/rakuten-ai/ (third-party explainer)
- https://app-tatsujin.com/rakuten-ai-new-cart-features-2026/

**Recommendation:** Stop watching Rakuten as a manga-asset source. It's a competing LLM, not a Stable-Diffusion-style image hub.

---

## Qwen Chat / Tongyi Wanxiang / Qwen-Image

**Status: CONTENT — and this is the highest-value finding in the entire scan.**

The Qwen-Image family (Alibaba's open foundation image model, 20B MMDiT) is generating a community manga LoRA ecosystem that English-only searches mostly miss. Key surfaces:

- **Qwen-Image-2.0** (Feb 10, 2026) — released with explicit support for "professional typography rendering... including PPTs, posters, **comics**, and more." Generates manga where dialogue and per-frame composition can be specified.
- **Qwen-Image-2512** (recent; "Finer Details, Greater Realism" — official Qwen blog post).
- **Qwen-Image-Edit-2511** — base model with **selected popular LoRAs integrated directly**, including manga-relevant transforms.
- **Qwen-Image-i2L** — one-image-to-LoRA, "zero-barrier LoRA training." Lowers the bar for personalized style transfer dramatically (this is a fork-not-build candidate).
- **`Qwen-Image-Edit-2511-Multiple-Angles-LoRA`** on ModelScope (`fal/Qwen-Image-Edit-2511-Multiple-Angles-LoRA`) — multi-angle generation, useful for character consistency across panels.
- **`ColorManga` Qwen LoRA** on Civitai (model ID 1985245) — manga colorization LoRA designed for Qwen-Image base.
- **Tongyi Wanxiang 2.5 / 2.6** (Alibaba video+image platform) — Wanxiang 2.6 supports **multi-shot narrative with intelligent scheduling**, multi-character acting in 15-second video — relevant to motion-comic / manga storyboard generation, though video-tier not still-tier.

**Qwen Chat / chat.qwen.ai:** public landing exists; manga generation is reachable via the "image generation" feature, but it's a hosted chat surface, not a downloadable preset library. No public template gallery in the Civitai sense.

**Manga-relevant findings:** Qwen-Image is now a first-class manga generation base model with active LoRA development on ModelScope and HuggingFace. The English ecosystem mostly talks about FLUX; the CN ecosystem has split between FLUX and Qwen-Image, with Qwen-Image winning for **complex text rendering and Chinese typography** — directly relevant if Phoenix wants speech bubbles in CN/JP.

**License tiers:**
- Qwen-Image base model: Apache 2.0 — 🟢 commercial-clean.
- Community LoRAs on ModelScope: mixed; most permissive (CC-BY-4.0 or Apache), some 🟡 (non-commercial). Each LoRA must be checked individually before fork.

**URLs cited:**
- https://github.com/QwenLM/Qwen-Image
- https://qwen.ai/blog?id=qwen-image-2512
- https://chat.qwen.ai/
- https://qwenimages.com/blog/qwen-image-edit-release
- https://www.modelscope.cn/learn/3343 (Qwen-Image-i2L: "一张图秒生 LoRA")
- https://www.modelscope.cn/models/fal/Qwen-Image-Edit-2511-Multiple-Angles-LoRA
- https://civitai.com/models/1985245/colormanga
- https://huggingface.co/spaces/Onise/Qwen-Image-Edit-2509-LoRAs-Fast
- https://tongyi.aliyun.com/wan/
- https://www.aibase.com/news/23555 (Qwen-Image-i2L coverage)

---

## ModelScope (modelscope.cn)

**Status: CONTENT — Alibaba's HuggingFace equivalent, hosting both official Damo models and community LoRAs.**

Confirmed manga-relevant assets:

- **`damo/cv_cartoon_stable_diffusion_illustration`** ("卡通系列文生图模型-漫画风") — Damo (Alibaba official) cartoon/manga-style text-to-image model. Confirmed live (page exists) but full license/usage detail required a deeper read than budget allowed. Likely 🟡 commercial-conditional under Damo's typical license terms — verify before forking.
- **`iic/multi-style_portrait_stylization`** — "AI人像多风格漫画" (multi-style portrait → manga). Hosted as a ModelScope Studio (interactive).
- **`SD15-LoRA-AnimeLineartStyle`** (`sd_lora/SD15-LoRA-AnimeLineartStyle`) — manga lineart LoRA for SD1.5. The CN-ecosystem version of the workflow that JP creators run on `animeoutlineV4`.
- **`strangerzone/Ghibli-Flux-Cartoon-LoRA`**, **`strangerzone/Flux-Ghibli-Art-LoRA`**, **`strangerzone/Flux-Animex-v2-LoRA`** — anime-adjacent FLUX LoRAs mirrored on ModelScope.
- **`strangerzone/Flux-Ultimate-LoRA-Collection`** — an aggregator collection of FLUX style LoRAs.
- **`InstantX/FLUX.1-dev-LoRA-Makoto-Shinkai`** — Makoto Shinkai-style FLUX LoRA (anime-adjacent, not strict manga, but commonly co-used).
- **`DiffSynth-Studio/ArtAug-lora-FLUX.1dev-v1`** — general art-augmentation LoRA from DiffSynth (active CN community).

**Manga-relevant findings:** ModelScope is the right CN mirror to pull from when an asset isn't already on HuggingFace. Several Damo (Alibaba official) models include 商用 (commercial) licensing terms that the English ecosystem hasn't translated/surfaced — Phoenix's procurement layer should add a ModelScope crawler pass.

**License tiers:**
- Damo/Alibaba official models: typically 🟡 commercial-conditional (Apache-style with attribution + Damo's "responsible use" addendum). Per-model verification required.
- Community LoRAs (strangerzone, prithivMLmods, fal, etc.): mixed 🟢 / 🟡 — same author, same license as their HuggingFace mirror in most cases.

**URLs cited:**
- https://modelscope.cn/aigc
- https://modelscope.cn/docs/aigc/intro
- https://modelscope.cn/models/damo/cv_cartoon_stable_diffusion_illustration/summary
- https://modelscope.cn/studios/iic/multi-style_portrait_stylization
- https://www.modelscope.cn/models/sd_lora/SD15-LoRA-AnimeLineartStyle
- https://modelscope.cn/models/strangerzone/Ghibli-Flux-Cartoon-LoRA
- https://www.modelscope.cn/models/strangerzone/Flux-Animex-v2-LoRA
- https://modelscope.cn/models/InstantX/FLUX.1-dev-LoRA-Makoto-Shinkai
- https://www.modelscope.cn/models/DiffSynth-Studio/ArtAug-lora-FLUX.1dev-v1

---

## Pixiv (AI-illustrator prompt-share posts)

**Status: SPARSE on the public Pixiv side; CONTENT_LOCKED on pixivFANBOX.**

- **pixivFANBOX banned AI-generated works** (policy effective 2023, reaffirmed). Therefore the rich JP "AI prompt cookbook" tradition that used to live on FANBOX is now mostly archival or paywalled-legacy. Source: FANBOX official policy post.
- **One outstanding legacy resource** is still live: **studiomasakaki.fanbox.cc** ("AIイラストが理解る！【スタジオ真榊】") — they ship a "プロンプト超辞典" (Prompt Mega-Dictionary) for AnimagineXL and NovelAIv3, paywalled, but the existence of a 2024+ updated edition is confirmed. This is a fork-not-build candidate if Phoenix is willing to pay for a one-time purchase.
- **Pixiv proper** restricts mass AI uploads but hasn't banned them; some authors share prompts in captions. Surface is noisy, not curated.

**Manga-relevant findings:** treat Pixiv/FANBOX as a low-yield surface for asset reuse — the bans + paywalls outweigh the open-share signal.

**License tiers:**
- studiomasakaki "Prompt Mega-Dictionary": 🟡 commercial-conditional (paid creator content; verify reuse rights for derivative work).

**URLs cited:**
- https://studiomasakaki.fanbox.cc/
- https://studiomasakaki.fanbox.cc/posts/7391318
- https://official.fanbox.cc/posts/5932126 (FANBOX AI ban policy)
- https://fanbox.pixiv.help/hc/en-us/articles/20299395982489-What-is-AI-generated-content
- https://hikari-aiart.com/stablediffusion-manga-pronpt-models/ (third-party JP cookbook)

---

## note.com (JP creator tutorials)

**Status: CONTENT — second-strongest surface after Qwen/ModelScope.**

- **Manga colorization with Qwen-Image-Edit / FLUX Kontext** — confirmed via fetch of `note.com/catap_art3d/n/nb24d97f8c2b9` (Sep 4, 2025): the author runs both `FLUX Kontext (Nunchaku version, via Krita-ai-diffusion)` and `Qwen_Image_Edit-Q3_K_M.gguf + Qwen-Image-Lightning-4steps-V1.0.safetensors` on ComfyUI for manga colorization. Includes batch automation templates (¥1000/month membership for the templates). **Critical commercial caveat surfaced by the author:** for copyrighted works, only local/closed-environment processing avoids infringement — cloud services need rightsholder auth.
- **`note.com/levelma/n/nbee81ad10967`** — "Stable Diffusionで漫画風のプロンプト(呪文)とモデルについて" — open prompt cookbook for manga style. Recommends `老漫画_Monochrome manga` LoRA at weight 0.7–1.0 with `banhua, Monochromatic` triggers; `Lineart——照片线稿提取` for backgrounds; `Style shift sketch 风格转换素描草图` for sketch panels.
- **`note.com/catap_art3d/n/ned952a91511e`** — "FLUX.1 Japanese=アニメ調を回避する" — JP-specific negative-prompt patterns to stop FLUX from anime-fying when the prompt contains Japanese.
- **`note.com/ndesign0501/n/n7fa44527f71f`** — full-model comparison (FLUX.2 / Qwen / HiDream / Z-Image) from a JP studio's perspective, late 2025.
- **`note.com/asunaro_ai/n/n3eada754eb0e`** — "AI画像をPixivに投稿しはじめて1ヶ月" — meta-tutorial on the JP AI-author publishing loop (covers tagging, response patterns, takedown risk).
- **`note.com/mayu_hiraizumi/n/nfde4ea6fd661`** — ComfyUI prompt-generation pipeline using Ollama + IF_LLM (Tier-2-friendly: local Ollama, no paid API).

**Manga-relevant findings:** note.com hosts a real cookbook tradition with dated 2025 articles. The `Ollama + IF_LLM in ComfyUI` pipeline is exactly the "Tier-2 unattended" pattern Phoenix's CLAUDE.md mandates. The Catapp-Art3D author has explicitly worked the commercial-license problem and offers a paid template set; cheap to buy and audit.

**License tiers:**
- Most note.com tutorials: 🟢 free to read; the *workflows they describe* depend on the underlying LoRA's license.
- Catapp-Art3D paid template membership: 🟡 commercial-conditional (¥1000/mo, terms vary by template).

**URLs cited:**
- https://note.com/catap_art3d/n/nb24d97f8c2b9
- https://note.com/levelma/n/nbee81ad10967
- https://note.com/catap_art3d/n/ned952a91511e
- https://note.com/ndesign0501/n/n7fa44527f71f
- https://note.com/asunaro_ai/n/n3eada754eb0e
- https://note.com/mayu_hiraizumi/n/nfde4ea6fd661
- https://note.com/aiaicreate/n/n0884a97892dd
- https://note.com/henrik0516/n/ne75137b75590
- https://note.com/rich_emu5871/n/nbbcd3cbd111e
- https://note.com/blue_pen5805/n/na483c2522f4d
- https://note.com/fresh_sedum5880/n/n0a09c51fb5ca

---

## Zenn / Qiita (JP technical posts)

**Status: CONTENT — narrower than note.com but more rigorous (engineer audience).**

- **`zenn.dev/qikta/articles/9fb3818fa94af8`** — "AI漫画で社内ドキュメントを活性化した話" (Oct 2, 2024). Confirmed via fetch. End-to-end pipeline: ChatGPT 4o for script → Stable Diffusion `himawarimix` checkpoint + `Anime Lineart Style LoRA` (`<lora:animeoutlineV4_16:0.8>`) → CLIP STUDIO for assembly. Prompt skeleton: `monochrome, lineart, <lora:animeoutlineV4_16:0.8>, white background` + character spec. Negatives: `worst quality, low quality` + anatomical-error patterns. Use case is internal corporate education content — i.e., a deployment pattern, not a one-off demo. **This is the cleanest "fork the workflow" find in the JP scan.** ⚠️ Tier-1 violation only because of the ChatGPT 4o step — Phoenix would swap that for Pearl_Writer.
- **`qiita.com/GeneLab_999/items/1e9d9afcb7459606e3ac`** — "ComfyUI Flux プロンプト完全攻略ガイド" — open prompt-engineering guide for FLUX in JP, engineer-grade.
- **`qiita.com/kerimeka/items/d3cf8b338c742bc96a89`** — "Manga Editor Desu! ローカル環境構築 #StableDiffusion" — covers a real OSS tool (`Manga Editor Desu!` by ネギかも) that orchestrates ComfyUI / Forge / WebUI APIs for end-to-end manga page generation. Has Pro tier; was featured on Gigazine. **This is a candidate competitor / fork target.**
- **`corp.aicu.ai/ja/comfymaster27-20241025`** — "ComfyMaster27: 写真もイラストも線画に！ComfyUIとControlNetによる線画抽出ワークフロー" — formal lineart-extraction pipeline (ControlNet + LineAniRedmond LoRA), Oct 2024. AICU is a JP educational publisher.

**Manga-relevant findings:** the Zenn corporate-deployment article and the Qiita `Manga Editor Desu!` build are the two surfaces Phoenix should evaluate first — both ship deployable, JP-creator-validated workflows.

**License tiers:**
- Zenn / Qiita posts: 🟢 (CC-BY-style by default).
- `Manga Editor Desu!` tool: 🟡 — Pro tier exists, base may be free; verify before fork.
- `Anime Lineart Style LoRA` (`animeoutlineV4`): 🟡 — Civitai upload, license per uploader (typically OK for commercial, verify).

**URLs cited:**
- https://zenn.dev/qikta/articles/9fb3818fa94af8
- https://qiita.com/GeneLab_999/items/1e9d9afcb7459606e3ac
- https://qiita.com/kerimeka/items/d3cf8b338c742bc96a89
- https://corp.aicu.ai/ja/comfymaster27-20241025
- https://x.com/NegiTurkey/status/1861294186441646527 (Manga Editor Desu! Pro announcement)

---

## Bilibili / Zhihu (CN tutorials)

**Status: CONTENT — Bilibili = video, Zhihu = long-form text. Both active.**

**Bilibili (manga / FLUX / Qwen-Image / ComfyUI):**
- `BV1Rm421g7NM` — "用最近新出的FLUX.1模型搭建一个ComfyUI四格漫画工作流" — explicit 4-panel manga ComfyUI workflow.
- `BV1HcyGBjEep` — "Qwen-Edit 一键动漫转真人:3款LoRA独特差异实测对比" — head-to-head test of three Qwen-Edit anime-to-realistic LoRAs (i.e., the inverse direction Phoenix could use for char ref).
- `BV1wQZ4YKEdH` — "[ComfyUI+flux工作流+Lora训练] 一致性解决方案" — character consistency via FLUX + LoRA training, includes dataset and training pipeline.
- `BV1R7QLYMEsh` — "[ComfyUI] 多角色一致性完美效果控制, Flux LoRA训练数据集完整详细手把手教学" — multi-character consistency for FLUX LoRAs (directly relevant to manga cast consistency).
- `BV1JF22YpEVE` — "一键ComfyUI训练工作流：最新Flux LoRa 模型训练 x 训练人物 x 训练画风 x 训练概念" — one-click LoRA training (character / style / concept).
- `BV1arkgBWE2p` — Flux2 Klein workflow — text-to-image, image-to-image, inpainting, edit, line control, depth, multi-image edit, expansion.

**Zhihu (text tutorials):**
- `zhuanlan.zhihu.com/p/714657191` — "Flux-LoRA模型探索：7款LoRA模型出图效果一览" — comparison of 7 FLUX LoRAs incl. anime-style.
- `zhuanlan.zhihu.com/p/715697877` — "Flux持续火爆，这些Lora、ControlNet、工作流你值得拥有" — curated FLUX LoRA + ControlNet + workflow list.
- `zhuanlan.zhihu.com/p/714328678` — "FLUX.1 社区大繁荣，盘点当前支持FLUX.1的Lora模型" — FLUX.1 LoRA inventory.
- `zhuanlan.zhihu.com/p/716770443` — "使用 ComfyUI 进行本地 FLUX.1 LoRA 的训练" — local FLUX.1 LoRA training with ComfyUI.
- `zhuanlan.zhihu.com/p/1949239772930371853` — "墙裂推荐：Qwen image漫画转真人LoRa" — Qwen-Image manga→real LoRA recommendation. (Fetch was 403; URL confirmed via search snippet only.)
- **Shakker.ai** (CN-leaning Civitai equivalent): `MonoManga 黑白漫画 - 经典线条日漫风格` (`shakker.ai/modelinfo/4e4fc8081bcb4f1c966b4f30c90ff062`) — community CN-tagged monochrome manga LoRA.

**Manga-relevant findings:** the CN community has thoroughly mapped the FLUX-LoRA terrain and is now actively forking into Qwen-Image. Phoenix could compress months of LoRA-procurement R&D by treating the Zhihu pages as a curated index and the Bilibili videos as workflow validation.

**License tiers:**
- Tutorial posts: 🟢 free to read.
- Underlying LoRAs: 🟡 — most CN-uploaded LoRAs on Shakker / Civitai / ModelScope are commercial-friendly but each must be checked.

**URLs cited:** see list above; representative starting points:
- https://www.bilibili.com/video/BV1Rm421g7NM/
- https://www.bilibili.com/video/BV1R7QLYMEsh/
- https://www.bilibili.com/video/BV1HcyGBjEep/
- https://zhuanlan.zhihu.com/p/715697877
- https://zhuanlan.zhihu.com/p/714328678
- https://zhuanlan.zhihu.com/p/1949239772930371853
- https://www.shakker.ai/modelinfo/4e4fc8081bcb4f1c966b4f30c90ff062

---

## Top 5 finds Phoenix should actually evaluate

1. **Asset:** `Qwen-Image-Edit-2511` + integrated manga LoRAs (notably `ColorManga` Qwen LoRA + `Multiple-Angles-LoRA`)
   **URL:** https://github.com/QwenLM/Qwen-Image and https://www.modelscope.cn/models/fal/Qwen-Image-Edit-2511-Multiple-Angles-LoRA and https://civitai.com/models/1985245/colormanga
   **Why it matters:** Open foundation model from Alibaba, 2026, Apache 2.0 base; first-class CJK text rendering for speech bubbles; the multi-angle LoRA solves panel-to-panel character consistency, which is the hard problem in manga gen. English ecosystem mostly missed this — they're still on FLUX.
   **License tier:** 🟢 base; 🟡 per-LoRA (verify each)

2. **Asset:** `Qwen-Image-i2L` (one-image-to-LoRA, "zero-barrier" training)
   **URL:** https://www.modelscope.cn/learn/3343 (Alibaba walkthrough), https://www.aibase.com/news/23555
   **Why it matters:** Lets Phoenix turn a single character reference sheet into a character LoRA without a training run — directly attacks the cost wall of cast LoRAs at 800-config scale. If real (claim verified by Alibaba blog + AIBase coverage), this rewrites the per-character-LoRA budget.
   **License tier:** 🟢 (Apache-aligned with Qwen-Image base; verify)

3. **Workflow:** `Manga Editor Desu!` (ネギかも / NegiTurkey) — JP OSS tool that orchestrates ComfyUI / Forge / WebUI APIs for end-to-end local manga page generation
   **URL:** https://qiita.com/kerimeka/items/d3cf8b338c742bc96a89 and https://x.com/NegiTurkey/status/1861294186441646527
   **Why it matters:** This is the "we already built this" tool. JP creators run it locally; it's been featured on Gigazine. Fork target rather than rebuild target. Also a competitive-landscape datapoint — Phoenix's manga pipeline is not unique; the differentiator must be elsewhere (catalog scale, brand voice, EI authoring).
   **License tier:** 🟡 (free + Pro tier; license per repo)

4. **Cookbook:** Catapp-Art3D's note.com series (manga colorization on Qwen-Image-Edit and FLUX Kontext, with explicit commercial-license discipline)
   **URL:** https://note.com/catap_art3d/n/nb24d97f8c2b9 and https://note.com/catap_art3d/n/ned952a91511e
   **Why it matters:** Already-debugged ComfyUI workflows for the exact problem (B&W manga → color, anti-anime-fy) by a JP creator who has worked the copyright/commercial-use angle. ¥1000/mo for the templates is cheap insurance.
   **License tier:** 🟡 (paid templates; rights vary)

5. **Workflow:** Zenn corporate-manga deployment pattern (Stable Diffusion `himawarimix` + `animeoutlineV4` LoRA + CLIP STUDIO)
   **URL:** https://zenn.dev/qikta/articles/9fb3818fa94af8
   **Why it matters:** End-to-end deployment in a real corporate setting; cleanly documented; the only Tier-1 violation is the ChatGPT 4o script step, which Phoenix swaps for Pearl_Writer. This is the cleanest validated workflow for "manga as production output." The `Anime Lineart Style LoRA` family (`animeoutlineV4`) recurs across every JP/CN tutorial — strong signal that Phoenix should pin this as a baseline LoRA.
   **License tier:** 🟢 article; 🟡 LoRA (verify uploader terms)

---

## Qwen-VL as manga reverse-prompt QA

**Finding: SPARSE — no public benchmark vs WD-EVA02 specifically on manga, and the directional evidence is mildly negative.**

The Qwen-VL family (Qwen3-VL is current; technical report at arXiv 2511.21631) has strong general-purpose image captioning economics — Salad's benchmark put `Qwen 2.5 VL 3B` at 126,650 images/$ on an RTX 4080, claiming 98.4% cost savings vs OpenAI on plain image captioning. That's the bullish case.

The bearish case: the Danbooru-tagging community (`SmilingWolf/wd-eva02-large-tagger-v3` on HuggingFace, the de-facto JP-illustrator standard) uses an EVA02 backbone with 315M params trained specifically on Danbooru's ratings/character/general tag schema. Community write-ups note that **general-purpose VLMs (LLaVA, CogVLM — Qwen-VL is in the same class) misreport panel counts and panel content on comics**. There is no published paper, blog, or arXiv preprint that benchmarks Qwen-VL specifically against WD-EVA02 on a manga-specific tag set.

**Recommendation:** Phoenix should not assume Qwen-VL replaces WD-EVA02 for manga reverse-prompt QA. If the operator wants to bet on Qwen-VL, the responsible move is an in-house bench — same 1,000 manga panels, both taggers, score against a hand-labeled gold set. Until then, default to WD-EVA02 for tagging and reserve Qwen-VL for description-quality QA (the natural-language layer where it actually wins). All of this stays Tier-2-compatible because both models run locally on Pearl Star via Ollama / vLLM.

**URLs cited:**
- https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3
- https://github.com/QwenLM/Qwen3-VL
- https://arxiv.org/abs/2511.21631 (Qwen3-VL Technical Report)
- https://blog.salad.com/qwen-benchmark/
- https://github.com/IrisRainbowNeko/ML-Danbooru
- https://gwern.net/danbooru2021
