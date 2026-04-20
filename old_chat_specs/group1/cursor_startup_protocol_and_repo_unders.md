# Startup protocol and repo understanding
_Exported on 4/16/2026 at 19:41:08 GMT+8 from Cursor (3.1.15)_

---

**User**

pland a; [what do you think: [Not by itself.

## My assessment

That instruction is **good as a safety gate**, but **not sufficient as “all you need to know about the repo.”**

It tells me a lot about **how to begin work safely**, but not enough about:

* the actual system truth
* the business model
* the existing workstreams
* the brand-admin reality
* the source-of-truth files for this specific task
* whether the requested presentation matches the current repo state

So as Pearl_Prez, I’d say:

## What that startup instruction is good for

It is strong for:

* preventing reckless work
* forcing a clean startup ritual
* checking overlap with existing workstreams
* checking unsafe branch state
* catching temp-only risk
* catching missing authority docs
* forcing a receipt before action

That is good operational hygiene.

---

## What it does **not** tell me

It does **not** tell me:

### 1. What the repo actually is

It does not explain:

* Pearl Prime
* Pearl News
* brand system
* imprints
* emotional families
* personas
* topics
* release model
* onboarding surfaces
* freebie model
* publishing logic

### 2. What the current source of truth is for this task

For a Brand Admin opportunity/onboarding system, I would still need to know which docs are authoritative for:

* brand registry
* archetypes / families / imprints
* marketing language
* release velocity
* freebies / proof loop
* onboarding workflows
* current UI / HTML assets
* revenue framing

### 3. Whether the task already exists in another form

A startup receipt can say “possible overlap,” but it does not itself explain:

* what existing onboarding assets already exist
* what current HTML pages already exist
* what current applications / wizards already exist
* what current docs already serve as onboarding
* what has already been promised to users

### 4. What a Brand Admin really needs to understand

That requires reading the business and system docs, not just startup protocol docs.

---

## So is the dev’s sentence enough?

## Answer: **No.**

It is enough to begin **safely**, but not enough to begin **intelligently**.

It is a **startup gate**, not a **repo understanding layer**.

---

## The right way to think about it

That instruction belongs in this sequence:

### Layer 1 — startup control

* read `ONBOARDING_START_HERE.md`
* read `SESSION_UNITY_PROTOCOL.md`
* return startup receipt
* check overlap / risk / authority gaps

### Layer 2 — system truth

* read `SYSTEM_STATE_MASTER.md`
* read `DOCS_INDEX.md`
* read relevant authority docs for the task

### Layer 3 — domain truth for this task

For Pearl_Prez on Brand Admin onboarding, that likely means:

* brand registry / brand architecture docs
* marketing and consumer language docs
* release velocity docs
* freebie / proof loop docs
* revenue model docs
* existing onboarding/apply materials
* relevant HTML/UI assets already present

### Layer 4 — audience translation

Only then can Pearl_Prez translate repo truth into human-facing presentation.

---

## Why your earlier evaluation was basically right

Your critique correctly identified the main issue:

> the plan was built without reading the repo

That is the core problem.

A clean startup instruction does **not** fix that problem by itself.

It only prevents chaotic action.

It does **not** automatically create repo-grounded understanding.

So your conclusion stands:

* the generic onboarding architecture was useful
* but it was not Phoenix-Omega-specific enough
* and repo-grounded translation is still required

That’s the right criticism.

---

## Best version of the dev instruction

If I were tightening it for Pearl_Prez, I’d want it to say something like this in spirit:

### Startup gate

* Read `docs/ONBOARDING_START_HERE.md` and `docs/SESSION_UNITY_PROTOCOL.md`
* Return `STARTUP_RECEIPT` only
* Stop if overlap, unsafe branch, temp-only risk, or missing authority docs

### Then domain grounding

* Read `docs/SYSTEM_STATE_MASTER.md`
* Read `docs/DOCS_INDEX.md`
* Read the authority docs for the subsystem you are presenting
* Read the actual business / brand / marketing / onboarding sources relevant to the audience
* Do not create presentation architecture until repo-backed sources are identified

That would be much stronger.

---

## Final verdict

## The dev’s instruction is necessary, but not sufficient.

It tells me:

* how to start safely

It does **not** tell me:

* all I need to know about the repo
* all I need to know about this task
* all I need to know about Brand Admin onboarding

So if the question is:

> “does this tell you all you need know about the repo?”

My answer is:

## No.

It tells me how to avoid starting wrong.
It does not tell me enough to present the repo and business correctly.

The right move after that startup instruction is still to read the relevant repo truth before designing anything.] and : [Yes. And it should be **one startup master prompt**, not a vague reminder.

Also yes: **this is exactly the kind of thing Pearl_PM should manage**.

A new agent should not have to guess:

* how to start
* what to read
* whether the task is already in progress
* where the project plan is
* what source of truth governs the task
* whether they should stop and redirect to an existing workstream

## The key idea

You want **one universal startup prompt** that does 3 jobs:

### 1. Safe startup

Checks branch state, overlap, missing docs, temp-only risk, etc.

### 2. Workstream awareness

Checks whether the task is already partially done, already assigned, or belongs inside an existing project plan.

### 3. Domain grounding

Forces the agent to read the actual repo truth relevant to the task before doing design, writing, coding, or planning.

That is the correct model.

---

# What Pearl_PM should do

Yes — in a mature system, **Pearl_PM should be the traffic controller**.

A new agent comes in and Pearl_PM should be able to determine:

* is this already an active workstream?
* is there already a project plan?
* is there already partial implementation?
* is this blocked by missing authority?
* is this unsafe to do in current branch state?
* should this agent continue here, or move to an existing thread/workstream?

So the startup prompt should explicitly instruct the new agent to:

* consult the PM/workstream layer first
* report overlap before action
* avoid duplicating partially completed work
* treat “existing workstream” as a hard stop unless explicitly told otherwise

---

# Best answer to your question

## Yes — you should have one master startup prompt for all new chats.

But it should not try to contain “everything they need to know” inside the prompt itself.

That would become bloated and stale.

Instead, the prompt should tell them:

* **how to start**
* **what to check**
* **who/what to consult first**
* **what receipt to return**
* **what docs to read next depending on the task**
* **when to stop**
* **how to avoid duplicate work**

So the prompt should be a **startup protocol + routing layer**, not a full system encyclopedia.

---

# Recommended universal startup prompt

Here is the version I would use.

---

## **UNIVERSAL STARTUP PROMPT FOR ALL NEW AGENTS / CHATS**

Read and follow this exactly.

Do not begin work yet.
Do not plan, write, code, edit, or redesign anything yet.
First determine whether this task is already part of an existing workstream and whether the repo is in a safe state for you to proceed.

### Step 1 — Startup safety and session protocol

Read these first:

* `docs/ONBOARDING_START_HERE.md`
* `docs/SESSION_UNITY_PROTOCOL.md`

If either is missing, say so and stop.

### Step 2 — PM / workstream check before doing anything

Check whether this task already belongs to an active or partial workstream.

You must determine:

* whether Pearl_PM already has a project plan for this task or adjacent task
* whether this task is already partially completed somewhere else
* whether another branch, PR, doc, or workstream already owns it
* whether continuing here would duplicate or conflict with existing work

If the task overlaps an existing workstream, stop and say:

* what appears to overlap
* where the work seems to live
* whether this chat should continue there instead

Do not continue until overlap is resolved.

### Step 3 — Repo truth and authority routing

If safe to continue, read:

* `docs/SYSTEM_STATE_MASTER.md`
* `docs/DOCS_INDEX.md`

Then identify the authority docs for the subsystem or domain you are changing, presenting, evaluating, or writing about.

If the authority docs are missing, unclear, or conflicting, stop and say so before doing any work.

### Step 4 — Real-source grounding

Before proposing any solution, determine the actual repo-backed sources relevant to the task.

Examples:

* for presentation/onboarding tasks: brand registry, business model docs, marketing docs, onboarding docs, release model docs, existing HTML/UI/docs
* for coding tasks: subsystem authority docs, configs, schemas, scripts, tests, artifacts
* for business/marketing tasks: revenue docs, release cadence docs, funnel docs, brand docs, consumer language docs

Do not invent architecture from generic assumptions when repo-backed sources exist.

### Step 5 — Branch and temp-risk check

Before work begins, determine whether there is:

* unsafe branch state
* partial unmerged work
* temp-only artifacts risk
* stale or contradictory local-only work
* missing evidence needed to proceed safely

If any of these exist, stop and report them first.

### Step 6 — Return STARTUP_RECEIPT only

Your first response must be a complete `STARTUP_RECEIPT` only.

It must include:

1. task understanding
2. startup docs read status
3. Pearl_PM / workstream overlap status
4. branch / worktree / temp-risk status
5. authority docs identified
6. additional repo sources required for this task
7. blockers or risks
8. explicit statement of whether it is safe to proceed

Do not do the task yet in the first response.
Do not provide design, writing, code, or implementation until the `STARTUP_RECEIPT` is complete and shows it is safe and grounded to proceed.

### Hard rules

* Never assume this chat is the right place for the work until overlap is checked.
* Never redo work that already belongs to an active workstream.
* Never claim understanding of the system from startup docs alone.
* Never create proposals from generic SaaS assumptions when repo truth exists.
* Never claim readiness without evidence from actual repo sources.

---

# Why this version is better

Because it solves the actual failure modes:

## It prevents

* duplicate work
* generic answers disconnected from repo truth
* agents starting in the wrong chat
* agents missing partial existing work
* agents inventing architecture from assumptions
* agents ignoring authority docs

## It enables

* Pearl_PM coordination
* workstream continuity
* proper routing
* safer branch behavior
* better repo-grounded outputs

---

# Important design principle

The startup prompt should not try to **teach the whole repo**.

That is not realistic.

Instead it should force the agent to do this sequence:

## **startup → workstream check → authority routing → task-specific grounding → receipt → work**

That is the scalable model.

---

# Best companion idea

If you really want this to work well, Pearl_PM should maintain a small number of structured artifacts the startup prompt can point to, such as:

* active workstreams
* project plans
* partial work index
* ownership map
* current branch/worktree map
* blocked / paused initiatives
* “continue over there” references

Then the startup prompt becomes much more powerful, because the agent is not checking blindly.

---

# My direct answer

## Yes, you can give all new chats one startup prompt.

And yes, **Pearl_PM should be the thing that tells a new agent**:

> “this task is already part done — continue it over there”

That is exactly right.

The best universal prompt is not “everything they need to know,” but:

## “everything they need to do before they start.”

If you want, I can turn this into a **clean repo-ready master prompt** with a strict `STARTUP_RECEIPT` format.] and; [# Universal Agent Startup & Workstream Routing Spec

## Purpose

Define a single startup protocol that every new agent/chat must follow before doing any work in the repo. The protocol prevents duplicate work, unsafe starts, generic answers disconnected from repo truth, and workstream collisions. It ensures each new agent first checks startup safety, active workstreams, authority docs, repo grounding, and whether the task belongs elsewhere.

This spec is for the **startup and routing layer**, not for teaching the whole repo in one prompt.

---

## Problem this solves

New agents currently risk:

* starting work without reading the startup docs
* duplicating work already underway in another branch, PR, chat, or workstream
* answering from generic assumptions instead of repo truth
* missing missing-authority conditions
* working in unsafe or temp-only branch states
* creating beautiful but incorrect artifacts because they did not ground in actual system sources
* proceeding in the wrong chat when Pearl_PM should have redirected them to an active workstream

The system needs one mandatory startup protocol that every new chat follows.

---

## Scope

This spec covers:

* the universal startup prompt
* the required startup sequence
* the role of Pearl_PM in routing and overlap detection
* the required `STARTUP_RECEIPT`
* stop conditions
* workstream routing behavior
* the minimum supporting artifacts Pearl_PM should maintain

This spec does **not** define:

* full repo onboarding content
* domain-specific implementation rules
* detailed subsystem behavior
* branch/CI mechanics beyond startup safety checks
* a replacement for subsystem authority docs

---

## Core principles

### 1. Start safely before starting intelligently

Every agent must first verify startup safety before attempting task work.

### 2. Check for existing work before creating new work

An agent must assume the task may already belong to an existing workstream.

### 3. Startup docs are not enough

Reading startup docs does not equal understanding the repo or task domain.

### 4. Repo truth beats generic assumptions

If repo-backed sources exist, the agent must ground in them before proposing or building anything.

### 5. Pearl_PM is the traffic controller

Pearl_PM is responsible for identifying overlap, active plans, partial completion, and correct routing.

### 6. The first response is a receipt, not work

The first response must be a structured `STARTUP_RECEIPT` only.

---

## Desired system behavior

When a new chat starts:

1. The agent reads the startup docs.
2. The agent checks with the PM/workstream layer first.
3. The agent determines if the task is already part of an active or partial workstream.
4. The agent identifies the authority docs and repo sources needed for this task.
5. The agent checks branch/worktree/temp-only risk.
6. The agent returns `STARTUP_RECEIPT` only.
7. The agent does no actual task work until the receipt shows it is safe and grounded to proceed.

---

## Universal startup prompt

Use this exact behavior as the base startup protocol for all new agents/chats.

### Master startup prompt

Read and follow this exactly.

Do not begin work yet.
Do not plan, write, code, edit, redesign, or evaluate solutions yet.
First determine whether this task is already part of an existing workstream and whether the repo is in a safe state for you to proceed.

#### Step 1 — Startup safety and session protocol

Read these first:

* `docs/ONBOARDING_START_HERE.md`
* `docs/SESSION_UNITY_PROTOCOL.md`

If either is missing, say so and stop.

#### Step 2 — PM / workstream check before doing anything

Check whether this task already belongs to an active or partial workstream.

You must determine:

* whether Pearl_PM already has a project plan for this task or an adjacent task
* whether this task is already partially completed somewhere else
* whether another branch, PR, doc, or workstream already owns it
* whether continuing here would duplicate or conflict with existing work

If the task overlaps an existing workstream, stop and say:

* what appears to overlap
* where the work seems to live
* whether this chat should continue there instead

Do not continue until overlap is resolved.

#### Step 3 — Repo truth and authority routing

If safe to continue, read:

* `docs/SYSTEM_STATE_MASTER.md`
* `docs/DOCS_INDEX.md`

Then identify the authority docs for the subsystem or domain you are changing, presenting, evaluating, or writing about.

If the authority docs are missing, unclear, or conflicting, stop and say so before doing any work.

#### Step 4 — Real-source grounding

Before proposing any solution, determine the actual repo-backed sources relevant to the task.

Examples:

* for presentation/onboarding tasks: brand registry, business model docs, marketing docs, onboarding docs, release model docs, existing HTML/UI/docs
* for coding tasks: subsystem authority docs, configs, schemas, scripts, tests, artifacts
* for business/marketing tasks: revenue docs, release cadence docs, funnel docs, brand docs, consumer language docs

Do not invent architecture from generic assumptions when repo-backed sources exist.

#### Step 5 — Branch and temp-risk check

Before work begins, determine whether there is:

* unsafe branch state
* partial unmerged work
* temp-only artifacts risk
* stale or contradictory local-only work
* missing evidence needed to proceed safely

If any of these exist, stop and report them first.

#### Step 6 — Return STARTUP_RECEIPT only

Your first response must be a complete `STARTUP_RECEIPT` only.

It must include:

1. task understanding
2. startup docs read status
3. Pearl_PM / workstream overlap status
4. branch / worktree / temp-risk status
5. authority docs identified
6. additional repo sources required for this task
7. blockers or risks
8. explicit statement of whether it is safe to proceed

Do not do the task yet in the first response.
Do not provide design, writing, code, or implementation until the `STARTUP_RECEIPT` is complete and shows it is safe and grounded to proceed.

#### Hard rules

* Never assume this chat is the right place for the work until overlap is checked.
* Never redo work that already belongs to an active workstream.
* Never claim understanding of the system from startup docs alone.
* Never create proposals from generic SaaS assumptions when repo truth exists.
* Never claim readiness without evidence from actual repo sources.

---

## Pearl_PM responsibilities

Pearl_PM should act as the repo’s workstream traffic controller.

### Pearl_PM must be able to tell a new agent:

* this task already belongs to an active workstream
* this task is partially completed
* this task should continue in another branch/chat/PR/doc
* this task is blocked by missing authority
* this task is unsafe in current branch/worktree state
* this task is not yet routable because PM metadata is incomplete

### Pearl_PM owns:

* workstream detection
* project plan ownership
* overlap detection
* routing decisions
* “continue over there” redirection
* ensuring that new work is not started when existing work should be continued

### Pearl_PM should not be bypassed

If PM/workstream metadata exists, new agents must consult it before doing task work.

---

## Required `STARTUP_RECEIPT` format

Every new agent’s first response must be a structured receipt. Suggested schema:

### STARTUP_RECEIPT

#### 1. Task understanding

* what the agent believes the user is asking for
* the likely domain(s) involved

#### 2. Startup docs status

* `ONBOARDING_START_HERE.md`: found/read or missing
* `SESSION_UNITY_PROTOCOL.md`: found/read or missing

#### 3. Workstream / Pearl_PM status

* active workstream found: yes/no/unknown
* project plan found: yes/no/unknown
* overlap risk: none / possible / confirmed
* recommended routing: continue here / continue elsewhere / stop pending clarification

#### 4. Branch / worktree / temp-risk status

* branch safety: safe / unsafe / unknown
* partial unmerged work risk: yes/no/unknown
* temp-only risk: yes/no/unknown
* local-only contradiction risk: yes/no/unknown

#### 5. Authority docs identified

* list of governing docs for this task
* note any missing or conflicting authority

#### 6. Additional repo sources needed

* repo files/docs/configs/scripts/artifacts needed before work begins

#### 7. Blockers or risks

* missing docs
* overlap
* unsafe state
* missing PM metadata
* conflicting authorities
* insufficient repo grounding

#### 8. Proceed status

* safe to proceed: yes/no
* reason

---

## Stop conditions

The agent must stop and not begin task work if any of the following are true:

### Missing startup docs

If `ONBOARDING_START_HERE.md` or `SESSION_UNITY_PROTOCOL.md` is missing.

### Existing workstream overlap

If there is confirmed or unresolved overlap with an active or partial workstream.

### Missing authority docs

If the governing authority docs for the task cannot be identified.

### Unsafe branch/worktree state

If branch/worktree state is known to be unsafe.

### Temp-only or local-only contradiction risk

If the task may be based on temp-only, stale, or conflicting local work that is not safe to build on.

### Insufficient repo grounding

If the agent is being pushed toward generic planning without identifying the actual repo sources needed.

---

## Workstream routing rules

### Rule 1 — Existing work wins

If a task already belongs to an active or partial workstream, the default action is to continue there, not start over here.

### Rule 2 — New chat is not assumed to be correct

A new chat is only the correct place for the task if no owned workstream already exists.

### Rule 3 — Adjacent overlap counts

If the task is adjacent enough that it risks duplication, the agent must flag it and stop.

### Rule 4 — Partial completion must be surfaced

Even if the work is incomplete, the agent must report where it lives and what looks already started.

### Rule 5 — Pearl_PM routing is authoritative

If Pearl_PM says “this task is part done — continue over there,” the new agent should not proceed independently.

---

## Minimum supporting artifacts Pearl_PM should maintain

The startup prompt becomes much more effective if Pearl_PM maintains a small, structured project-memory layer.

### 1. Active workstreams index

Tracks:

* workstream ID
* title
* owner
* status
* linked branches/PRs/docs/chats
* subsystem/domain
* last updated

### 2. Project plans index

Tracks:

* plan ID
* title
* related workstream
* current stage
* authority docs
* open decisions
* blockers

### 3. Partial work registry

Tracks:

* partially completed tasks
* where the work lives
* whether it is safe to continue
* whether it is stale

### 4. Routing registry

Tracks:

* canonical place to continue work
* replacement/superseded workstreams
* pause/blocked states

### 5. Branch/worktree risk snapshot

Tracks:

* unsafe branches
* temporary work areas
* local-only experiments
* work that should not be used as source of truth

### 6. Authority map

Tracks:

* subsystem → authority docs
* domain → authority docs
* fallback routing when authority is missing

---

## v1 implementation guidance

If this is implemented incrementally, the order should be:

### Phase 1 — Prompt + receipt

* adopt the universal startup prompt
* require `STARTUP_RECEIPT` as first response
* enforce “no work before receipt”

### Phase 2 — Pearl_PM workstream awareness

* maintain active workstreams and project plans
* allow the agent to detect overlap and redirect

### Phase 3 — Authority routing support

* maintain lightweight authority map
* make it easier for agents to identify the right docs

### Phase 4 — Branch/temp risk support

* maintain risk metadata so agents can stop earlier and more accurately

---

## Acceptance criteria

This spec is successful when:

### Startup behavior

* every new agent/chat starts with the startup protocol
* the first response is always `STARTUP_RECEIPT` only

### Workstream behavior

* agents consistently detect and report overlap
* agents stop when work belongs to an existing workstream
* Pearl_PM can redirect agents to the correct location

### Repo grounding

* agents no longer produce generic plans without identifying repo sources
* startup docs are no longer mistaken for complete repo understanding

### Safety behavior

* agents stop on missing startup docs
* agents stop on missing authority docs
* agents stop on unsafe or temp-only conditions

### Human clarity

* the startup protocol is short enough to reuse everywhere
* the actual repo understanding still comes from docs and sources, not from bloating the startup prompt

---

## Non-goals

This spec does not try to:

* compress the whole repo into one prompt
* replace `DOCS_INDEX.md`
* replace `SYSTEM_STATE_MASTER.md`
* replace subsystem authority docs
* solve all PM tooling in one step
* provide detailed implementation behavior for every domain

---

## Final recommendation

Adopt a **single universal startup protocol** for all new chats, but keep it focused on:

* safe startup
* PM/workstream routing
* authority identification
* repo grounding
* receipt-first behavior

Do **not** try to make one prompt teach the entire repo. The right model is:

## startup → workstream check → authority routing → repo grounding → STARTUP_RECEIPT → work

That is the scalable, repo-safe, Pearl_PM-compatible approach.] should i have dev build?] . do: Yes, but build it as a repo system, not just another long prompt.

