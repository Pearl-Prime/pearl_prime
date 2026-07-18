# Synthetic Reference Legality — Phoenix Omega Position Paper (2026-05-03)

**Status:** AUTHORITY (new, this PR — research-only; legal-research, not legal-advice).
**Audience:** Phoenix Omega operator + counsel, for legal review.
**Branch:** `agent/license-clean-corpus-20260503`
**Cross-references (SHA-pinned):**
- PR #838 commit `3d7118b3` — drawing-tradition + corpus framework
- PR #803 commit `f4c50142b6` — community-audit base-model license register
- This PR's `artifacts/research/license_diligence_2026-05-03.md` — Q1-Q6 license framework

---

## §1 The legal framing

When Phoenix Omega generates a reference image *from* its own trained LoRA at lower res for QA / drift-detection purposes, three theories of derivation are possible:

- **(a) Derivative of model weights:** The output is a deterministic function of the weights, conditioned on the prompt. If weights are Phoenix-owned (LoRA trained from Phoenix-rights-cleared inputs), this is a clean theory.
- **(b) Derivative of the original training data:** Plaintiffs in Andersen, Authors Guild, etc. argue model outputs are unauthorised derivative works of training inputs.
- **(c) Clean derivative (transformative use):** Defendants argue model outputs are statistical syntheses, not reproductions.

US case law has not resolved which theory wins. UK case law (Getty v. Stability AI, Nov 2025) decided on jurisdictional grounds without endorsing either theory.

---

## §2 Case-law tracker (as of 2026-05)

### §2.1 Andersen v. Stability AI Ltd., 3:23-cv-00201 (N.D. Cal.)

- **Docket:** https://www.courtlistener.com/docket/66732129/andersen-v-stability-ai-ltd/
- **Status (Oct 2025 status report):** https://chatgptiseatingtheworld.com/wp-content/uploads/2025/10/Andersen-v-Stability-AI-Status-Report-Oct-16-2025.pdf — case in **active discovery**, parties negotiating ESI custodian and search terms.
- **Rulings to date:**
  - Oct 2023: most claims dismissed for the original complaint; direct copyright infringement allowed to proceed.
  - Aug 12, 2024: DMCA §1202 claims dismissed with prejudice.
  - Feb 2026: third amended complaint filed.
- **No class certification ruling yet.** No summary-judgment ruling on the core "is training fair use" question.
- **Implication for Phoenix:** the legal question Phoenix cares about — whether outputs from a model trained on copyrighted images are themselves infringing — **remains undecided in the US**. The operator's E1=conservative default (no synthetic reference in shipped product) is the legally correct posture pending Andersen merits ruling.

### §2.2 Getty Images v. Stability AI Ltd. [2025] EWHC 2783 (Ch) (UK High Court)

- **Judgment:** 4 November 2025. Stability AI prevailed on the remaining secondary copyright claim. Getty had abandoned its primary copyright claims mid-trial.
- **Summary sources:**
  - https://www.lw.com/en/insights/getty-images-v-stability-ai-english-high-court-rejects-secondary-copyright-claim
  - https://www.twobirds.com/en/insights/2025/uk/stability-ai-defeats-getty-images-copyright-claims-in-first-of-its-kind-dispute-before-the-high-cour
  - https://www.pinsentmasons.com/out-law/news/gettys-copyright-case-against-stability-ai-fails
  - https://www.brownejacobson.com/insights/getty-images-stability-ai-judgment-uk-copyright-law-analysis
- **Trademark side:** "extremely limited" infringement findings under TMA s.10(1) and s.10(2) for early Stable Diffusion versions reproducing Getty watermarks; s.10(3) claim dismissed.
- **Key fact-finding:** the court **found Getty's copyright works WERE used to train Stable Diffusion**, but that the training and storage occurred outside the UK (so UK secondary infringement didn't lie). **This is a jurisdictional ruling, not a substantive endorsement of training-as-fair-use.** US plaintiffs in Andersen are not bound by it.
- **Implication for Phoenix:** UK outcome reduces UK-side risk for shippers that use Stability-trained models. Does not change US-side risk profile.

### §2.3 Authors Guild v. OpenAI, 1:23-cv-08292 (S.D.N.Y.)

- **Docket:** https://www.courtlistener.com/docket/67810584/authors-guild-v-openai-inc/
- **Status (late 2025):** Judge Sidney Stein **denied OpenAI's motion to dismiss** the substantial-similarity claims in Oct 2025 — Stein found ChatGPT-generated summaries of Game of Thrones could plausibly be "substantially similar" to Martin's original. Discovery ongoing; OpenAI ordered to produce 20M ChatGPT logs.
- **Source synthesis:**
  - https://www.publishersweekly.com/pw/by-topic/digital/copyright/article/98961-authors-class-action-lawsuit-against-openai-moves-forward.html
  - https://bannerwitcoff.com/ip-alert-authors-copyright-battle-against-openai-survives-motion-to-dismiss/
