# Agent Prompt Packs

This directory is the canonical archive for large Phoenix Omega prompt packs.

Use it when a task needs more than three agents or cannot be safely expressed as
one paste-ready prompt.

## Directory Convention

Create one directory per program:

```text
docs/agent_prompt_packs/<YYYYMMDD>_<slug>/
```

Required files:

```text
00_MASTER_DISPATCH_PROMPT.md
01_<Agent>_<lane>.md
02_<Agent>_<lane>.md
...
INDEX.md
```

## Required Index Fields

`INDEX.md` must include:

- program goal;
- live origin/main anchor used by router;
- source request summary;
- prompt count;
- wave order;
- dependencies;
- owner/substrate per lane;
- hot-file conflict notes;
- required output tags;
- final audit or release gate;
- cleanup and handoff requirements.

## Existing Packs

- [Manga 100% agent prompt pack, 2026-07-14](../manga_100pct_agent_prompt_pack_20260714/) — created before this canonical archive existed; retained in place and indexed here.
- [PR Backlog Clear, 2026-07-14](20260714_pr_backlog_clear/) — 18 lanes to merge/reconcile the 1,609-open-PR backlog (14 catalog-locale merge sweeps, the Enhancement Contract V2.1 chain, a mergeable-singles sweep, stale/conflicting reconciliation, and a final auditor).

## Router

Use [AGENT_PROMPT_ROUTER_V4.md](../AGENT_PROMPT_ROUTER_V4.md) to generate future packs.
