# Wiring gate — manga_mode_vessels before → after (M4)

`check_manga_wiring.py` lives on open PR **#4607** (not yet on main). M4 does **not**
fork that file. This note records the vessels-specific flip.

## Call-reachability (this PR — verified)

| Path | Calls `load_vessel` |
|---|---|
| `phoenix_v4/manga/series/story_architect.py` → `apply_mode_vessel` | **yes** (when `mode` set) |
| `phoenix_v4/manga/chapter/writer.py` → `_mode_vessel_prompt_block` | **yes** (when `mode` set) |
| `phoenix_v4/manga/mode/vessels.py` | loader (pre-existing) |

Behavioral proof: `BEAT_DIFF_REPORT.md` — **PASS** (39 beats with vessel vs 36 without;
writer prompt gains `Mode vessel` block only when mode set).

## Gate status for `manga_mode_vessels.yaml`

| State | Result |
|---|---|
| **BEFORE** (#4607 KNOWN_UNWIRED includes vessels) | declared-unwired (honest: loader present, uncalled) |
| **AFTER** (this PR's consumers + remove vessels line from KNOWN_UNWIRED) | **wired** — stem appears in non-test consumers *and* is on a callable path |

## Unblock (one line, after #4607 merges)

```diff
-    "manga_mode_vessels.yaml":
-        "teacher/music narrative vessels; loader is test-only — roadmap M4 wires "
-        "it into story_architect + chapter-writer prompt assembly",
```

Do **not** apply that edit on the open #4607 branch from this lane (one actor per resource).
Follow-up PR or commit on main once #4607 lands: `chore(manga): drop manga_mode_vessels from KNOWN_UNWIRED (M4 wired)`.
