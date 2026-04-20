# Manga Visual Quality Gates Specification
## AI Manga Dharma System — SpiritualTech Systems

**Version:** 1.0
**Status:** Design
**Workstream:** 7
**Date:** 2026-04-17
**Gate IDs:** MQG-01 through MQG-08

---

## 1. PURPOSE & SCOPE

Phoenix Omega's prose quality gates (MDLG-01 through MDLG-05) validate text-domain properties: length, semantic density, formatting, tone. They cannot evaluate visual properties.

The MQG gates defined here validate manga-specific visual properties: panel size rhythm, silence distribution, establishing shot cadence, reading flow, emotional arc, page-turn structure, character presence, and dialogue bubble density. These gates operate on the **layout and script layers**, not on rendered pixels. They can therefore run before FLUX is invoked (at Name Stage) and again after lettering (post-composition).

**When MQG gates run:**

| Gate | Run at Name Stage | Run at QC Stage |
|------|:-----------------:|:---------------:|
| MQG-01 Visual Rhythm | yes | yes |
| MQG-02 Silence Density | yes | yes |
| MQG-03 Establishing Shot Cadence | yes | yes |
| MQG-04 Reading Flow | yes | yes |
| MQG-05 Emotional Arc Progression | yes | — |
| MQG-06 Page-Turn Payoff | yes | — |
| MQG-07 Character Presence Density | yes | — |
| MQG-08 Dialogue Bubble Count | yes | yes |

Gates marked "yes" at Name Stage run against `page_layout_spec.json` *before* FLUX. This is the cheapest point to catch structural violations.

---

## 2. DATA SOURCES

All eight gates read from a defined set of upstream files. No gate reads rendered pixel data.

| Source file | How it is used |
|-------------|---------------|
| `page_layout_spec.json` | Primary: panel size classes, positions, bubble zones, emotional roles, page types, chapter_stats |
| `chapter_script_writer_handoff.json` | Dialogue arrays (bubble count ground truth), panel_type, silence_guard, page_type |
| `lettering_spec.json` | Actual rendered bubble count post-lettering (MQG-08 post-composition run) |

No gate requires rendered panel images. The gates are **structural validators**, not aesthetic scorers.

---

## 3. GATE: MQG-01 — VISUAL RHYTHM

**Purpose:** Verify that each page has deliberate panel size variety, not uniform tiling.

### 3.1 What It Checks

On each page: how many distinct `size_class` values appear among that page's panels.

Uniform grids (all panels the same size) produce visual monotony. Iyashikei especially requires rhythm between large environmental panels and smaller reactive panels.

### 3.2 Computation

```python
def mqg_01_visual_rhythm(page_layout_spec: dict) -> GateResult:
    violations = []

    for page in page_layout_spec["pages"]:
        if len(page["panels"]) == 1:
            continue  # single-panel pages (splash/full_page) are inherently rhythmic; skip

        size_classes = [p["size_class"] for p in page["panels"]]
        distinct_count = len(set(size_classes))

        if distinct_count < 2:
            violations.append({
                "page_number": page["page_number"],
                "issue": "all panels same size_class",
                "size_classes": size_classes,
                "distinct_count": distinct_count
            })

    # Iyashikei additional check: at least one large-or-bigger panel per page
    if page_layout_spec.get("genre") == "iyashikei":
        LARGE_OR_BIGGER = {"full_page", "splash", "large"}
        for page in page_layout_spec["pages"]:
            if len(page["panels"]) == 1:
                continue
            has_large = any(p["size_class"] in LARGE_OR_BIGGER for p in page["panels"])
            if not has_large:
                violations.append({
                    "page_number": page["page_number"],
                    "issue": "iyashikei requires at least one large/splash/full_page panel per page"
                })

    return build_result("MQG-01", violations)
```

### 3.3 Thresholds

| condition | verdict |
|-----------|---------|
| Distinct size classes per page >= 2 | PASS |
| Distinct size classes = 1 on any multi-panel page | FAIL |
| Iyashikei: no large-or-bigger panel on a multi-panel page | FAIL |

### 3.4 Fail Action

- **At Name Stage:** Regenerate the offending pages using `vary_sizes(candidate, variation="expand")` to introduce size hierarchy. Block FLUX.
- **At QC Stage:** Flag for editorial review. Do not block publish if Name Stage passed; this indicates a regression introduced after approval.

