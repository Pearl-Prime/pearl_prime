# Police Officer Template Library

**Persona:** Patrol Officer / Detective (8+ years experience)
**Complete Set:** 4 mechanisms × 4 roles = 16 templates

---

## Persona Context

Law enforcement operates in a distinct first responder context:

- **Hypervigilance:** Constant threat assessment, on and off duty
- **Use of force:** Split-second decisions reviewed for months/years
- **Public scrutiny:** Every action potentially recorded, criticized
- **Unpredictability:** Routine stops can escalate instantly
- **Control orientation:** Training emphasizes command presence
- **Specific triggers:** Domestics, traffic stops, "that call" that changed things
- **Brotherhood/isolation:** Tight bonds with other officers, distance from civilians
- **Administrative burden:** Investigations, reviews, media attention

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

**Template ID:** `police_ar_recognition_off_duty_v1`
**Content Type:** crisis
**Resolution Level:** 0

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{character.years_on_job}}` | Years of service | eleven |
| `{{location.civilian}}` | Civilian location | the grocery store |
| `{{body.primary_sensation}}` | Main physical sensation | his shoulders tighten |
| `{{relationship.partner}}` | Home relationship | his wife |

### Template

```
{{character.name}} couldn't turn it off.

{{character.years_on_job}} years on the job,
and he was still scanning {{location.civilian}}
like it was a traffic stop.

Exits.
Hands.
Who's behind him.
Who's moving too fast.

{{relationship.partner}} noticed.
Said something once about how he never relaxed.
How even at dinner he sat facing the door.

He'd laughed it off.
Old habit.
Occupational hazard.

But lately, it wasn't a habit.
It was a default.

His body didn't know the difference
between a domestic call and a Sunday afternoon.

The alertness that kept him alive at work
was running all the time now.

Standing in line for coffee,
he'd feel {{body.primary_sensation}}.

No threat.
No reason.
Just his system on watch
because that's what it learned to do.

He used to be able to leave it at the precinct.
Clock out, be a civilian, come home.

Now the badge was off
but the radar wasn't.

And he didn't know how to turn it down.
Wasn't even sure he should.

What if the one time he relaxed
was the time something happened?

So he stayed ready.
All the time.
Even when there was nothing to be ready for.

And it was wearing him out.
```

### Validation Notes
- Identity anchor: years on job, scanning behavior, professional identity
- Internal stakes: can't turn off, wearing out, relationship strain
- Somatic activation: shoulders tighten, constant alertness
- No insight, no relief, no resolution
- Resolution level: 0 ✓

---

## AR-MP-01: Mechanism Proof (Autonomic Regulation)

**Template ID:** `police_ar_mechproof_control_trap_v1`
**Content Type:** constraint
**Resolution Level:** 1

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{location.detail}}` | Specific location | his cruiser |

### Template

```
{{character.name}} tried to manage it.

That's what he was trained to do, right?
Assess. Control. Contain.

He tried compartmentalizing.
Work stays at work.
Home stays at home.
Clean lines.

The lines kept bleeding.

He tried exercise.
Burning off the excess energy.
Weights, running, heavy bag.

It helped for an hour.
Then the alertness came back.
Sometimes worse.

He tried the opposite.
Forcing himself to relax.
Deep breaths.
Telling himself to stand down.

His body didn't take orders.
Not about this.

Sitting in {{location.detail}} between calls,
he'd notice his jaw clenched.
Hands gripping the wheel.
Eyes scanning even when parked.

He tried to release it consciously.
Jaw would clench again in minutes.

It was like trying to stay awake by force.
Eventually, the body does what it does.

And his body had decided
that ready was the safest state.

The more he tried to control it,
the more it resisted.

Like it didn't trust him
to know when the threat was real.

So it stayed on
just in case.

And he couldn't argue it down.
```

