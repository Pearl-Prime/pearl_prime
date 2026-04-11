# EMT Template Library

**Persona:** EMT / Paramedic (5+ years field experience)
**Complete Set:** 4 mechanisms × 4 roles = 16 templates

---

## Persona Context

EMTs and paramedics operate in a distinct first responder context:

- **Patient outcomes:** Direct responsibility for life/death, frequent exposure to death
- **Medical decisions:** Split-second clinical judgment under pressure
- **Partner dynamics:** Two-person crews create intense working relationships
- **Scene chaos:** Uncontrolled environments, bystanders, family members present
- **Systemic stress:** Understaffing, long shifts, low pay relative to responsibility
- **Specific triggers:** Pediatric calls, codes, overdoses, "couldn't save them" moments
- **Hospital interface:** Handoffs, waiting, feeling dismissed by ER staff

---

## Template Index

| Mechanism | Recognition | Mechanism Proof | Turning Point | Embodiment |
|-----------|-------------|-----------------|---------------|------------|
| Autonomic Regulation | AR-R-01 | AR-MP-01 | AR-TP-01 | AR-E-01 |
| Cognitive Defusion | CD-R-01 | CD-MP-01 | CD-TP-01 | CD-E-01 |
| Exposure Tolerance | ET-R-01 | ET-MP-01 | ET-TP-01 | ET-E-01 |
| Self-Trust Repair | ST-R-01 | ST-MP-01 | ST-TP-01 | ST-E-01 |

---

# AUTONOMIC REGULATION

> **Mechanism Truth:** "The body can downshift without certainty or resolution."

---

## AR-R-01: Recognition (Autonomic Regulation)

**Template ID:** `emt_ar_recognition_after_the_call_v1`
**Content Type:** crisis
**Resolution Level:** 0

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{character.years_on_job}}` | Years of service | seven |
| `{{partner.name}}` | Partner's name | Danny |
| `{{trigger.time}}` | Time of call | 0300 |
| `{{body.primary_sensation}}` | Main physical sensation | her hands still buzzing |

### Template

```
{{character.name}} had been running calls for {{character.years_on_job}} years.

Long enough to know which ones would stick.
Long enough to know this one shouldn't.

Routine transport.
Stable patient.
Textbook handoff at the ER.

Nothing went wrong.

But driving back to post,
{{character.name}} couldn't shake it.

{{body.primary_sensation}}.
Heart rate still up.
That feeling like something was about to happen
even though something already had
and it was fine.

{{partner.name}} was talking about dinner plans.
She nodded along.
Said the right things.

But her body was somewhere else.
Still on scene.
Still waiting for the other shoe to drop.

The call had been at {{trigger.time}}.
It was almost dawn now.

And she was still running hot.

Not because something was wrong.
Because her system hadn't gotten the memo
that the emergency was over.

She'd felt this before.
The after-buzz.
The way her body kept the engine revving
long after the lights went off.

But lately it was happening more.
And lasting longer.

And she didn't know how to turn it off.
```

### Validation Notes
- Identity anchor: years on job, partner, professional context
- Internal stakes: can't downshift, isolation (nodding along while elsewhere)
- Somatic activation: hands buzzing, heart rate, "running hot"
- No insight, no relief, no resolution
- Resolution level: 0 ✓

---

## AR-MP-01: Mechanism Proof (Autonomic Regulation)

**Template ID:** `emt_ar_mechproof_caffeine_trap_v1`
**Content Type:** constraint
**Resolution Level:** 1

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{location.detail}}` | Specific location | the rig |

### Template