---

## 4. GATE: MQG-02 — SILENCE DENSITY

**Purpose:** Verify that the chapter's ratio of silent panels (zero dialogue/SFX/caption) is within genre-appropriate bounds.

### 4.1 What It Checks

Percentage of all panels with zero `bubble_zones` (from `page_layout_spec.json`) and zero dialogue/sfx entries (from `chapter_script_writer_handoff.json`).

### 4.2 Computation

```python
def mqg_02_silence_density(page_layout_spec: dict, chapter_script: dict) -> GateResult:
    genre = page_layout_spec["genre"]
    stats = page_layout_spec["chapter_stats"]

    silent_pct = stats["silent_panel_pct"]
    thresholds = SILENCE_THRESHOLDS[genre]

    if silent_pct < thresholds["fail_below"]:
        verdict = "FAIL"
        message = f"{silent_pct:.0%} silent panels — below minimum {thresholds['fail_below']:.0%} for {genre}"
    elif silent_pct < thresholds["warn_below"]:
        verdict = "WARN"
        message = f"{silent_pct:.0%} silent panels — below recommended {thresholds['warn_below']:.0%} for {genre}"
    elif silent_pct > thresholds["warn_above"]:
        verdict = "WARN"
        message = f"{silent_pct:.0%} silent panels — above recommended {thresholds['warn_above']:.0%} for {genre}"
    elif silent_pct > thresholds["fail_above"]:
        verdict = "FAIL"
        message = f"{silent_pct:.0%} silent panels — above maximum {thresholds['fail_above']:.0%} for {genre}"
    else:
        verdict = "PASS"
        message = f"{silent_pct:.0%} silent panels — within target range"

    return GateResult("MQG-02", verdict, message, {"silent_pct": silent_pct})
```

### 4.3 Thresholds by Genre

```python
SILENCE_THRESHOLDS = {
    "iyashikei": {
        "fail_below": 0.20,   # <20% = overcrowded, wrong for genre
        "warn_below": 0.40,   # 20-40% = below ideal
        "target_low":  0.40,  # ideal range: 40-70%
        "target_high": 0.70,
        "warn_above":  0.70,  # 70-85% = potentially too sparse
        "fail_above":  0.85   # >85% = almost no content (structural error)
    },
    "slice_of_life": {
        "fail_below": 0.20,
        "warn_below": 0.35,
        "target_low":  0.35,
        "target_high": 0.65,
        "warn_above":  0.65,
        "fail_above":  0.80
    },
    "shonen": {
        "fail_below": 0.20,   # shared universal minimum: ALL genres
        "warn_below": 0.20,
        "target_low":  0.20,
        "target_high": 0.40,
        "warn_above":  0.40,
        "fail_above":  0.65
    },
    "horror": {
        "fail_below": 0.20,
        "warn_below": 0.50,
        "target_low":  0.50,
        "target_high": 0.80,
        "warn_above":  0.80,
        "fail_above":  0.90
    },
    "psychological": {
        "fail_below": 0.20,
        "warn_below": 0.40,
        "target_low":  0.40,
        "target_high": 0.75,
        "warn_above":  0.75,
        "fail_above":  0.90
    },
    "drama": {
        "fail_below": 0.20,
        "warn_below": 0.30,
        "target_low":  0.30,
        "target_high": 0.60,
        "warn_above":  0.60,
        "fail_above":  0.80
    }
}
# All genres not listed default to shonen thresholds.
# Universal minimum: fail_below = 0.20 for ALL genres (overcrowded text is always wrong).
```

**Key invariant:** `fail_below = 0.20` for ALL genres. A chapter where more than 80% of panels have dialogue is overcrowded by any genre standard.

### 4.4 Fail Action

- **FAIL (below minimum):** Chapter has too much text. Regenerate Name Stage with higher `emotional_role: "breath"` density. Block FLUX.
- **FAIL (above maximum):** Structural error — chapter is nearly content-free. Check chapter_script for missing dialogue. Block FLUX.
- **WARN:** Log warning. Human editorial review recommended. Do not block FLUX.

---

## 5. GATE: MQG-03 — ESTABLISHING SHOT CADENCE

**Purpose:** Verify that the reader is periodically re-grounded in environment/setting, preventing a chapter that is all close-ups.

### 5.1 What It Checks