### Validation Notes
- Constraint loop: trying to control → body resists
- Repeated failure: compartmentalizing, exercise, forcing — none work
- Pattern language: "the more he tried," "didn't take orders"
- No instructions, no solution, no twist
- Resolution level: 1 ✓

---

## AR-TP-01: Turning Point (Autonomic Regulation)

**Template ID:** `police_ar_turning_sentinel_not_malfunction_v1`
**Content Type:** reframe
**Resolution Level:** 2

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{location.detail}}` | Specific location | his backyard |

### Template

```
{{character.name}} was sitting in {{location.detail}},
supposedly relaxing,
when he caught himself scanning the fence line.

No threat.
Kids playing next door.
Nothing but Sunday afternoon.

And still, his eyes tracked movement.
Still, his body stayed ready.

He almost got angry at himself again.
What's wrong with you?
There's nothing here.

But this time, he stopped.

And thought about it differently.

His body wasn't broken.
It was trained.

Trained by hundreds of calls
where the thing that looked routine
suddenly wasn't.

Where the person who seemed calm
had a weapon.

Where the moment you relaxed
was the moment it went sideways.

His nervous system had learned that lesson
perfectly.

Too perfectly, maybe.

But not wrong.

It wasn't malfunctioning.
It was standing sentinel.

Doing exactly what it was built to do
in a job where alertness wasn't optional.

The scanning wasn't a problem.
It was a solution—
to a problem that didn't exist right now.

His system didn't know the difference.
And he couldn't explain it in words.

But maybe he didn't need to fix it.
Maybe he just needed to understand it.

His body was keeping watch.
Not because something was wrong here.
Because keeping watch was how it kept him alive out there.

Trained.
Not broken.

Inconvenient.
Not malfunctioning.
```

### Validation Notes
- Meaning inversion: "sentinel, not malfunction" / "trained, not broken"
- Scanning still happening — no cure
- Understanding, not fixing
- Shows shift through reframe
- Resolution level: 2 ✓

---

## AR-E-01: Embodiment (Autonomic Regulation)

**Template ID:** `police_ar_embodiment_allowing_watch_v1`
**Content Type:** integration
**Resolution Level:** 3

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{relationship.partner}}` | Home relationship | his wife |
| `{{location.civilian}}` | Civilian location | the restaurant |

### Template

```
The scanning didn't stop.

{{character.name}} didn't expect it to.

But now, when he caught himself
tracking exits at {{location.civilian}},
watching hands at the store,
sitting with his back to the wall—

he didn't fight it.

Not because it was comfortable.
Because fighting it made it worse.

His body was going to keep watch.
That was just true now.

The question was whether he could keep watch
without being at war with himself about it.

One night, {{relationship.partner}} noticed him scanning.
Same old pattern.
Eyes on the door.

"You're doing it again."

He nodded.

"I know."

But this time, he wasn't ashamed of it.
Wasn't trying to force himself to stop.

"Force of habit," he said.
And meant it differently now.

The habit was trained.
It was also protective.
It was also exhausting.

All those things could be true.

He still sat facing the door.
But he could have a conversation
while his eyes did their thing.

The sentinel could stand watch
without him being only a sentinel.

He was never going to be the guy
who sat with his back exposed
and didn't notice who walked in.

But he could be the guy
who noticed
and still stayed present.

That was the compromise.
Not peace.
Just coexistence.

For now, that was enough.
```

### Validation Notes
- Relational shift: allowing the watch instead of fighting
- Lived example: restaurant, wife notices, honest response
- Scanning still present — no cure
- "Coexistence, not peace" — honest, not triumphant
- Resolution level: 3 ✓

---

# COGNITIVE DEFUSION

> **Mechanism Truth:** "Thoughts can be present without being obeyed."

---

## CD-R-01: Recognition (Cognitive Defusion)

**Template ID:** `police_cd_recognition_force_replay_v1`
**Content Type:** pattern
**Resolution Level:** 0

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{character.years_on_job}}` | Years of service | eleven |
| `{{trigger.event}}` | Specific incident | the use of force last year |
| `{{body.primary_sensation}}` | Main physical sensation | his jaw clench |

### Template

```
{{character.name}} couldn't stop replaying it.