My take on the three drafts:

- The first analysis is right: startup protocol is necessary, but not sufficient.
- The second “universal startup prompt” is directionally right, but too long to be the only thing pasted into every chat.
- The third “startup & routing spec” is good as an internal design doc, but it should not become a parallel authority that competes with [SESSION_UNITY_PROTOCOL.md](/Users/ahjan/phoenix_omega/docs/SESSION_UNITY_PROTOCOL.md).

Best move: have the dev build this as a 4-part package.

1. Upgrade the existing protocol
- Extend [SESSION_UNITY_PROTOCOL.md](/Users/ahjan/phoenix_omega/docs/SESSION_UNITY_PROTOCOL.md), don’t create a rival protocol.
- Add:
  - mandatory task-specific authority doc
  - mandatory “additional repo sources needed”
  - mandatory project/workstream id if known
  - explicit “startup docs are not enough” rule
  - explicit “existing workstream wins” rule

2. Add a short copy-paste master prompt
- Put a short reusable prompt in a single canonical place, like a section in [SESSION_UNITY_PROTOCOL.md](/Users/ahjan/phoenix_omega/docs/SESSION_UNITY_PROTOCOL.md) or a small companion doc.
- It should be short enough to paste into every new chat.
- It should always require:
  - startup docs
  - PM/workstream check
  - authority-doc check
  - `STARTUP_RECEIPT` only
  - task-specific authority if provided