```
{{character.name}} tried the obvious things.

Cut back on caffeine.
Which lasted about two shifts
before a 14-hour day made that impossible.

Tried to sleep more.
But her body didn't know the difference
between tired and wired anymore.

She'd lie down exhausted
and her heart would race
like dispatch was about to call.

She tried breathing exercises.
The ones from the wellness training.
Four counts in, hold, four counts out.

It worked sometimes.
For about ten minutes.
Then the hum came back.

She tried talking herself down.
The call is over.
Nothing bad happened.
You can relax now.

Her body didn't speak that language.

The logic made sense.
The relaxation didn't follow.

Sitting in {{location.detail}} between calls,
she'd notice it—
the tension in her shoulders,
the grip on the stretcher rail,
the way she was braced for impact
even when nothing was coming.

She couldn't think her way out of it.
Couldn't reason her way to calm.
Couldn't will her system to stand down.

The more she tried to force it,
the more her body resisted.

Like it didn't trust her
to know when it was safe.
```

### Validation Notes
- Constraint loop: trying to force calm → body resists more
- Repeated failure: caffeine, sleep, breathing, logic — none work
- Pattern language: "couldn't," "didn't work," "the more she tried"
- No instructions, no solution, no twist
- Resolution level: 1 ✓

---

## AR-TP-01: Turning Point (Autonomic Regulation)

**Template ID:** `emt_ar_turning_engine_idle_v1`
**Content Type:** reframe
**Resolution Level:** 2

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{location.detail}}` | Specific location | the ambulance bay |

### Template

```
{{character.name}} was sitting in {{location.detail}},
rig backed in, shift almost over.

Her body was still humming.
No call pending.
Nothing to do but wait.

And instead of fighting it,
she just sat with it.

Not trying to fix it.
Not telling herself to calm down.
Just noticing.

Heart still faster than it needed to be.
Shoulders still up around her ears.
That alertness with nowhere to go.

And she thought about the rig.

How even when you park it,
the engine doesn't just stop.
It idles.
Cools down.
Takes its time.

You don't yell at the engine to stop running.
You just let it do what it does.

Her body was the same.

It wasn't broken.
It was idling.

Running down from a state of readiness
the only way it knew how—
slowly, on its own schedule,
not hers.

The hum didn't stop.
But she stopped needing it to stop right now.

It was just her system
doing what systems do after running hot.

Cooling down.
At its own pace.
Not because she commanded it.
Because that's what bodies do
when you stop fighting them.
```

### Validation Notes
- Meaning inversion: "idling, not broken"
- Metaphor discovered, not delivered (the rig)
- Body still activated — no cure
- Shift through acceptance, not control
- Resolution level: 2 ✓

---

## AR-E-01: Embodiment (Autonomic Regulation)

**Template ID:** `emt_ar_embodiment_letting_idle_v1`
**Content Type:** integration
**Resolution Level:** 3

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{partner.name}}` | Partner's name | Danny |
| `{{location.home}}` | Home location | her apartment |

### Template

```
The buzz still came after calls.

{{character.name}} didn't expect it to stop.

But now, when her body stayed revved
after a stable transport,
after a routine handoff,
after nothing went wrong—

she let it.

Not fighting.
Not forcing.
Just letting the engine idle.

One night after shift,
she got home to {{location.home}}
and noticed her hands were still shaking.

Old her would've panicked.
What's wrong?
Why won't this stop?
Something must be broken.

New her just noticed.

Oh. Still idling.

She made tea.
Sat on the couch.
Let her body do what it was going to do.

Twenty minutes later,
the shaking stopped.
On its own.

Not because she fixed it.
Because she stopped getting in the way.

{{partner.name}} texted asking how shift was.

She wrote back: "Long. But okay."

And meant it.

Not okay like everything was perfect.
Okay like she could handle the imperfect.

Her body still ran hot sometimes.
But she wasn't scared of it anymore.

She just let it cool down
the way engines do.

In its own time.
At its own pace.
```

### Validation Notes
- Relational shift: letting it idle instead of fighting
- Lived example: shaking hands, making tea, letting it pass
- Body still activated — "still ran hot"
- No cure, no permanence
- Resolution level: 3 ✓

---

# COGNITIVE DEFUSION

> **Mechanism Truth:** "Thoughts can be present without being obeyed."

---