{{trigger.event}}.

Cleared by the review board.
Justified by every measure.
His partner backed every word.

And still, his brain kept running the tape.

What if you'd waited another second.
What if there was another option.
What if the camera angle made it look—

He knew how it ended.
He was there.
He made the call.

But his mind kept editing.
Looking for the mistake.
The thing he should've seen.
The choice he should've made.

At the precinct, it would start.
Driving home, same loop.
3 AM, awake, same loop.

{{character.years_on_job}} years on the job.
Decisions made in seconds, every shift.
This was one of hundreds.

But this one got stuck.

He felt {{body.primary_sensation}}
every time the loop started again.

He told himself to let it go.
The review is done.
You're cleared.
Move on.

The thoughts didn't move on.

They just kept playing
the same two seconds
from every possible angle.

Looking for the version
where he did something different.
```

### Validation Notes
- Identity anchor: years on job, use of force, cleared but haunted
- Internal stakes: can't let go, 3 AM loops
- Somatic activation: jaw clench
- Pattern established: same loop, every angle
- No insight, no relief, no resolution
- Resolution level: 0 ✓

---

## CD-MP-01: Mechanism Proof (Cognitive Defusion)

**Template ID:** `police_cd_mechproof_justification_trap_v1`
**Content Type:** constraint
**Resolution Level:** 1

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{trigger.event}}` | Specific incident | the incident |

### Template

```
{{character.name}} tried to justify it away.

Listed the factors.
Recited the training.
Rehearsed the timeline.

He was right.
He knew he was right.
The board agreed.
The union agreed.
Everyone agreed.

And still, the thought:
What if you were wrong?

He tried arguing with it.
Building an airtight case.
Evidence, procedure, law.

The thought didn't care about evidence.
It just asked the question again.
What if?

He tried ignoring it.
Shoving it down.
Focusing on the next call.

The thought waited.
Patient.
And came back at 2 AM
when there was nothing else to focus on.

He tried talking about it.
With his partner. With the chaplain.
They said the same things.

It was a good shoot.
You did what you had to do.
Anyone would've made the same call.

For a few hours, that helped.
Then the thought came back:
But what if they're all wrong?

The harder he worked to convince himself,
the more unconvinced he felt.

Like the arguing was evidence
that something needed to be argued about.

He couldn't prove his way to peace.
The case was closed everywhere but his head.

And his head wasn't accepting verdicts.
```

### Validation Notes
- Constraint loop: justifying → more doubt → more justifying
- Repeated failure: arguing, ignoring, talking — none work
- Pattern language: "the thought didn't care," "came back"
- No instructions, no solution, no twist
- Resolution level: 1 ✓

---

## CD-TP-01: Turning Point (Cognitive Defusion)

**Template ID:** `police_cd_turning_review_not_verdict_v1`
**Content Type:** reframe
**Resolution Level:** 2

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{location.detail}}` | Specific location | the locker room |

### Template

```
{{character.name}} was in {{location.detail}}
when the thought came again.

What if you were wrong?

Same question.
Same weight.
Same pull to defend himself.

But this time, he didn't answer.

He thought about review boards.

How they look at everything.
Every angle. Every second.
Slow motion. Enhanced. Analyzed.

And how after all that,
they issue a finding.

His brain was doing the same thing.
Running its own review.
Over and over.

But the brain's review never closed.
Never issued a verdict.
Just kept requesting more evidence.

That's what thoughts do.

They review.
They question.
They run scenarios.

It's not a verdict.
It's just process.

The board had closed the case.
His brain was still in session.

But the brain's session
didn't have the authority
to overturn the actual finding.

It was just running its program.
Question. Review. Repeat.

He could hear the question
without treating it like new evidence.

What if you were wrong?