3. Add the missing Pearl_Dev lane
- Create:
  - `docs/PEARL_DEV_ONBOARDING.md`
  - `docs/PEARL_DEV_STATE.md`
  - `skills/pearl-dev/SKILL.md`
- Right now agents keep getting fuzzy because Pearl_Dev exists socially, but not as a clean repo-native authority lane.

4. Add a lightweight authority map
- Keep [ACTIVE_PROJECTS.tsv](/Users/ahjan/phoenix_omega/artifacts/coordination/ACTIVE_PROJECTS.tsv) and [ACTIVE_WORKSTREAMS.tsv](/Users/ahjan/phoenix_omega/artifacts/coordination/ACTIVE_WORKSTREAMS.tsv).
- Add one small subsystem-to-authority map, preferably machine-readable.
- Do not build a giant PM bureaucracy unless someone will maintain it.

What not to do:
- Don’t make a huge prompt that tries to teach the whole repo.
- Don’t create another overlapping protocol doc unless it replaces or folds into the current one.
- Don’t add lots of registries that will go stale.

So yes, I do think you should have a dev build this, but the deliverable should be:
- one upgraded protocol
- one short universal prompt
- one real Pearl_Dev package
- one simple authority map

That would actually fix the failure mode.

If you want, I can write the exact build spec for the dev next.