## CD-R-01: Recognition (Cognitive Defusion)

**Template ID:** `emt_cd_recognition_code_replay_v1`
**Content Type:** pattern
**Resolution Level:** 0

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{character.years_on_job}}` | Years of service | seven |
| `{{trigger.event}}` | Specific call | the code last Tuesday |
| `{{location.detail}}` | Where it happens | restocking the rig |

### Template

```
{{character.name}} couldn't stop replaying {{trigger.event}}.

The compressions.
The monitor.
The moment it went flatline
and stayed there.

She knew how it ended.
She was there.
She called it.

But her mind kept going back.

What if she'd pushed the epi faster.
What if she'd gotten there two minutes sooner.
What if she'd done one more round.

The protocol said stop.
Her partner agreed.
The ER doc confirmed.

But her brain kept asking
what if, what if, what if.

{{location.detail}}, the loop would start.
Driving home, same loop.
2 AM, lying awake, same loop.

She'd been doing this job {{character.years_on_job}} years.
Lost patients before.
It was part of the work.

But this one had gotten stuck.

Not because it was different.
Because her brain decided it mattered more.

And now it wouldn't let go.

She told herself to move on.
Think about something else.
It was a good code. You did everything right.

The thoughts didn't care what she told herself.

They just kept playing
the same scene
from a different angle
every time.
```

### Validation Notes
- Identity anchor: years on job, specific call, professional context
- Internal stakes: can't let go, intrusive replay
- Somatic implied: 2 AM awake
- Pattern established: same loop, different angles
- No insight, no relief, no resolution
- Resolution level: 0 ✓

---

## CD-MP-01: Mechanism Proof (Cognitive Defusion)

**Template ID:** `emt_cd_mechproof_review_trap_v1`
**Content Type:** constraint
**Resolution Level:** 1

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{trigger.event}}` | Specific call | the code |

### Template

```
{{character.name}} tried to review her way out of it.

Pulled up the protocol.
Went through it step by step.
Confirmed she did everything right.

The thoughts didn't care.

Yeah, but what if—

She tried arguing back.
Listing all the reasons it wasn't her fault.
The downtime before the call.
The presenting rhythm.
The comorbidities.

The thoughts found exceptions.
Every time.

She tried distracting herself.
TV, podcasts, music.
Anything to drown out the loop.

It worked until it didn't.
The thoughts waited.
And came back louder in the silence.

She tried talking to her partner about it.
He said the same things she told herself.
You did everything right.
It was their time.

And still, lying awake that night:
What if you missed something?

She tried exhausting herself.
Extra shifts.
Gym after work.
Anything to be too tired to think.

Her body got tired.
Her brain didn't.

The thoughts were patient.
Persistent.
Like they had something important to say
if she could just think about it long enough.

But {{character.years_on_job}} years in,
she'd never thought her way to peace.
```

### Validation Notes
- Constraint loop: engaging → thoughts find exceptions
- Repeated failure: reviewing, arguing, distracting, exhausting — none work
- Pattern language: "the thoughts didn't care," "every time"
- No instructions, no solution, no twist
- Resolution level: 1 ✓

---

## CD-TP-01: Turning Point (Cognitive Defusion)

**Template ID:** `emt_cd_turning_dispatch_not_truth_v1`
**Content Type:** reframe
**Resolution Level:** 2

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{location.detail}}` | Specific location | the station |

### Template

```
{{character.name}} was at {{location.detail}}
when the thought came again.

You missed something.

Same accusation.
Same certainty.
Same pull to defend herself.

But this time, she paused.

She thought about dispatch.

How sometimes the call comes in wrong.
"Chest pain" turns out to be anxiety.
"Fall" turns out to be stroke.
"Routine" turns out to be anything but.

Dispatch tells you what it thinks is happening.
Not what's actually happening.

And you learn not to trust it completely.
You show up and assess for yourself.

Her thoughts were the same.

They were dispatching information.
Urgent.
Certain.
Demanding a response.