The thought would keep asking.
That's what thoughts do.

But he didn't have to keep answering.
The case was already closed.

The review in his head
wasn't the same as the verdict in reality.

It was just noise.
Persistent.
But not authoritative.
```

### Validation Notes
- Meaning inversion: "review, not verdict" — thought ≠ authority
- Thought still present — no cure
- Metaphor from his world (review boards)
- Shows shift through changed relationship
- Resolution level: 2 ✓

---

## CD-E-01: Embodiment (Cognitive Defusion)

**Template ID:** `police_cd_embodiment_case_closed_v1`
**Content Type:** integration
**Resolution Level:** 3

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{partner.name}}` | Work partner | Torres |
| `{{trigger.event}}` | The incident | the shooting |

### Template

```
The thought still came.

{{character.name}} didn't expect it to stop.

Some nights, the loop was loud.
Some nights, barely there.
It didn't follow a schedule.

But now, when it started—
What if you were wrong?
What if there was another way?
What if, what if, what if.

—he recognized it.

Oh. Review board's in session again.

Not dismissing it.
Not arguing with it.
Just noting that his brain
was doing its thing.

One shift, {{partner.name}} mentioned {{trigger.event}}.
Something about the report.
Paperwork.

And the thought fired immediately:
Your fault.

{{character.name}} felt it land.
Felt the pull to defend, explain, relitigate.

And then let it pass.

Not because it was wrong.
Not because it was right.

Because the actual verdict was already in.
And his brain's ongoing review
didn't have the authority
to change it.

The thought could keep asking.
That was fine.

He just didn't have to keep testifying.

The case was closed.

His brain could keep the file open
if it wanted to.
He didn't have to sit in the hearing room
every time it scheduled a session.

He could note the meeting request
and decline to attend.

Most of the time now,
that's what he did.
```

### Validation Notes
- Relational shift: noting without engaging
- Lived example: partner mentions it, thought fires, lets it pass
- Thought still present — "still came"
- Metaphor extended (meeting request, decline to attend)
- Resolution level: 3 ✓

---

# EXPOSURE TOLERANCE

> **Mechanism Truth:** "Discomfort can be survived without avoidance."

---

## ET-R-01: Recognition (Exposure Tolerance)

**Template ID:** `police_et_recognition_domestics_avoidance_v1`
**Content Type:** pattern
**Resolution Level:** 0

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{character.years_on_job}}` | Years of service | eleven |
| `{{trigger.call_type}}` | Avoided call type | domestics |
| `{{body.primary_sensation}}` | Main physical sensation | his stomach drop |

### Template

```
{{character.name}} used to take {{trigger.call_type}} like any other call.

Part of the job.
Unpredictable, sure.
But manageable.

That was before.

Now, every time dispatch called out a domestic,
he felt {{body.primary_sensation}}.

Not caution.
Something deeper.
Something that said: not this one.

He started doing things he wouldn't have done before.

Taking longer to clear the previous call.
Letting another unit grab it if they were closer.
Finding reasons to be unavailable.

Nothing obvious.
Nothing anyone would call him on.

Just... managing.

The other officers didn't notice.
Or if they did, they understood.
Everyone had their thing.

But {{character.name}} noticed.

The list of calls he'd rather not take
was getting longer.

The window of situations he felt steady in
was getting smaller.

{{character.years_on_job}} years in,
and he was building his shifts
around avoiding what scared him.

And the worst part—
the part he wouldn't admit—

was that the avoiding wasn't making it better.

Every domestic he dodged
made the next one loom larger.

The fear was winning
by inches.
```

### Validation Notes
- Identity anchor: years on job, professional competence eroding
- Internal stakes: world shrinking, fear winning
- Somatic activation: stomach drop
- Pattern established: avoiding → worse
- No insight, no relief, no resolution
- Resolution level: 0 ✓

---

## ET-MP-01: Mechanism Proof (Exposure Tolerance)

**Template ID:** `police_et_mechproof_dodge_loop_v1`
**Content Type:** constraint
**Resolution Level:** 1

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{trigger.call_type}}` | Avoided call type | domestics |