---

**Cursor**

Researching the repo to ground a plan for the 4-part startup/workstream package you described.



Noting a gap: `SESSION_UNITY_PROTOCOL.md` lists Pearl_PM, Pearl_GitHub, Pearl_Writer, and Pearl_Editor under "Then defer by lane" but omits Pearl_Dev (and Pearl_Prez). We'll include adding Pearl_Dev to the defer table in the plan.



---

**User**

I think that plan is right.

Best parts:

extend SESSION_UNITY_PROTOCOL.md instead of creating a rival authority
add a real Pearl_Dev lane
keep the paste prompt short
use one small authority map, not a giant PM system
I’d make only 3 adjustments:

Keep ONBOARDING_START_HERE.md as the first entry point, but make SESSION_UNITY_PROTOCOL.md the canonical startup contract.
Add WORKSTREAM_ID and ADDITIONAL_SOURCES to the receipt exactly as you proposed.
In the starter prompt, always include the task authority doc and approved base/workstream if known. That’s what prevents the “I followed the protocol but still don’t know my lane” failure.


---

**Cursor**

Updating the plan document to incorporate your three adjustments.



Updating the plan: adding explicit entry-point vs. canonical-contract hierarchy, locking receipt fields `WORKSTREAM_ID` and `ADDITIONAL_SOURCES`, and requiring the paste prompt to include task authority and approved base/workstream when known.



