# gen_z_reactions atom — schema sketch

**Purpose.** When a hard_news_v2 article is assembled, the "How this news is affecting Gen Z" section needs prose that translates the news event into how it lands for 14-29-year-olds. This atom library makes that translation deterministic (not LLM-generated per article), so the voice stays consistent and the prose can be reviewed once and reused.

## Architecture decision

The library is keyed by **reaction-type**, not by **topic**.

Rationale:
- "Reaction-type" is how a generation processes news (displacement-anxiety, moral-injury, agency-loss, etc.).
- A given news story can trigger multiple reaction-types depending on its facts.
- The same reaction-type recurs across many topics (a climate event and a war can both produce displacement-anxiety).
- If we keyed by topic, we'd duplicate the same emotional content under climate/peace_conflict/economy_work entries.
- By keying on reaction-type, we get small library size × high reuse.

## Reaction-type taxonomy (v0 — 12 reactions)

Each reaction-type names a recognized psychological response Gen Z research and clinical literature identify. The taxonomy is open for expansion.

| ID | Name | When it activates |
|---|---|---|
| `displacement_anxiety` | Displacement Anxiety | News about climate events, war, housing, forced migration. Triggers fear that one's place / future is not stable. |
| `moral_injury` | Moral Injury | News exposing institutional failure to act on known harms (climate inaction, war crimes documented but not stopped, etc.). |
| `agency_loss` | Agency Loss | News showing decisions made about the cohort, without the cohort. Treaties, budgets, AI regulation drafted without youth input. |
| `future_foreclosure` | Future Foreclosure | News that narrows the runway: economic precarity, declining birthrate framing, "you may never own a home" narratives. |
| `betrayal_by_institutions` | Institutional Betrayal | News revealing institutions known to be safe-keepers (UN, governments, schools) have failed in their core role. |
| `compassion_overload` | Compassion Overload | Mass-casualty news, refugee flows, famines — the volume of need exceeds the capacity to respond. |
| `epistemic_disorientation` | Epistemic Disorientation | AI deepfakes, misinformation operations, news about news being weaponized. Erodes ability to know what's true. |
| `acceleration_dread` | Acceleration Dread | News about pace-of-change outrunning the cohort's ability to adapt: AI capability, climate tipping points, geopolitical fluxes. |
| `recognition_relief` | Recognition Relief | News confirming what the cohort has been saying. Validating but with bittersweet edge — "finally on the record." |
| `solidarity_pull` | Solidarity Pull | News about peer cohorts organizing, documenting, taking action. Activates desire to join. |
| `body_overload` | Body Overload | News whose volume itself stresses the body — too many crises, too much exposure to harm. Somatic, not cognitive. |
| `narrative_thinning` | Narrative Thinning | News that erodes the meaning-frame the cohort had been operating in: "everything I was told about adulthood no longer applies." |

## Atom file format

One YAML file per reaction-type at `pearl_news/atoms/gen_z_reactions/<reaction_id>.yaml`. Each file has 5 variations × ~50 words.

```yaml
# pearl_news/atoms/gen_z_reactions/moral_injury.yaml
schema_version: 1
reaction_id: moral_injury
display_name: "Moral Injury"
description: >
  Activates when a news story exposes institutional failure to act on a
  known harm. The cohort reads the failure as evidence the system was
  never the protector it advertised itself as.

# topics this reaction maps well to (for selection heuristic; not exclusive)
strong_topics:
  - peace_conflict
  - climate
  - partnerships
  - inequality

# 5 variations, ~50 words each, rotated deterministically by article_id.
variations:
  - id: v1
    text: >
      The shock is not that something was broken. The shock is that
      something the cohort was told to trust — the convention, the
      court, the framework — had a duty and did not act on it. That
      reading lands as moral injury, not disappointment. The body
      registers it as betrayal long before the analysis does.

  - id: v2
    text: >
      Gen Z is reading this story not for new information but for
      confirmation. The harm was named. The protocol existed. The
      mechanism failed anyway. The reaction is not anger at the
      perpetrators; it is a quieter recoil from the institution that
      was supposed to act and didn't. That recoil has a name: moral
      injury.

  - id: v3
    text: >
      What lives in the body after this kind of news is not rage. It
      is the slower load of carrying a contradiction: the rule
      existed, the failure was documented, no consequence followed.
      Moral injury is what the cohort calls the residue when the
      framework's silence becomes evidence about the framework.

  - id: v4
    text: >
      The cohort is not naive about institutional friction. What this
      story names is something sharper — a failure to act on harm
      already known. The injury is not in the harm itself. It is in
      the system's refusal to do what it told the cohort it would do.
      That refusal is what moral injury actually means.

  - id: v5
    text: >
      The harder finding for the 16-29 audience is not the event. It
      is the institutional response: documented, deliberated, declined.
      That sequence is what moral injury catalogues. The body knows
      this signature — it has seen it before. The cohort is not
      surprised. It is calibrating around the pattern.
```