### Template

```
Every time {{character.name}} dodged a {{trigger.call_type}},
he felt relief.

Not this time.
Someone else got it.
Thank god.

And that relief was the trap.

His brain logged it:
Avoiding = feeling better.
Avoiding = safe.

So he avoided more.

And every time he avoided,
the relief came faster.
And the dread before came harder.

A perfect system
designed to shrink his world.

He tried reasoning with himself.
You've handled hundreds of these.
Nothing's happened.
You're being irrational.

His body didn't speak rational.
It only knew what worked last time.
And last time, dodging worked.

He tried to force himself once.
Took a domestic he would've let slide.
Stayed professional. Got through it.

But his hands shook for an hour after.
And the next one was worse.

Because now his body knew
he might override it.
So the alarm got louder.

He couldn't think his way out.
Couldn't force his way through.
The only thing that worked was avoiding.

And avoiding was slowly turning him
into the cop who couldn't handle a domestic.

{{character.years_on_job}} years.
Commendations on the wall.
And this is what was getting him.

Not the big stuff.
The thing he couldn't face.
```

### Validation Notes
- Constraint loop: avoiding → relief → more avoidance
- Repeated failure: logic, forcing — none work
- Pattern language: "every time," "perfect system"
- No instructions, no solution, no twist
- Resolution level: 1 ✓

---

## ET-TP-01: Turning Point (Exposure Tolerance)

**Template ID:** `police_et_turning_through_the_door_v1`
**Content Type:** reframe
**Resolution Level:** 2

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{trigger.call_type}}` | Call type | domestic |
| `{{partner.name}}` | Partner's name | Torres |

### Template

```
The call came in.
{{trigger.call_type}}.
No way to pass it off.

{{character.name}}'s body did what it always did.
Stomach dropped.
Heart rate spiked.
Every cell saying: don't go in there.

He went in.

Not because he was ready.
Not because the fear had stopped.

Because {{partner.name}} was already moving
and there was no other option.

In the doorway, his body was screaming.
He ignored it.
Did the job.
Separated the parties.
Took the statements.

The whole time, the alarm blaring inside.

And when it was over—
nothing.

No one got hurt.
Standard call.
Paperwork and drive away.

But something had shifted.

He'd felt the full force of the dread
and kept moving anyway.

Not around it.
Through it.

The fear hadn't stopped him.
He'd stopped letting it stop him.

Just this once.
Just this door.

But that was something.

He'd been so sure
that feeling that afraid meant he couldn't function.

Turns out,
he could feel all of it
and still walk through the door.

Terrible.
But possible.
```

### Validation Notes
- Meaning inversion: "through, not around"
- Fear still present — no cure
- Shows action despite dread
- "Terrible. But possible."
- Resolution level: 2 ✓

---

## ET-E-01: Embodiment (Exposure Tolerance)

**Template ID:** `police_et_embodiment_walking_in_v1`
**Content Type:** integration
**Resolution Level:** 3

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{trigger.call_type}}` | Call type | domestics |
| `{{partner.name}}` | Partner's name | Torres |

### Template

```
{{character.name}} stopped dodging.

Not all at once.
Not perfectly.

Some days the dread won.
Some days he let another unit take it.

But more often now,
when dispatch called a {{trigger.call_type}},
he took it.

Not because the fear stopped.
Every time, his body still said don't.

But he'd learned something
his body hadn't caught up to yet:

The dread was not a prediction.
It was just a feeling.
And he could feel it
and still function.

One call, bad one,
shouting and broken glass and a kid crying.

{{partner.name}} glanced at him after.
"You good?"

{{character.name}} took a second.

"No. But I'm here."

That was the new normal.

Not comfortable.
Not fixed.

Just willing to be uncomfortable
and still do the job.

The calls still lit him up.
He stopped expecting that to change.

But he could walk through the door
with the alarm blaring
and still be a cop on the other side.

Not the cop he used to be.
The one who didn't feel this.

But a cop who could feel all of it
and still show up.

Some days that was barely enough.
Some days it was more than he expected.

Either way,
he was still walking through doors.

And that counted for something.
```