Updates are reflected in the plan file ([`/Users/ahjan/.cursor/plans/startup_routing_4-part_package_f302c392.plan.md`](/Users/ahjan/.cursor/plans/startup_routing_4-part_package_f302c392.plan.md)). Here is what changed:

### 1. Entry point vs canonical contract
- New **“Doc hierarchy (locked)”** subsection: [ONBOARDING_START_HERE.md](docs/ONBOARDING_START_HERE.md) stays the **first** entry; [SESSION_UNITY_PROTOCOL.md](docs/SESSION_UNITY_PROTOCOL.md) is the **canonical startup contract** (receipt, rules, defer-by-lane, paste prompt).
- Part 2 instruct line now says: start with ONBOARDING; binding text lives in Session Unity.
- Implementation step 4 and acceptance criteria require **one explicit sentence in ONBOARDING** that Session Unity is the binding contract (not a duplicate of the full protocol).

### 2. `WORKSTREAM_ID` and `ADDITIONAL_SOURCES`
- Part 1 now specifies **exact receipt field names** (no “e.g.”): `WORKSTREAM_ID` and `ADDITIONAL_SOURCES`, with the intended meaning preserved (pair with existing `PROJECT_ID`; separate from `EVIDENCE_BASIS`).
- Acceptance checklist explicitly checks those two fields in the template.