But that didn't mean they were accurate.

You missed something.

Maybe.
Or maybe that's just what the thought says.

She didn't have to treat her thoughts
like they knew something she didn't.

They were just dispatch.
Not ground truth.

The thought kept talking.
It wasn't going to stop.

But she stopped treating it like a reliable informant.

It was just noise on the radio.
Urgent-sounding.
Not necessarily true.

She could hear it
without driving lights and sirens to respond.
```

### Validation Notes
- Meaning inversion: "dispatch, not ground truth"
- Metaphor emerges from her world
- Thought still present — no cure
- Insight feels discovered
- Resolution level: 2 ✓

---

## CD-E-01: Embodiment (Cognitive Defusion)

**Template ID:** `emt_cd_embodiment_radio_noise_v1`
**Content Type:** integration
**Resolution Level:** 3

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{partner.name}}` | Partner's name | Danny |
| `{{trigger.event}}` | Original call | that code |

### Template

```
The thoughts still came.

{{character.name}} didn't expect them to stop.

Some days the replay was loud.
Some days it was barely there.
It didn't follow rules.

But now, when the loop started—
You should've done more.
You missed something.
What if, what if, what if.

—she recognized it.

Oh. Dispatch again.

Not dismissing it.
Not arguing with it.
Just noting the transmission.

One shift, {{partner.name}} mentioned {{trigger.event}}
in passing.
Said something about the family.

And the thought fired immediately:
Your fault.

{{character.name}} felt it land.
Felt the pull to explain, defend, review.

And then let it pass.

Not because it was wrong.
Not because it was right.

Because it was just a dispatch.
And she didn't have to respond to every call.

She could let it come through.
Note it.
And keep driving.

The radio was always going to have noise.
That was the job.

But she didn't have to drop everything
every time the noise got loud.

She could hear it
and choose what was worth responding to.

Most of the time,
it wasn't this.
```

### Validation Notes
- Relational shift: hearing without responding
- Lived example: partner mentions call, she lets it pass
- Thoughts still present — "still came"
- No cure, no permanence
- Resolution level: 3 ✓

---

# EXPOSURE TOLERANCE

> **Mechanism Truth:** "Discomfort can be survived without avoidance."

---

## ET-R-01: Recognition (Exposure Tolerance)

**Template ID:** `emt_et_recognition_peds_avoidance_v1`
**Content Type:** pattern
**Resolution Level:** 0

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{character.years_on_job}}` | Years of service | seven |
| `{{trigger.call_type}}` | Avoided call type | peds calls |
| `{{body.primary_sensation}}` | Main physical sensation | her stomach turn |

### Template

```
{{character.name}} used to take whatever came.

That's the job, right?
You don't get to pick.
Dispatch calls, you go.

But somewhere along the way,
she started managing around {{trigger.call_type}}.

Little things at first.
Letting her partner take lead.
Hanging back a step.
Focusing on the parents while he worked the patient.

Then bigger things.
Mentioning casually that she'd been on a lot of those lately.
Maybe someone else could take the next one.

No one called her on it.
Everyone understood.
Those calls were hard on everyone.

But {{character.name}} knew what she was doing.

Every time dispatch said the word,
she felt {{body.primary_sensation}}.

Not just concern.
Something deeper.
Something that said: I can't do this one.

And the more she avoided,
the louder that voice got.

{{character.years_on_job}} years in,
and she was building her shifts
around calls she wouldn't take.

The world getting smaller.
The list of things she couldn't handle
getting longer.

And the worst part—
the part she wouldn't say out loud—

was that she used to be good at those calls.
One of the best.

Now she wasn't sure she could do one at all.
```

### Validation Notes
- Identity anchor: years on job, professional competence eroding
- Internal stakes: world shrinking, used to be good
- Somatic activation: stomach turn
- Pattern established: avoidance → louder voice
- No insight, no relief, no resolution
- Resolution level: 0 ✓

---

## ET-MP-01: Mechanism Proof (Exposure Tolerance)

**Template ID:** `emt_et_mechproof_relief_trap_v1`
**Content Type:** constraint
**Resolution Level:** 1

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{trigger.call_type}}` | Avoided call type | peds calls |