### Validation Notes
- Relational shift: going despite fear, not waiting for fear to stop
- Lived example: bad call, partner asks, honest answer
- Fear still present — "still lit him up"
- "Not the cop he used to be" — honest
- Resolution level: 3 ✓

---

# SELF-TRUST REPAIR

> **Mechanism Truth:** "I can trust my responses even when they are imperfect."

---

## ST-R-01: Recognition (Self-Trust Repair)

**Template ID:** `police_st_recognition_split_second_doubt_v1`
**Content Type:** identity
**Resolution Level:** 0

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{character.years_on_job}}` | Years of service | eleven |
| `{{trigger.event}}` | Triggering incident | the traffic stop last month |
| `{{body.primary_sensation}}` | Main physical sensation | his confidence crack |

### Template

```
{{character.name}} used to trust his instincts.

{{character.years_on_job}} years of split-second decisions.
Reading situations.
Knowing when to push, when to back off.
Lives depending on his judgment.

He'd earned that trust.

But since {{trigger.event}},
something had shifted.

Everything felt slower now.
Heavier.

Situations that used to be automatic
now had a pause in them.

Is this right?
Am I sure?
What if I'm wrong?

Not careful.
Paralyzed.

He felt {{body.primary_sensation}}
every time he had to make a call.

The other officers didn't notice.
He was still professional.
Still competent.

But inside, the foundation was shaking.

He couldn't tell anymore
if his hesitation was wisdom
or fear.

If questioning himself was growth
or erosion.

What if the guy I was before was right?
What if the guy I am now can't do this?

He didn't know which version to trust.

So he trusted neither.

Just moved through shifts
waiting to find out
which one would show up
when it mattered.
```

### Validation Notes
- Identity anchor: years on job, split-second decisions, professional identity
- Internal stakes: can't trust himself, waiting to fail
- Somatic: confidence cracking
- Doubt established, no resolution
- Resolution level: 0 ✓

---

## ST-MP-01: Mechanism Proof (Self-Trust Repair)

**Template ID:** `police_st_mechproof_hesitation_trap_v1`
**Content Type:** constraint
**Resolution Level:** 1

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{partner.name}}` | Partner's name | Torres |

### Template

```
{{character.name}} tried to earn back the trust.

Ran scenarios in his head.
What would I do if—
How would I respond to—
What's the right call when—

The preparation didn't help.

Real situations didn't follow the script.
And every scenario just reminded him
of how many ways things could go wrong.

He tried to study his way back.
Reread use-of-force guidelines.
Reviewed case law.
Memorized decision trees.

His brain filed it all away
and still froze in the moment.

He tried to watch himself.
Monitor every decision.
Looking for the hesitation,
the error, the sign of failure.

But the watching made it worse.

The more he scrutinized,
the more uncertain he felt.
Like the attention itself
was manufacturing doubt.

{{partner.name}} didn't say anything.
But {{character.name}} caught the looks sometimes.
The slight pause.
Waiting to see what he'd do.

Or maybe that was in his head too.
He couldn't tell anymore
what was real concern
and what was his own doubt
reflected back at him.

He was trying to think his way to confidence.
And thinking was exactly what was breaking it.
```

### Validation Notes
- Constraint loop: monitoring → more doubt → more monitoring
- Repeated failure: preparation, studying, watching — none work
- Pattern language: "didn't help," "made it worse"
- No instructions, no solution, no twist
- Resolution level: 1 ✓

---

## ST-TP-01: Turning Point (Self-Trust Repair)