Does at least one establishing shot (panel with `emotional_role: "establishing"` or `size_class` in `{full_page, splash, large}` and `subject == "environment"`) appear every N pages?

Iyashikei: N = 4. Setting IS character in this genre; environmental panels are especially critical.

Default (all genres): N = 6.

### 5.2 Computation

```python
def mqg_03_establishing_shot_cadence(
    page_layout_spec: dict,
    chapter_script: dict,
) -> GateResult:
    genre = page_layout_spec["genre"]
    max_gap = 4 if genre == "iyashikei" else 6

    # Collect pages that contain an establishing shot
    establishing_pages = set()
    for page in page_layout_spec["pages"]:
        for panel in page["panels"]:
            if panel["emotional_role"] == "establishing":
                establishing_pages.add(page["page_number"])
                break
            # Also qualify: large+ panel showing environment
            if (panel["size_class"] in {"full_page", "splash", "large"}
                    and panel.get("bubble_zones") == []):
                establishing_pages.add(page["page_number"])
                break

    # Find gaps between establishing shots
    total_pages = page_layout_spec["target_page_count"]
    violations = []
    last_establishing = 0

    for pn in range(1, total_pages + 1):
        if pn in establishing_pages:
            gap = pn - last_establishing - 1
            last_establishing = pn
        else:
            gap = pn - last_establishing

        if gap > max_gap:
            violations.append({
                "page_range": f"{last_establishing + 1}–{pn}",
                "gap_pages": gap,
                "max_allowed": max_gap
            })

    # Deduplicate overlapping violation ranges
    violations = deduplicate_violations(violations)

    return build_result("MQG-03", violations)
```

### 5.3 Thresholds

| genre | max pages between establishing shots | fail condition |
|-------|--------------------------------------|----------------|
| `iyashikei` | 4 | gap > 4 pages |
| all others | 6 | gap > 6 pages |

### 5.4 Fail Action

- **At Name Stage:** Insert `emotional_role: "establishing"` panel into the gap region. Reduce an existing `small` or `reaction` panel to `gutter` to make space. Regenerate affected pages.
- **At QC Stage:** Flag for editorial. Do not block publish unless gap > 2× max (e.g., gap > 8 for iyashikei).

---

## 6. GATE: MQG-04 — READING FLOW

**Purpose:** Verify that panel positions decode to an unambiguous, coherent reading path.

### 6.1 What It Checks

For each page: do the `reading_order` values form a valid sequence given the panel grid positions and `reading_direction`?

**LTR validation:** Panels in reading order must progress generally left-to-right, then top-to-bottom. Formally: for consecutive panels A (order N) and B (order N+1):
- If A and B are on the same row: B.col > A.col (B is to the right of A)
- If B is on a lower row than A: always valid (row break = natural LTR step)
- Ambiguous: two panels at the same row AND same column start (e.g., identical top-left corner) — this is a grid overlap error

**RTL validation:** Same as LTR but direction reversed: B.col < A.col on same row.

### 6.2 Computation

```python
def mqg_04_reading_flow(page_layout_spec: dict) -> GateResult:
    direction = page_layout_spec["reading_direction"]
    violations = []

    for page in page_layout_spec["pages"]:
        panels = sorted(page["panels"], key=lambda p: p["reading_order"])

        for i in range(len(panels) - 1):
            a = panels[i]["position"]
            b = panels[i + 1]["position"]

            # Overlap check: no two panels should share the same grid cell
            a_rows = set(range(a["row"], a["row"] + a["row_span"]))
            a_cols = set(range(a["col"], a["col"] + a["col_span"]))
            b_rows = set(range(b["row"], b["row"] + b["row_span"]))
            b_cols = set(range(b["col"], b["col"] + b["col_span"]))

            if a_rows & b_rows and a_cols & b_cols:
                violations.append({
                    "page": page["page_number"],
                    "issue": "OVERLAP",
                    "panels": [panels[i]["panel_id"], panels[i+1]["panel_id"]],
                    "detail": "panels occupy overlapping grid cells"
                })
                continue

            # Same-row directionality check
            a_top_row = a["row"]
            b_top_row = b["row"]

            if a_top_row == b_top_row:
                if direction == "ltr" and b["col"] < a["col"]:
                    violations.append({
                        "page": page["page_number"],
                        "issue": "FLOW_REVERSAL",
                        "panels": [panels[i]["panel_id"], panels[i+1]["panel_id"]],
                        "detail": f"LTR: panel {panels[i+1]['panel_id']} is left of {panels[i]['panel_id']} on same row"
                    })
                elif direction == "rtl" and b["col"] > a["col"]:
                    violations.append({
                        "page": page["page_number"],
                        "issue": "FLOW_REVERSAL",
                        "panels": [panels[i]["panel_id"], panels[i+1]["panel_id"]],
                        "detail": f"RTL: panel {panels[i+1]['panel_id']} is right of {panels[i]['panel_id']} on same row"
                    })

    return build_result("MQG-04", violations)
```