### Template

```
Every time {{character.name}} avoided a {{trigger.call_type}},
she felt relief.

Thank god. Not this one.

And that relief was the problem.

Her brain logged it:
Avoiding = feeling better.
Simple math.

So she avoided more.

And every time the relief came,
the dread before got worse.

It was a perfect trap
designed to make her smaller.

She tried reasoning with herself.
These calls are rare.
You've handled them before.
Most kids are fine.

Her body didn't listen to logic.
It only remembered what worked.
And avoiding worked.

She tried imagining herself through a call.
Visualizing success.
Telling herself she could do it.

Then the tones would drop
and all that preparation evaporated.

She tried pushing through once.
Took a call she would've traded.
White-knuckled the whole thing.

Kid was fine.
She was not.

Shaking for hours afterward.
And the next one was worse.
Because now her body knew
she might force it.

So the alarm got louder.

Escape didn't work.
Forcing didn't work.
The only thing that worked was avoiding.

And avoiding was slowly turning her
into someone she didn't recognize.
```

### Validation Notes
- Constraint loop: avoiding → relief → more avoidance
- Repeated failure: logic, visualization, forcing — none work
- Pattern language: "every time," "perfect trap"
- No instructions, no solution, no twist
- Resolution level: 1 ✓

---

## ET-TP-01: Turning Point (Exposure Tolerance)

**Template ID:** `emt_et_turning_through_not_around_v1`
**Content Type:** reframe
**Resolution Level:** 2

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{trigger.call_type}}` | Call type | peds |
| `{{partner.name}}` | Partner's name | Danny |

### Template

```
The call came in.
{{trigger.call_type}}.
No one to trade with.

{{character.name}}'s body did what it always did.
Stomach dropped.
Hands went cold.
Every part of her screaming: not this.

She went anyway.

Not because she was ready.
Not because she'd conquered anything.

Because {{partner.name}} was driving
and there was nowhere else to be.

On scene, her body was loud.
Heart pounding.
Thoughts racing.
That voice saying you can't do this.

She did it anyway.

Hands moving through the assessment.
Voice steady even when she wasn't.
Doing the job while her body screamed.

The kid was fine.
Broken arm. Scared but okay.

And on the way back,
something strange.

The dread was still there.
But she was still there too.

She hadn't escaped it.
She'd gone through it.

And going through hadn't killed her.

It was terrible.
She wouldn't choose it.
But she'd survived it.

Not around the fear.
Through it.

And through was a direction
she'd forgotten existed.
```

### Validation Notes
- Meaning inversion: "through, not around"
- Dread still present — no cure
- Shows survival, not victory
- "Terrible" — honest, not triumphant
- Resolution level: 2 ✓

---

## ET-E-01: Embodiment (Exposure Tolerance)

**Template ID:** `emt_et_embodiment_taking_the_call_v1`
**Content Type:** integration
**Resolution Level:** 3

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{trigger.call_type}}` | Call type | peds |
| `{{partner.name}}` | Partner's name | Danny |

### Template

```
{{character.name}} stopped trading out.

Not all at once.
Not perfectly.

Some days the dread won.
Some days she said not today
and let someone else take it.

But more often now,
she went.

Not because the fear stopped.
Every {{trigger.call_type}} call still lit her up.
Still made her body say wrong way.

But she'd learned something
her body hadn't caught up to yet:

She could be terrified
and still functional.

She could feel all of it
and still do the job.

One shift, {{partner.name}} looked at her
after a particularly rough one—
kid was fine, but it was close.

"You okay?"

She thought about it.

"No. But I'm here."

That was the difference.

Not okay.
But present.

Not comfortable.
But capable.

The fear was always going to come
with certain calls.
That was just true now.

But she didn't have to let the fear
decide which calls she could take.

She could take them afraid.
And find out afterward
that afraid wasn't the same as unable.

Most of the time,
that was enough.
```