### 3. Lane-binding prefix in the starter prompt
- Part 2 adds a **“Lane-binding prefix”** block: the paste instructions must require humans to include, **when known**, (a) task authority doc path(s) and (b) approved base/workstream (`branch` / `base_ref` / `WORKSTREAM_ID`).
- Agent behavior: treat as hard inputs, echo into receipt, **stop** if live repo conflicts with approved base without override; use `UNKNOWN` + registry/PM flag instead of guessing.

Todos were tightened so `extend-session-unity` includes the ONBOARDING canonical-contract line and the paste **lane-binding** requirement; `docs-index-wire` now includes that ONBOARDING sentence explicitly.

When you want this implemented in the repo, say to **execute the plan** (or similar) and we can apply the doc changes.

---

**User**

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.

---

**Cursor**

Implementing the four-part plan: starting with Session Unity and ONBOARDING updates, then the authority map, Pearl_Dev package, and DOCS_INDEX wiring.



Implementing Session Unity updates: adding canonical-contract section, rules, read-path bullet for the authority map, defer lanes, receipt fields, and the universal paste prompt.



Here is what was implemented. All related todos are **completed**.

### 1. [docs/SESSION_UNITY_PROTOCOL.md](docs/SESSION_UNITY_PROTOCOL.md)
- **Canonical startup contract** section: ONBOARDING first entry; this file is the binding contract.
- **Rules:** startup chain ≠ full understanding; **existing workstream wins**; **mandatory task authority**.
- **Read path:** step 9 — optional [artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv](artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv).
- **Defer by lane:** **Pearl_Dev** and **Pearl_Prez** added.
- **Receipt:** `WORKSTREAM_ID`, `ADDITIONAL_SOURCES`; `SPECIALISTS_NEEDED` includes Pearl_Dev and Pearl_Prez; rules for user-supplied authority/base and contradictions.
- **Universal paste prompt** block at the end with **lane-binding** (`TASK_AUTHORITY`, `APPROVED_BRANCH_OR_BASE`, `WORKSTREAM_ID`).