### 6.3 Thresholds

| condition | verdict |
|-----------|---------|
| Zero violations | PASS |
| Any OVERLAP error | FAIL (grid layout is broken) |
| Any FLOW_REVERSAL on same row | FAIL (reading direction violated) |

### 6.4 Fail Action

- **FAIL:** The Name Stage grid assignment algorithm produced an invalid layout. This is a code error, not an editorial issue. Regenerate the page layout. Block FLUX.
- If FLOW_REVERSAL persists after regeneration: escalate to engineering. Do not proceed.

---

## 7. GATE: MQG-05 — EMOTIONAL ARC PROGRESSION

**Purpose:** Verify that the sequence of `emotional_role` values across the chapter follows genre-appropriate arc conventions.

### 7.1 What It Checks

The chapter's `chapter_stats.emotional_role_sequence` is a flat ordered list of all panel emotional roles in reading order. This gate checks whether the arc shape matches the genre pattern.

### 7.2 Genre Patterns

**Iyashikei arc pattern:**
- Chapter must OPEN with `establishing` or `breath` in first 3 panels
- Chapter must CLOSE with `breath` or `silence` in last 3 panels
- Chapter must NOT open with `action` as the first panel
- Chapter must NOT close with `action` or `revelation` as the last panel (unresolved tension)
- Middle third of panels (by index): may contain `intimate_dialogue`, `action`, `reaction` freely

**Default arc pattern (all other genres):**
- Chapter must have at least one `establishing` in first 10% of panels
- No constraint on closing

### 7.3 Computation

```python
def mqg_05_emotional_arc(page_layout_spec: dict) -> GateResult:
    genre = page_layout_spec["genre"]
    sequence = page_layout_spec["chapter_stats"].get("emotional_role_sequence", [])

    if not sequence:
        return GateResult("MQG-05", "WARN", "emotional_role_sequence not computed; skipping arc check", {})

    n = len(sequence)
    violations = []

    if genre == "iyashikei":
        # Opening check: first 3 panels
        opening = sequence[:3]
        if not any(r in {"establishing", "breath"} for r in opening):
            violations.append({
                "check": "opening",
                "issue": "iyashikei must open with establishing or breath in first 3 panels",
                "actual": opening
            })

        if sequence[0] == "action":
            violations.append({
                "check": "opening_action",
                "issue": "iyashikei chapter must not open with action panel",
                "actual": sequence[0]
            })

        # Closing check: last 3 panels
        closing = sequence[-3:]
        if not any(r in {"breath", "silence"} for r in closing):
            violations.append({
                "check": "closing",
                "issue": "iyashikei must close with breath or silence in last 3 panels",
                "actual": closing
            })

        if sequence[-1] in {"action", "revelation"}:
            violations.append({
                "check": "closing_unresolved",
                "issue": f"iyashikei chapter must not end on '{sequence[-1]}' — leaves reader in unresolved tension",
                "actual": sequence[-1]
            })

    else:
        # Generic: has establishing in first 10%
        opening_window = sequence[:max(1, n // 10)]
        if "establishing" not in opening_window:
            violations.append({
                "check": "opening_establishing",
                "issue": f"no establishing shot in first {max(1, n//10)} panels",
                "actual": opening_window
            })

    return build_result("MQG-05", violations)
```

### 7.4 Thresholds

| condition | verdict |
|-----------|---------|
| All arc checks pass | PASS |
| Any arc violation | FAIL |

### 7.5 Fail Action

- **At Name Stage:** Re-run layout candidate selection, passing the arc constraint as a hard requirement to the LLM selection prompt. Alternatively, swap the first panel's emotional_role to `establishing` and re-assign its size_class to `large`.
- Block FLUX if iyashikei arc fails.