### Validation Notes
- Relational shift: going afraid instead of avoiding
- Lived example: rough call, partner asks, honest answer
- Fear still present — "still lit her up"
- No cure, no permanence
- Resolution level: 3 ✓

---

# SELF-TRUST REPAIR

> **Mechanism Truth:** "I can trust my responses even when they are imperfect."

---

## ST-R-01: Recognition (Self-Trust Repair)

**Template ID:** `emt_st_recognition_second_guessing_v1`
**Content Type:** identity
**Resolution Level:** 0

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{character.years_on_job}}` | Years of service | seven |
| `{{trigger.event}}` | Recent call | the call last week |
| `{{partner.name}}` | Partner's name | Danny |
| `{{body.primary_sensation}}` | Main physical sensation | her confidence crack |

### Template

```
{{character.name}} used to trust her instincts.

{{character.years_on_job}} years of reading patients.
Knowing when something was off before the monitor said so.
Making calls in the field that turned out right.

But since {{trigger.event}},
something had shifted.

She second-guessed everything now.

Did I give the right dose?
Should I have called it sooner?
What if I missed something?

Not just on the hard calls.
On the routine ones too.

Stable patient, obvious presentation,
and still that voice:
Are you sure?

{{partner.name}} hadn't noticed.
Or if he had, he hadn't said anything.

But she noticed.

The hesitation that wasn't there before.
The double-checking that bordered on obsessive.
The way she felt {{body.primary_sensation}}
every time she made a decision.

She wasn't sure if she was being careful
or if she was falling apart.

The line between thoroughness and doubt
had gotten blurry.

And the worst part was,
she couldn't tell if the doubt was right.

Maybe she should trust herself less.
Maybe the confidence before was arrogance.
Maybe this is what careful looks like.

Or maybe she was losing something
she'd spent years building.

And she couldn't tell the difference anymore.
```

### Validation Notes
- Identity anchor: years on job, instincts, professional competence
- Internal stakes: losing trust in self, can't tell the difference
- Somatic activation: confidence cracking
- Doubt established
- No insight, no relief, no resolution
- Resolution level: 0 ✓

---

## ST-MP-01: Mechanism Proof (Self-Trust Repair)

**Template ID:** `emt_st_mechproof_checking_trap_v1`
**Content Type:** constraint
**Resolution Level:** 1

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{partner.name}}` | Partner's name | Danny |

### Template

```
{{character.name}} started checking more.

Double-checking doses.
Triple-checking vitals.
Asking {{partner.name}} to confirm things
she already knew.

She thought if she was careful enough,
she'd catch the mistake before it happened.

But the checking didn't help.

It just gave the doubt more evidence.

Every time she checked,
her brain logged it:
See? You needed to check.
You can't trust yourself.

So she checked more.

And the more she checked,
the less she trusted.
The less she trusted,
the more she needed to check.

A perfect loop
with no exit.

She tried to reason with it.
Your outcomes are good.
Your patients are fine.
You haven't actually made a mistake.

The doubt found exceptions.
What about that time?
What about this one?
You got lucky. That's all.

She tried to fake confidence.
Project certainty.
Act like the person she used to be.

It worked on the outside.
Inside, the doubt got louder.

Because now she was performing trust
instead of feeling it.

And the gap between the two
was exhausting.
```

### Validation Notes
- Constraint loop: checking → more doubt → more checking
- Repeated failure: checking, reasoning, faking — none work
- Pattern language: "every time," "perfect loop"
- No instructions, no solution, no twist
- Resolution level: 1 ✓

---

## ST-TP-01: Turning Point (Self-Trust Repair)