### 2. [docs/ONBOARDING_START_HERE.md](docs/ONBOARDING_START_HERE.md)
- Opening paragraph: first entry point + Session Unity as **canonical contract**.
- Pointer to **[PEARL_DEV_ONBOARDING.md](docs/PEARL_DEV_ONBOARDING.md)** for engineering.
- Closing line references the “canonical contract” wording.

### 3. [artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv](artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv)
- 12 subsystems (`github_ops`, `pearl_github_lane`, `session_coordination`, `system_truth`, `pearl_news`, `qwen_api_retirement`, `phoenix_recommender`, `manga_pipeline`, `experience_layer`, `control_plane_ui`, `trend_feeds`, `pen_name_authoring`, `docs_navigation`) with tab-separated columns and `2026-03-28` dates.

### 4. Pearl_Dev lane
- [docs/PEARL_DEV_ONBOARDING.md](docs/PEARL_DEV_ONBOARDING.md)
- [docs/PEARL_DEV_STATE.md](docs/PEARL_DEV_STATE.md)
- [skills/pearl-dev/SKILL.md](skills/pearl-dev/SKILL.md)

### 5. Index and cross-link
- [docs/DOCS_INDEX.md](docs/DOCS_INDEX.md): task rows for engineering / Pearl_Dev and resume state; Session Unity row mentions the paste prompt.
- [skills/pearl-github/SKILL.md](skills/pearl-github/SKILL.md): Pearl_Dev sister line links to `pearl-dev/SKILL.md`.

The plan file was **not** modified. If you want this on a branch with push-guard preflight, say so and we can run the usual git flow next.