---

## 8. GATE: MQG-06 — PAGE-TURN PAYOFF

**Purpose:** Verify that right-hand pages (odd-numbered pages in LTR reading; even-numbered in RTL) carry higher visual weight, rewarding the reader's page-turn action.

### 8.1 What It Checks

For LTR reading: odd-numbered pages are right-hand pages (visible when reader opens a spread). These pages should disproportionately carry the narrative's high-impact moments.

At least 30% of odd-numbered pages must have `page_turn_payoff: true`.

For RTL reading: even-numbered pages are right-hand pages; same 30% threshold applies.

For webtoon: gate is skipped (no page-turn concept).

### 8.2 Computation

```python
def mqg_06_page_turn_payoff(page_layout_spec: dict) -> GateResult:
    direction = page_layout_spec["reading_direction"]

    if direction == "webtoon":
        return GateResult("MQG-06", "SKIP", "webtoon format — no page-turn concept", {})

    pages = page_layout_spec["pages"]
    stats = page_layout_spec["chapter_stats"]

    # Identify right-hand pages
    if direction == "ltr":
        right_hand = [p for p in pages if p["page_number"] % 2 == 1]
    else:  # rtl
        right_hand = [p for p in pages if p["page_number"] % 2 == 0]

    if not right_hand:
        return GateResult("MQG-06", "SKIP", "no right-hand pages found", {})

    payoff_count = sum(1 for p in right_hand if p["page_turn_payoff"])
    payoff_pct = payoff_count / len(right_hand)

    MIN_PAYOFF_PCT = 0.30

    if payoff_pct < MIN_PAYOFF_PCT:
        verdict = "FAIL"
        message = (
            f"Only {payoff_pct:.0%} of right-hand pages have page_turn_payoff=true "
            f"({payoff_count}/{len(right_hand)}). Minimum: {MIN_PAYOFF_PCT:.0%}."
        )
    else:
        verdict = "PASS"
        message = f"{payoff_pct:.0%} of right-hand pages are page-turn payoffs ({payoff_count}/{len(right_hand)})"

    return GateResult("MQG-06", verdict, message, {
        "payoff_pct": payoff_pct,
        "payoff_count": payoff_count,
        "right_hand_page_count": len(right_hand)
    })
```

### 8.3 Thresholds

| condition | verdict |
|-----------|---------|
| `page_turn_payoff_odd_page_pct` >= 30% | PASS |
| 20–29% | WARN |
| < 20% | FAIL |
| webtoon format | SKIP |

### 8.4 Fail Action

- **At Name Stage:** Identify odd pages with high visual impact panels (`size_class: full_page` or `splash`, or `emotional_role: revelation`) and promote their `page_turn_payoff` flag to `true`. If no high-impact candidates exist, consider swapping a `revelation` panel to an odd page.
- WARN: Log. Do not block FLUX.
- FAIL: Flag for editorial. Do not block FLUX (this is a structural preference, not a structural error).

---

## 9. GATE: MQG-07 — CHARACTER PRESENCE DENSITY

**Purpose:** Verify that the protagonist appears frequently enough to maintain reader identification, without exceeding genre-specific upper bounds.

### 9.1 What It Checks

Of all pages in the chapter, on what percentage does the protagonist appear in at least one panel? And are there stretches of 3+ consecutive pages with no protagonist?

`protagonist_present` is set on `PanelLayout` objects (see `manga_page_layout_spec_schema.json`). It is null when not computed; the gate treats null as "unknown" and issues a WARN rather than FAIL.

### 9.2 Computation