## Selection heuristic

The pipeline picks a reaction atom in one of three ways (in order of preference):

1. **LLM classifier (--expand mode).** A short LLM call reads the news summary + topic and returns one reaction_id from the taxonomy. Prompt at `pearl_news/prompts/gen_z_reaction_classifier.txt`.
2. **Topic-fallback (--no-expand mode).** Look up `gen_z_reaction_topic_map.yaml` for the article's topic; pick the first reaction listed.
3. **Default.** If neither selects, use `recognition_relief` (least likely to misframe).

Once a reaction_id is chosen, rotate variation by:
```
variation_index = hash(article_id + reaction_id) % 5
```
Deterministic — same article always renders the same variation. Lets editors review the picked variation in QA.

## Topic → reaction default map (fallback)

```yaml
# pearl_news/config/gen_z_reaction_topic_map.yaml
# Default reaction-type per topic for --no-expand pipeline runs.
# Order matters: first item is the primary; subsequent are secondary candidates.

climate:           [displacement_anxiety, future_foreclosure, acceleration_dread]
peace_conflict:    [moral_injury, body_overload, solidarity_pull]
economy_work:      [future_foreclosure, narrative_thinning, agency_loss]
partnerships:      [agency_loss, betrayal_by_institutions, recognition_relief]
inequality:        [narrative_thinning, betrayal_by_institutions, solidarity_pull]
education:         [epistemic_disorientation, agency_loss, future_foreclosure]
mental_health:     [body_overload, narrative_thinning, recognition_relief]
ai_regulation:     [epistemic_disorientation, agency_loss, acceleration_dread]
migration:         [displacement_anxiety, moral_injury, compassion_overload]
generic:           [recognition_relief]   # last-resort default
```

## Library footprint

```
pearl_news/atoms/gen_z_reactions/
  SCHEMA.md                       (this file)
  displacement_anxiety.yaml       (5 × ~50 words)
  moral_injury.yaml               (5 × ~50 words)
  agency_loss.yaml                (5 × ~50 words)
  future_foreclosure.yaml         (5 × ~50 words)
  betrayal_by_institutions.yaml   (5 × ~50 words)
  compassion_overload.yaml        (5 × ~50 words)
  epistemic_disorientation.yaml   (5 × ~50 words)
  acceleration_dread.yaml         (5 × ~50 words)
  recognition_relief.yaml         (5 × ~50 words)
  solidarity_pull.yaml            (5 × ~50 words)
  body_overload.yaml              (5 × ~50 words)
  narrative_thinning.yaml         (5 × ~50 words)
```

Total content investment: 12 reactions × 5 variations × ~50 words = **3,000 words**, written once, reusable across the entire Pearl News catalog forever.

Compare to the alternative (one variation per topic-event pair): 9 topics × 100+ events/year × 50 words = **45,000 words/year**, never reusable.

## Loader contract (already wired in assemble_v52.py)

The v2 renderer reads `slots["gen_z_reactions"]` and emits it under the "How this news is affecting Gen Z" section. The pipeline step that fills that slot does:

```python
# pseudo
reaction_id = pick_reaction(item)  # LLM or topic-map
atom = load_yaml(f"pearl_news/atoms/gen_z_reactions/{reaction_id}.yaml")
variation_idx = stable_hash(item["id"], reaction_id) % len(atom["variations"])
item["_v52_slots"]["gen_z_reactions"] = atom["variations"][variation_idx]["text"]
```

Then `slot_expansion_engine` propagates `_v52_slots["gen_z_reactions"]` through to render. No LLM call needed for the prose itself — only for the classifier picking the reaction-type.

## Open questions for operator review

1. **Taxonomy completeness.** Are there reaction-types missing from this 12? Common Gen-Z research adds: `algorithmic_grief`, `anticipatory_loss`, `peer_modeling_pressure`. Worth a follow-up review with an editor.
2. **Locale variants.** Should each variation be authored separately in ja / zh-cn, or LLM-translated from en? Authored is more authentic; translated is cheaper. Recommend authored for the 4-5 highest-frequency reactions; LLM-translate the rest with editor pass.
3. **Editorial review cycle.** Operator pre-publishes 5 variations per reaction → editor reviews → ship to atom file. Then ANY article using that reaction renders the reviewed prose.
4. **Diversity / overlap guard.** Two articles published the same day should not show the same variation. Add a deterministic-rotation key that includes pub_date (already done in some existing teacher_topic_packs as `deterministic_rotation_key: article_id + slot + teacher_id + topic`).