- **Relevance to image-gen:** the substantial-similarity standard the court is applying is the same one image-gen plaintiffs will press in Andersen. **The Authors Guild ruling is a leading indicator that US courts are willing to let "output substantially similar to training input" claims proceed past MTD.** This tightens the case for Phoenix's conservative default.

---

## §3 Phoenix's risk profile

| Use case | Operator default | Legal floor | Recommendation |
|---|---|---|---|
| **Synthetic reference, INTERNAL-ONLY** (QA gates, drift detection, internal cookbook QA) | OK | No public distribution → no §106 distribution claim. Training-data-derivative theory still hypothetically reachable but no plaintiff has established standing for purely internal use. | **PROCEED with internal use.** Document the gate boundary in `config/manga/character_design_template.yaml` and any LoRA training spec. |
| **Synthetic reference, EMBEDDED IN SHIPPED PRODUCT** | NOT OK | Andersen unresolved; Authors Guild substantial-similarity test surviving MTD; Getty UK is a jurisdictional carve-out that doesn't transfer to US. | **HOLD pending Andersen merits ruling.** Sub-question "Phoenix Omega's specific risk profile" is an operator-side legal-review call regardless. Mark `thin-answer-with-legal-review`. |
| **Synthetic reference using a Phoenix-OWNED LoRA trained on Manga109-s + PD anchors** | OK for internal | Manga109-s clause (5) explicitly authorises this. | OK. |
| **Synthetic reference using a third-party model whose training set includes copyrighted manga** (e.g., FLUX-dev, SD-base) | NOT OK | Compounds the Andersen risk with the upstream-model-license risk per the audit's `license_risk_register_2026-04-29.md` (FLUX-dev / Pony / Illustrious / NoobAI all commercial-blocked). | **Already blocked by audit PR #803.** No additional action. |

---

## §4 Operationalization

### §4.1 What Phoenix may do safely today

1. **Train LoRAs** on Manga109-s + PD-only datasets (Manga109-s clause 5 covers this).
2. **Generate synthetic reference imagery** from those LoRAs and use them for:
   - QA harness pairwise face-distance computation
   - Drift-detection embeddings
   - Internal cookbook validation
   - Operator visual review at the dashboard level
3. **Ship images directly generated by the production pipeline** (i.e., the actual main_character.png catalog images that go on Stillness Press, etc.) — these are the LoRA's *intended* outputs, not "synthetic reference."

### §4.2 What Phoenix should NOT do without legal review

1. **Embed synthetic reference imagery directly in shipped product** (e.g., as decorative side-panels in the catalog dashboard, as part of marketing material, as illustrations in a published "How Phoenix's manga style works" article).
2. **Distribute the LoRA weights themselves to third parties** without verifying the upstream training-data license chain.
3. **Cite Manga109-s images in the published cookbook** (clause 8 violation risk).

### §4.3 Documentation requirements

For any LoRA Phoenix trains:
- Training corpus manifest (every input image + its license + provenance URL)
- Output classification (internal-QA-only vs production-shippable vs research-only)
- Manga109-s attribution propagation if applicable
- Periodic legal review (annually or on case-law update — Andersen ruling will trigger a review)

---

## §5 Sub-question status (per operator's stop-condition tree)

| Sub-question | Status | Action |
|---|---|---|
| Manga109 commercial-use allow/forbid text | ✅ Resolved | Cite HF mirror in production legal docs |
| Manga109 commercial license cost estimate | `deferred_followup_pr` | Operator outreach to Aizawa Lab |
| Andersen v. Stability AI 2026 status | ✅ Resolved | Re-check at next Andersen ruling |
| Getty v. Stability AI UK 2025 status | ✅ Resolved | UK posture stable; US posture unaffected |
| Authors Guild v. OpenAI status | ✅ Resolved | MTD survived; substantial-similarity standard applies |
| Phoenix Omega's specific risk profile | `thin-answer-with-legal-review` | Operator-side legal review required for any synthetic-EMBEDDED decision |

---

## §6 NEXT_ACTION (post this PR)

1. Operator legal review of §3 risk-profile table; confirm or override per-row defaults.
2. Operator outreach to Aizawa Lab re. Manga109 22-volume non-s tier.
3. Cache the Manga109-s license text to `artifacts/research/manga109_s_license_text_2026-05-02.md` (archival).
4. Set up periodic Andersen / Authors Guild / Getty docket-watch (quarterly). Re-trigger this position paper on any merits ruling.
5. Document training-corpus manifest schema for any LoRA Phoenix trains (separate engineering PR; references this position paper as the legal-grounding document).

---

*End of synthetic_reference_legal_position_2026-05-03.md. This document is research, not legal advice.*