```python
def mqg_07_character_presence(page_layout_spec: dict) -> GateResult:
    genre = page_layout_spec["genre"]
    pages = page_layout_spec["pages"]
    stats = page_layout_spec["chapter_stats"]

    # Check if protagonist_present was computed
    protagonist_page_count = stats.get("protagonist_page_count")
    if protagonist_page_count is None:
        return GateResult("MQG-07", "WARN",
            "protagonist_present not computed in panel layouts; skipping presence check", {})

    total_pages = len(pages)
    presence_pct = protagonist_page_count / total_pages
    thresholds = PROTAGONIST_THRESHOLDS.get(genre, PROTAGONIST_THRESHOLDS["default"])

    violations = []

    # Presence percentage check
    if presence_pct < thresholds["fail_below"]:
        violations.append({
            "check": "presence_pct",
            "issue": f"protagonist present on only {presence_pct:.0%} of pages — below {thresholds['fail_below']:.0%} minimum for {genre}",
            "value": presence_pct
        })
    elif presence_pct > thresholds["fail_above"]:
        violations.append({
            "check": "presence_pct_high",
            "issue": f"protagonist present on {presence_pct:.0%} of pages — above {thresholds['fail_above']:.0%} maximum (claustrophobic POV)",
            "value": presence_pct
        })

    # Consecutive absence check
    MAX_CONSECUTIVE_ABSENT = 3
    consecutive_absent = 0
    for page in pages:
        has_protagonist = any(p.get("protagonist_present") for p in page["panels"])
        if not has_protagonist:
            consecutive_absent += 1
            if consecutive_absent > MAX_CONSECUTIVE_ABSENT:
                violations.append({
                    "check": "consecutive_absent",
                    "issue": f"protagonist absent for {consecutive_absent}+ consecutive pages starting around page {page['page_number'] - consecutive_absent + 1}",
                    "page": page["page_number"]
                })
        else:
            consecutive_absent = 0

    return build_result("MQG-07", violations)


PROTAGONIST_THRESHOLDS = {
    "iyashikei": {
        "fail_below": 0.60,   # protagonist must anchor 60%+ of pages
        "warn_below": 0.70,
        "target_low":  0.70,  # ideal: 70–90%
        "target_high": 0.90,
        "warn_above":  0.90,
        "fail_above":  1.00   # 100% = no environment-only pages (structural error for iyashikei)
    },
    "shonen": {
        "fail_below": 0.50,
        "warn_below": 0.60,
        "target_low":  0.60,
        "target_high": 0.95,
        "warn_above":  0.95,
        "fail_above":  1.01   # shonen can be protagonist-only; no upper fail
    },
    "default": {
        "fail_below": 0.40,
        "warn_below": 0.50,
        "target_low":  0.50,
        "target_high": 0.95,
        "warn_above":  0.95,
        "fail_above":  1.01
    }
}
```

### 9.3 Thresholds

| genre | protagonist presence range (fail) | max consecutive absent pages |
|-------|----------------------------------|------------------------------|
| `iyashikei` | 60–100% (100% fails — needs environment pages) | 3 |
| `shonen` | 50%+ | 3 |
| default | 40%+ | 3 |

### 9.4 Fail Action

- **FAIL (too low):** Protagonist is absent from too many pages. Editorial review. Do not block FLUX, but flag for Name Stage revision.
- **FAIL (iyashikei: 100%):** No environment-only pages — violates the genre's core "setting is character" principle. Add breath panels with `subject: "environment"`.
- **Consecutive absence > 3:** Flag for editorial. Reader loses protagonist anchor. Consider restructuring affected pages.

---

## 10. GATE: MQG-08 — DIALOGUE BUBBLE COUNT

**Purpose:** Verify that average dialogue bubble density per page is within genre-appropriate limits.

### 10.1 What It Checks

Average speech bubbles per page across the chapter. Computed from `bubble_zones` of type `speech`, `thought`, `whisper`, `shout` (not `narration`, `sfx`, `caption`).

This gate runs twice:
1. At Name Stage: against `page_layout_spec.json` bubble_zones (planned density)
2. At QC Stage: against `lettering_spec.json` actual rendered bubbles (confirmed density)

### 10.2 Computation