**Template ID:** `police_st_turning_trained_not_frozen_v1`
**Content Type:** reframe
**Resolution Level:** 2

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{character.years_on_job}}` | Years of service | eleven |

### Template

```
{{character.name}} was on a call—
nothing major, dispute at a bar—
when he noticed himself hesitating again.

That half-second pause.
The one that felt like failure.

But this time, he paid attention to what happened next.

His body still moved.
Positioned right.
Voice steady.
De-escalation working
before his conscious mind caught up.

The hesitation didn't stop him.
The training carried him through it.

And he realized something.

The doubt was new.
The competence wasn't.

{{character.years_on_job}} years of experience
lived in his body.
In his positioning.
In his tone.
In responses that happened
before he had time to question them.

The hesitation was his brain
adding a layer of review
on top of what his training already knew.

The training wasn't broken.
The confidence was just... louder about checking.

He could feel uncertain
and still be effective.

The doubt and the competence
could exist in the same moment.

One was a feeling.
The other was a skill.

And the skill was still there.
Underneath the noise.
Working.

Even when he wasn't sure it would.
```

### Validation Notes
- Meaning inversion: doubt ≠ incompetence; skill still there
- Training carries through despite hesitation
- Shows shift through observation of self
- No cure — doubt still present
- Resolution level: 2 ✓

---

## ST-E-01: Embodiment (Self-Trust Repair)

**Template ID:** `police_st_embodiment_doubt_and_duty_v1`
**Content Type:** integration
**Resolution Level:** 3

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Marcus |
| `{{partner.name}}` | Partner's name | Torres |

### Template

```
The doubt still came.

{{character.name}} didn't expect it to stop.

Some calls, the hesitation was barely there.
Some calls, it was loud.

But now, when it showed up—
Are you sure?
What if you're wrong?
—he didn't let it drive.

He just noted it.

Oh. The review board again.

And let his training take the wheel.

One night, call went sideways fast.
Situation changed in a second.
He had to decide.

The doubt was there.
Loud.
What if—

But his body was already moving.
Doing what it was trained to do.

Afterward, {{partner.name}} nodded.
"Good call."

{{character.name}} felt the doubt still buzzing.
Even after it worked.
Even after it was over.

What if you got lucky?

He let it talk.

Maybe he did get lucky.
Or maybe his training worked.
He couldn't know for certain.

But he could trust the training
even when his brain wanted more proof.

That was the deal now.

Not confidence like before.
Not certainty.

Just willingness to act
while uncertain.

To trust the {{character.years_on_job}} years
even when his brain was noisy.

Some days it felt like barely enough.

Most days, it was enough.

And that was the version of trust
he could actually live with.
```

### Validation Notes
- Relational shift: trusting training despite doubt
- Lived example: call goes sideways, partner affirms, doubt still present
- Doubt still there — "still buzzing"
- No return to old confidence
- Trust redefined
- Resolution level: 3 ✓

---

# TEMPLATE METADATA SUMMARY

## Variable Registry (Police Officer Persona)

```yaml
# persona_variables_police.yaml

character:
  name: "string"           # First name only
  years_on_job: "string"   # Written out (e.g., "eleven")
  rank: "string"           # Officer, Sergeant, Detective

location:
  precinct: "string"       # "the 14th", "Central Division"
  detail: "string"         # "his cruiser", "the locker room", "the backyard"
  civilian: "string"       # "the grocery store", "the restaurant"

trigger:
  time: "string"           # "0200", "3 AM"
  event: "string"          # "the use of force last year", "the traffic stop"
  call_type: "string"      # "domestics", "traffic stops"

body:
  primary_sensation: "string"    # "his shoulders tighten", "his stomach drop"
  secondary_sensation: "string"  # "heart rate spike", "jaw clench"

partner:
  name: "string"           # Work partner's name
  role: "string"           # "his partner", "his sergeant"

relationship:
  partner: "string"        # "his wife", "his husband"
  partner_name: "string"   # Optional first name
```

---

*End of Police Officer Template Library*
