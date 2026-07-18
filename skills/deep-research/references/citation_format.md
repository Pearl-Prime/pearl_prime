# Citation Format & Output Template

Every research output is a markdown file saved to the repo. This document defines
the exact format.

---

## File location

```
research/<YYYY-MM-DD>_<topic-slug>.md
```

Example: `research/2026-03-30_gen-z-consumer-trends-shanghai.md`

The `research/` directory is at the root of the phoenix_omega workspace.
Create it if it doesn't exist. Use `scripts/init_research_dir.sh` to generate
the filepath.

The topic slug should be lowercase, hyphenated, and under 60 characters.

---

## Output template

Every research file MUST follow this structure:

```markdown
# Research: [Full Topic Title]

**Date:** YYYY-MM-DD
**Query:** [The exact research query as given by the user]
**Region:** [Auto-detected region or "Global/US"]
**Requested by:** [User name if known, or "tech lead"]

## Research metadata

| Field | Value |
|-------|-------|
| Tools used | [List each tool that returned results] |
| Tools quota-exhausted | [List any tools that hit quota, or "None"] |
| Tools skipped | [List any tools not in the cascade for this region] |
| Total sources | [Count of unique URLs] |
| Research duration | [Approximate time from start to finish] |

---

## Findings

[Organized by sub-topic or theme. Use ### headers for sub-sections.]

### [Sub-topic 1]

[Prose with inline citations. Every factual claim gets a citation number.]

Example: The Gen Z segment in Shanghai represents approximately 23% of the
city's consumer spending [1], with a strong preference for domestic brands
over international ones [2][3].

### [Sub-topic 2]

[Continue with cited findings...]

---

## Conflicts & gaps

[Note any contradictions between sources, or topics where no tool returned
useful results.]

- **Conflict:** Source [2] claims X while source [5] claims Y. The discrepancy
  may be due to [possible explanation].
- **Gap:** No results found for [specific sub-topic] across [tools tried].

---

## Sources

[Numbered list. Every citation used in the Findings section must appear here.]

[1] "Article or page title" — https://full-url.com/path
    *Via: [Tool name that found this]*

[2] "Article or page title" — https://full-url.com/path
    *Via: [Tool name]*

[3] (translated from Chinese) "Article title in English" — https://example.cn/path
    *Via: DeepSeek Deep Research*

[4] [ChatGPT Deep Research, no URL provided] — Description of the claim and
    context provided by the tool.
```

---

## Citation rules

1. **Every factual claim needs a citation.** No exceptions. If you can't cite it,
   don't include it.

2. **Inline citations use bracketed numbers:** `[1]`, `[2]`, `[3]`, etc.
   Multiple citations for one claim: `[2][3]` (no space between).

3. **Sources section is mandatory.** Must list every citation number used in the
   findings with:
   - The page or article title (in quotes)
   - The full URL
   - Which research tool found it

4. **No-URL citations.** If a research tool provides a finding with a clear source
   attribution but no clickable URL, cite as:
   `[N] [Tool Name, no URL provided] — Description of source`
   This is acceptable but should be minimized. Prefer tools that give real URLs.

5. **Translated sources.** When a source was found in a non-English language and
   translated, mark it: `(translated from [language])` before the title.

6. **Cross-tool validation.** When multiple tools find the same fact from the same
   source, cite it once but note all tools that confirmed it:
   `*Via: Gemini Deep Research, ChatGPT Deep Research*`

7. **Numbering.** Citations are numbered sequentially starting at [1] in the order
   they first appear in the Findings section. Don't reorder by tool or by section.

---

## What NOT to include

- No training-data-only claims. If it didn't come from a research tool result
  with a source, it doesn't go in the report.
- No speculative analysis beyond what the sources support. Synthesis is fine;
  fabrication is not.
- No source URLs that are clearly hallucinated by the research tool (common with
  ChatGPT). If a URL looks suspicious (wrong domain for the claimed publication,
  404-style path), note it as `[unverified URL]` and try to cross-reference.

---

## Downstream integration notes

When research is done for a specific repo subsystem, add a final section:

```markdown
## Repo integration

**Target subsystem:** [atoms / teacher banks / location profiles / etc.]
**Spec reference:** [e.g., SOURCE_BANK_REPAIR_DEV_SPEC §3]
**Actionable for:** [Pearl_Writer / Pearl_Editor / Pearl_Dev / etc.]

### Key findings for [subsystem]

[Bullet points of the most directly usable findings, with citation numbers,
framed in terms of what the downstream agent needs to know.]
```

This section is optional when the research is general-purpose and not tied to
a specific repo task.