```python
def mqg_08_bubble_count(
    page_layout_spec: dict,
    lettering_spec: dict | None = None,  # None = Name Stage run
) -> GateResult:
    genre = page_layout_spec["genre"]
    thresholds = BUBBLE_COUNT_THRESHOLDS.get(genre, BUBBLE_COUNT_THRESHOLDS["default"])

    if lettering_spec is not None:
        # Post-composition: count from lettering_spec.json
        total_bubbles = sum(
            1 for panel in lettering_spec.get("panels", [])
            for element in panel.get("lettering_elements", [])
            if element["type"] in {"speech_bubble", "thought_bubble", "whisper", "shout"}
        )
        total_pages = len(page_layout_spec["pages"])
        source = "lettering_spec"
    else:
        # Name Stage: count from page_layout_spec bubble_zones
        DIALOGUE_TYPES = {"speech", "thought", "whisper", "shout"}
        total_bubbles = sum(
            1 for page in page_layout_spec["pages"]
            for panel in page["panels"]
            for zone in panel["bubble_zones"]
            if zone["type"] in DIALOGUE_TYPES
        )
        total_pages = len(page_layout_spec["pages"])
        source = "page_layout_spec"

    avg_bubbles_per_page = total_bubbles / total_pages if total_pages > 0 else 0

    if avg_bubbles_per_page > thresholds["fail_above"]:
        verdict = "FAIL"
        message = (
            f"avg {avg_bubbles_per_page:.1f} speech bubbles/page exceeds maximum "
            f"{thresholds['fail_above']} for {genre} (source: {source})"
        )
    elif avg_bubbles_per_page > thresholds["warn_above"]:
        verdict = "WARN"
        message = f"avg {avg_bubbles_per_page:.1f} speech bubbles/page — above recommended {thresholds['warn_above']} for {genre}"
    else:
        verdict = "PASS"
        message = f"avg {avg_bubbles_per_page:.1f} speech bubbles/page — within target for {genre}"

    return GateResult("MQG-08", verdict, message, {
        "avg_bubbles_per_page": avg_bubbles_per_page,
        "total_bubbles": total_bubbles,
        "total_pages": total_pages,
        "source": source
    })


BUBBLE_COUNT_THRESHOLDS = {
    "iyashikei": {
        "target_range": (0, 3),
        "warn_above": 3,
        "fail_above": 5
    },
    "slice_of_life": {
        "target_range": (1, 4),
        "warn_above": 5,
        "fail_above": 7
    },
    "shonen": {
        "target_range": (2, 6),
        "warn_above": 7,
        "fail_above": 10
    },
    "drama": {
        "target_range": (1, 5),
        "warn_above": 6,
        "fail_above": 9
    },
    "psychological": {
        "target_range": (0, 4),
        "warn_above": 5,
        "fail_above": 8
    },
    "default": {
        "target_range": (1, 5),
        "warn_above": 6,
        "fail_above": 10
    }
}
```

### 10.3 Thresholds

| genre | target range (avg/page) | warn above | fail above |
|-------|------------------------|------------|-----------|
| `iyashikei` | 0–3 | >3 | >5 |
| `slice_of_life` | 1–4 | >5 | >7 |
| `shonen` | 2–6 | >7 | >10 |
| `drama` | 1–5 | >6 | >9 |
| `psychological` | 0–4 | >5 | >8 |
| default | 1–5 | >6 | >10 |

### 10.4 Fail Action

- **FAIL (iyashikei: avg > 5 bubbles/page):** Chapter is too text-dense for the genre. Regenerate Name Stage with reduced bubble zone allocations. Remove dialogue lines from middle pages. Block FLUX.
- **WARN:** Log. Do not block FLUX. Surface to editorial.
- **Post-composition FAIL:** The Lettering Agent produced more bubbles than the Name Stage planned. Check for script dialogue that was added between stages. Flag for QC review.

---

## 11. GATE RUNNER & OUTPUT

### 11.1 Runner Function

```python
def run_mqg_gates(
    page_layout_spec: dict,
    chapter_script: dict,
    lettering_spec: dict | None = None,
    run_at: str = "name_stage",  # "name_stage" | "qc_stage"
) -> MQGReport:
    """
    Run all applicable MQG gates and return a composite report.

    At name_stage: runs MQG-01 through MQG-08 against page_layout_spec.
    At qc_stage: re-runs MQG-01, MQG-02, MQG-03, MQG-04, MQG-08 with
                 lettering_spec as additional input for MQG-08.
    """
    gates = [
        mqg_01_visual_rhythm(page_layout_spec),
        mqg_02_silence_density(page_layout_spec, chapter_script),
        mqg_03_establishing_shot_cadence(page_layout_spec, chapter_script),
        mqg_04_reading_flow(page_layout_spec),
    ]

    if run_at == "name_stage":
        gates += [
            mqg_05_emotional_arc(page_layout_spec),
            mqg_06_page_turn_payoff(page_layout_spec),
            mqg_07_character_presence(page_layout_spec),
            mqg_08_bubble_count(page_layout_spec),
        ]
    else:  # qc_stage
        gates += [
            mqg_08_bubble_count(page_layout_spec, lettering_spec),
        ]

    return MQGReport(
        chapter_id=page_layout_spec["chapter_id"],
        run_at=run_at,
        overall_verdict=aggregate_verdict(gates),
        gates=gates,
        timestamp=utcnow(),
    )
```