**Template ID:** `emt_st_turning_trained_response_v1`
**Content Type:** reframe
**Resolution Level:** 2

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{character.years_on_job}}` | Years of service | seven |

### Template

```
{{character.name}} was on a call—
routine, nothing special—
when she caught herself double-checking again.

Same dose she'd given a hundred times.
Same patient presentation.
And still that voice: Are you sure?

But this time, instead of checking,
she stopped.

And asked a different question:

What would I have done
before the doubt started?

The answer came immediately.
Push the dose. Move on.

That knowledge hadn't gone anywhere.
It was still in her hands.
Still in her reflexes.
Still in the {{character.years_on_job}} years of training
her body remembered even when her mind forgot.

The doubt was new.
The competence wasn't.

She'd spent years building responses
that didn't require conscious thought.
Pattern recognition.
Muscle memory.
The kind of knowing that lives in the body.

And that training was still there.

Underneath the doubt,
her hands still knew what to do.

The doubt wasn't her instincts failing.
It was her brain adding an extra layer—
a quality-control voice
that had gotten too loud.

She could hear the voice
without letting it override
what her training already knew.

The doubt wasn't evidence of incompetence.
It was just noise.

And underneath the noise,
she was still good at this.
```

### Validation Notes
- Meaning inversion: doubt is noise, not evidence
- Training affirmed, competence still present
- Shows shift through internal realization
- No cure — doubt still present
- Resolution level: 2 ✓

---

## ST-E-01: Embodiment (Self-Trust Repair)

**Template ID:** `emt_st_embodiment_trusting_training_v1`
**Content Type:** integration
**Resolution Level:** 3

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Sarah |
| `{{partner.name}}` | Partner's name | Danny |

### Template

```
The doubt still came.

{{character.name}} didn't expect it to stop.

Some calls, the voice was quiet.
Some calls, it was loud.
It didn't follow rules.

But now, when it showed up—
Are you sure?
What if you're wrong?
Check again.

—she noticed it
without letting it drive.

One shift, high-acuity call,
she made a field decision fast.
The kind that used to be automatic.

The doubt fired immediately:
What if that was wrong?

She felt it.
Let it pass.
Watched her patient stabilize.

After, {{partner.name}} said,
"Good call."

She nodded.

Not because the doubt had stopped.
It was still there, second-guessing.

But underneath it,
her hands had done the right thing.

And maybe that's what trust was now.

Not the absence of doubt.
The willingness to act anyway.

To let her training do its job
even when her brain was noisy.

She wasn't going back
to the easy confidence of before.
That was gone.

But this was something else.
Something harder, maybe.
But still functional.

Trust with the doubt included.

She could live with that.
```

### Validation Notes
- Relational shift: acting despite doubt
- Lived example: fast decision, partner affirms, doubt present
- Doubt still there — "still second-guessing"
- No cure, no return to "before"
- Trust redefined
- Resolution level: 3 ✓

---

# TEMPLATE METADATA SUMMARY

## Variable Registry (EMT Persona)

```yaml
# persona_variables_emt.yaml

character:
  name: "string"           # First name only
  years_on_job: "string"   # Written out (e.g., "seven")
  cert_level: "string"     # EMT-B, Paramedic, etc.

location:
  station: "string"        # "Station 4", "Base 12"
  detail: "string"         # "the rig", "the ambulance bay", "the station"
  hospital: "string"       # "County General", "St. Mary's"
  home: "string"           # "her apartment", "the house"

trigger:
  time: "string"           # "0300", "2 AM"
  event: "string"          # "the code last Tuesday", "the call last week"
  call_type: "string"      # "peds calls", "codes", "overdoses"

body:
  primary_sensation: "string"    # "her hands still buzzing", "her stomach turn"
  secondary_sensation: "string"  # "heart rate up", "hands cold"

partner:
  name: "string"           # Partner's first name
  role: "string"           # "her partner", "her medic"

relationship:
  partner: "string"        # "her husband", "her girlfriend"
  partner_name: "string"   # Optional first name
```

---

*End of EMT Template Library*