### 11.2 Aggregate Verdict

```
BLOCKED  → one or more FAIL results
APPROVED → all PASS or SKIP (zero FAIL, zero WARN)
APPROVED_WITH_WARNINGS → all PASS or SKIP except one or more WARN
```

### 11.3 Report Output Format

```json
{
  "chapter_id": "ch_01",
  "run_at": "name_stage",
  "overall_verdict": "APPROVED_WITH_WARNINGS",
  "timestamp": "2026-04-17T10:00:00Z",
  "gates": [
    {
      "gate_id": "MQG-01",
      "name": "Visual Rhythm",
      "verdict": "PASS",
      "message": "All pages have >= 2 distinct size classes",
      "data": {}
    },
    {
      "gate_id": "MQG-02",
      "name": "Silence Density",
      "verdict": "PASS",
      "message": "41% silent panels — within iyashikei target range (40-70%)",
      "data": { "silent_pct": 0.41 }
    },
    {
      "gate_id": "MQG-03",
      "name": "Establishing Shot Cadence",
      "verdict": "PASS",
      "message": "No gaps > 4 pages without establishing shot",
      "data": {}
    },
    {
      "gate_id": "MQG-04",
      "name": "Reading Flow",
      "verdict": "PASS",
      "message": "No flow reversals or panel overlaps detected",
      "data": {}
    },
    {
      "gate_id": "MQG-05",
      "name": "Emotional Arc Progression",
      "verdict": "PASS",
      "message": "Iyashikei arc: opens with establishing, closes with breath",
      "data": {}
    },
    {
      "gate_id": "MQG-06",
      "name": "Page-Turn Payoff",
      "verdict": "WARN",
      "message": "25% of right-hand pages are page-turn payoffs (3/12). Minimum: 30%.",
      "data": { "payoff_pct": 0.25, "payoff_count": 3, "right_hand_page_count": 12 }
    },
    {
      "gate_id": "MQG-07",
      "name": "Character Presence Density",
      "verdict": "PASS",
      "message": "Protagonist present on 75% of pages — within iyashikei target range (70-90%)",
      "data": { "presence_pct": 0.75 }
    },
    {
      "gate_id": "MQG-08",
      "name": "Dialogue Bubble Count",
      "verdict": "PASS",
      "message": "avg 1.8 speech bubbles/page — within iyashikei target (0-3)",
      "data": { "avg_bubbles_per_page": 1.8, "total_bubbles": 43, "total_pages": 24, "source": "page_layout_spec" }
    }
  ]
}
```

### 11.4 Action Table

| overall_verdict | Can proceed to FLUX? | Can proceed to publish? |
|----------------|----------------------|------------------------|
| `APPROVED` | yes | yes |
| `APPROVED_WITH_WARNINGS` | yes | yes (log warnings) |
| `BLOCKED` | no — fix and re-run Name Stage | no |

---

## 12. RELATIONSHIP TO EXISTING GATES

The MQG gates extend but do not replace the existing quality gate architecture:

| existing gate | domain | replaced by MQG? |
|--------------|--------|-----------------|
| MDLG-01 through MDLG-05 | prose/text quality | no — parallel track |
| Layout Agent Gate 1 (reading flow) | panel sequence order | MQG-04 provides earlier version of same check |
| Layout Agent Gate 3 (contrast) | pixel-level legibility | not replaced — runs on rendered output |
| Layout Agent Gate 8 (silence purity) | panel-level text presence | MQG-02 runs earlier at Name Stage |
| Production Pipeline QC level_2 (silence weight) | chapter-level silence % | MQG-02 is the authoritative gate; pipeline QC defers to it |

**Interaction with the Layout Agent Spec** (`MANGA_LAYOUT_AGENT_SPEC.md` Section 9): The Layout Agent's Gate 8 (silence purity) runs on composed pixels. MQG-02 runs earlier on structural spec. Both are required; they check different things (MQG-02: planned density vs. genre target; Layout Agent Gate 8: rendered output vs. zero-text requirement on marked panels).

---

*SpiritualTech Systems · Manga Visual Quality Gates Spec v1.0 · Confidential*
