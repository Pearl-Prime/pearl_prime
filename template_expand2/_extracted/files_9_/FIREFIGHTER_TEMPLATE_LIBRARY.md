# Firefighter Template Library

**Persona:** Career Firefighter (10+ years experience)
**Complete Set:** 4 mechanisms × 4 roles = 16 templates

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

**Template ID:** `firefighter_ar_recognition_false_alarm_v1`
**Content Type:** crisis
**Resolution Level:** 0

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{character.years_on_job}}` | Years of service | twelve |
| `{{location.station}}` | Station identifier | Station 7 |
| `{{trigger.time}}` | Time of incident | 3 AM |
| `{{body.primary_sensation}}` | Main physical sensation | chest lock up |

### Template

```
{{character.name}} had been on the job {{character.years_on_job}} years.

Long enough to trust his instincts.
Long enough to know the difference between a real call and a drill.

But lately, his body wasn't getting the memo.

The tones dropped at {{trigger.time}}.
Routine medical.
Nothing that should've made his {{body.primary_sensation}}.

He pulled on his gear the same way he always did.
Checked the rig.
But something in his chest was already running ahead.

By the time they rolled out, his hands were steady—
but his pulse was telling a different story.

The call was nothing.
False alarm, basically.
The patient was fine before they even arrived.

And still, driving back to {{location.station}},
he couldn't shake it.

That hum in his body that said something's wrong
even when nothing was.

He'd trained for years to trust that signal.
Now it was firing when there was nothing to fight.

And that—
that was the part he couldn't tell anyone.
```

### Validation Notes
- Identity anchor: years on job, station, professional competence
- Internal stakes: can't trust his body, isolation ("couldn't tell anyone")
- Somatic activation: chest, pulse, "hum in his body"
- No insight, no relief, no resolution
- Resolution level: 0 ✓

---

## AR-MP-01: Mechanism Proof (Autonomic Regulation)

**Template ID:** `firefighter_ar_mechproof_analysis_trap_v1`
**Content Type:** constraint
**Resolution Level:** 1

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{location.detail}}` | Specific location | apparatus bay |

### Template

```
{{character.name}} tried to figure it out.

That's what you do, right?
Something's off, you diagnose.
Find the source. Fix it.

He ran through the call again.
Nothing dangerous.
Nothing he hadn't handled a hundred times.

So why was his body still running hot?

He thought maybe it was sleep.
Cut back on coffee.
Tried to get to bed earlier.

The next shift, same thing.
Tones dropped for a structure fire—
real this time—
and his body responded the way it was supposed to.

But the medical call after?
Routine.
And there it was again.

That hum.
That readiness with nowhere to go.

He tried breathing slower.
Telling himself to relax.
Walking it off in the {{location.detail}}.

None of it worked.

Because he was trying to think his way out of something
that wasn't a thinking problem.

The more he analyzed,
the more his body stayed on alert.

Scanning for the threat he couldn't find.
```

### Validation Notes
- Constraint loop: thinking → more alert → more thinking
- Repeated failure: sleep, coffee, breathing, walking — none work
- Pattern language: "same thing," "there it was again"
- No instructions, no solution, no twist
- Resolution level: 1 ✓

---

## AR-TP-01: Turning Point (Autonomic Regulation)

**Template ID:** `firefighter_ar_turning_signal_not_command_v1`
**Content Type:** reframe
**Resolution Level:** 2

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{location.detail}}` | Specific location | apparatus bay |

### Template

```
{{character.name}} stood in the {{location.detail}} longer than usual.

Didn't rush.
Didn't check the board.
Didn't do anything, really.

Just stood there.

The alarm had already passed.
The call was hours ago.
But his body was still holding on.

He noticed it—
chest still braced,
shoulders still up,
breath still shallow.

Not because something was wrong.
Because his system was still on watch.

He didn't try to fix it.
Didn't tell himself to calm down.
Just noticed.

And somewhere in that noticing,
something shifted.

Not dramatic.
Just quieter.

Breath came a little lower.
Shoulders dropped without instruction.

The alarm wasn't gone.
But it wasn't running the show anymore.

It was a signal.
Not a command.

His body had been doing its job—
keeping him ready,
keeping him sharp.

It wasn't broken.
It was trained.

And maybe—
maybe he didn't need to stop the alarm.

Maybe he just needed to land after it passed.
```

### Validation Notes
- Meaning inversion: "signal, not a command"
- Supporting reframe: "trained, not broken"
- Shows shift through body, not explanation
- "Maybe" maintains appropriate tentativeness
- No cure, no permanence, no mastery
- Resolution level: 2 ✓

---

## AR-E-01: Embodiment (Autonomic Regulation)

**Template ID:** `firefighter_ar_embodiment_landing_v1`
**Content Type:** integration
**Resolution Level:** 3

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{location.station}}` | Station identifier | Station 7 |
| `{{relationship.partner}}` | Home relationship | his wife |

### Template

```
The next time it happened,
{{character.name}} didn't fight it.

Tones dropped.
Routine call.
Body lit up anyway.

He let it.

On the way back to {{location.station}},
he noticed his grip on the wheel—
tight, like he was still bracing.

He didn't tell himself to relax.
Didn't analyze why.

Just noticed.

And let his hands soften when they were ready.

It wasn't instant.
Took a few minutes.
Maybe longer.

But somewhere between the call and the station,
his body found its own way down.

Not because the alarm stopped.
It was still there, humming low.

But he wasn't trying to silence it anymore.

He was just letting it run its course.

The way a siren fades after the rig passes.

Still there.
Just not in charge.

That night, {{relationship.partner}} asked how his shift was.

He said, "Quiet."

And for the first time in a while,
that was actually true.
```

### Validation Notes
- Relational shift: not fighting, letting it run its course
- Lived example: specific scene, specific actions
- Grounded presence: hands on wheel, body finding its way down
- Alarm still present ("humming low") — no cure
- "Quiet" is earned, not promised
- Resolution level: 3 ✓

---

# COGNITIVE DEFUSION

> **Mechanism Truth:** "Thoughts can be present without being obeyed."

---

## CD-R-01: Recognition (Cognitive Defusion)

**Template ID:** `firefighter_cd_recognition_replay_loop_v1`
**Content Type:** pattern
**Resolution Level:** 0

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{character.years_on_job}}` | Years of service | twelve |
| `{{trigger.event}}` | Specific incident | the warehouse fire |
| `{{trigger.time}}` | When it happened | three months ago |
| `{{location.home_detail}}` | Home setting | kitchen table |

### Template

```
{{character.name}} couldn't stop replaying it.

{{trigger.event}}.
{{trigger.time}}.
Everyone got out fine.

But his mind kept going back.

What if the floor had given way sooner.
What if the rookie had been two steps to the left.
What if he'd missed the signs.

He knew how the call actually ended.
He'd been there.
He'd walked out.

But his thoughts kept writing different endings.

Worse ones.

At the {{location.home_detail}}, staring at nothing.
In the rig, waiting for the next call.
At 2 AM, awake again.

The same loop.
The same what-ifs.
The same tightness in his chest
every time his brain ran the scenario one more time.

He told himself to stop.
To think about something else.
To let it go.

But the thoughts didn't listen.

They just kept coming.
Loud.
Insistent.
Like they had something important to say—
something he hadn't figured out yet.

And maybe if he just thought about it enough,
he'd finally understand.

But {{character.years_on_job}} years in,
and he still couldn't think his way to quiet.
```

### Validation Notes
- Identity anchor: years on job, specific incident, professional context
- Internal stakes: can't stop the loop, can't find quiet
- Somatic activation: tightness in chest
- Pattern established: same loop, same what-ifs
- No insight, no relief, no resolution
- Resolution level: 0 ✓

---

## CD-MP-01: Mechanism Proof (Cognitive Defusion)

**Template ID:** `firefighter_cd_mechproof_engagement_trap_v1`
**Content Type:** constraint
**Resolution Level:** 1

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{trigger.event}}` | Specific incident | the warehouse fire |

### Template

```
{{character.name}} tried to argue with the thoughts.

They'd say: You should've seen it sooner.
He'd counter: I did everything right.

They'd say: Someone could've died.
He'd counter: But no one did.

Back and forth.
Like a debate he couldn't win
because the other side didn't play fair.

He tried ignoring them.
Pushing them away.
Focusing on the TV, the workout, the next call.

The thoughts waited.
Patient.
And came back louder.

He tried analyzing them.
Where did this start?
What's the root cause?
What does this say about me?

That just gave them more material.

He tried reassuring himself.
Listing all the reasons he was good at his job.
All the calls that went right.

The thoughts found exceptions.
Every time.

The harder he pushed,
the harder they pushed back.

It was like arm-wrestling something with no arms.
No matter how much force he used,
there was nothing to beat.

Just a voice in his head
that wouldn't stop talking
no matter how many times he answered.
```

### Validation Notes
- Constraint loop: engaging thoughts → thoughts get louder
- Repeated failure: arguing, ignoring, analyzing, reassuring — none work
- Pattern language: "back and forth," "every time"
- No instructions, no solution, no twist
- Resolution level: 1 ✓

---

## CD-TP-01: Turning Point (Cognitive Defusion)

**Template ID:** `firefighter_cd_turning_weather_not_orders_v1`
**Content Type:** reframe
**Resolution Level:** 2

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{location.detail}}` | Specific location | back of the rig |

### Template

```
{{character.name}} was sitting in the {{location.detail}}
when the thought came again.

You missed something.

Same voice.
Same certainty.
Same pull to engage.

But this time, he didn't answer.

Not because he was ignoring it.
Not because he was pushing it away.

He just... noticed it.

Like noticing the weather.

Rain doesn't need a response.
You don't argue with clouds.
You don't try to convince the wind to stop.

You just notice it's there.

The thought was still talking.
You missed something.
You should've seen it.

But he wasn't listening the same way anymore.

It wasn't an order.
It was just noise.

His brain doing what brains do—
running scenarios,
looking for threats,
trying to keep him safe
in the only way it knew how.

The thought didn't stop.

But he stopped treating it like it knew something he didn't.

It was weather.
Not orders.

And he didn't have to stand in the rain
just because it was falling.
```

### Validation Notes
- Meaning inversion: "weather, not orders"
- Shows the shift through changed relationship, not suppression
- Thought still present — no cure
- Insight feels discovered ("Like noticing the weather")
- No permanence, no mastery
- Resolution level: 2 ✓

---

## CD-E-01: Embodiment (Cognitive Defusion)

**Template ID:** `firefighter_cd_embodiment_letting_pass_v1`
**Content Type:** integration
**Resolution Level:** 3

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{colleague.name}}` | Colleague name | Martinez |
| `{{location.station}}` | Station identifier | Station 7 |

### Template

```
The thoughts still came.

{{character.name}} didn't expect them to stop.

But now, when the loop started—
You should've seen it.
What if you'd missed it.
Someone could've died.

—he didn't climb in.

He just noticed.

Oh. That one again.

Not dismissing it.
Not fighting it.
Just recognizing the shape of it.

The way you recognize a regular at the station
without having to stop and talk every time.

Some days it was loud.
Some days he barely noticed.

It didn't follow rules.
Didn't care if he was tired
or focused
or finally feeling okay.

It just showed up when it showed up.

And he let it.

One shift, {{colleague.name}} said something about the call—
the old one, {{trigger.event}}—
and the thought fired immediately.

Your fault.

{{character.name}} felt it land.
Felt the pull to defend, explain, argue.

And then let it pass.

Not because it was wrong.
Not because it was right.

Because it was just a thought.

And thoughts don't need answers.

They just need room to move through.
```

### Validation Notes
- Relational shift: noticing without engaging
- Lived example: colleague triggers thought, he lets it pass
- Thoughts still present — "still came," "fired immediately"
- No cure, no permanence
- Grounded in real interaction
- Resolution level: 3 ✓

---

# EXPOSURE TOLERANCE

> **Mechanism Truth:** "Discomfort can be survived without avoidance."

---

## ET-R-01: Recognition (Exposure Tolerance)

**Template ID:** `firefighter_et_recognition_avoidance_cost_v1`
**Content Type:** pattern
**Resolution Level:** 0

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{character.years_on_job}}` | Years of service | twelve |
| `{{trigger.situation}}` | Avoided situation | high-rise calls |
| `{{location.station}}` | Station identifier | Station 7 |
| `{{body.primary_sensation}}` | Main physical sensation | his stomach drop |

### Template

```
{{character.name}} started trading shifts.

Nothing obvious.
Just small adjustments.
A favor here, a swap there.

If the schedule put him on {{trigger.situation}},
he'd find a way out of it.

Not every time.
Just enough.

He told himself it was logistics.
Family stuff.
Timing.

But he knew.

Every time the dispatch came through for a {{trigger.situation}},
he felt {{body.primary_sensation}}.

Not fear exactly.
Something lower.
Something that said: not today.

And the more he listened to it,
the more it talked.

What started as occasional
became regular.

What started as preference
became necessity.

{{character.years_on_job}} years on the job,
and he was managing his schedule
around something he couldn't name.

The guys at {{location.station}} didn't notice.
Or if they did, they didn't say.

But he noticed.

The shrinking.
The planning.
The way his world got a little smaller
every time he said not that one.

And the worst part—
the part that kept him up—

was that the avoiding didn't make it better.

It just made the next one worse.
```

### Validation Notes
- Identity anchor: years on job, station, professional identity
- Internal stakes: world shrinking, isolation, competence at risk
- Somatic activation: stomach drop
- Pattern established: avoiding → worse
- No insight, no relief, no resolution
- Resolution level: 0 ✓

---

## ET-MP-01: Mechanism Proof (Exposure Tolerance)

**Template ID:** `firefighter_et_mechproof_avoidance_loop_v1`
**Content Type:** constraint
**Resolution Level:** 1

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{trigger.situation}}` | Avoided situation | high-rise calls |

### Template

```
Every time {{character.name}} avoided a {{trigger.situation}},
he felt relief.

Real relief.
The kind that floods through your whole body.

Thank god. Not today.

And that was the problem.

The relief taught him something:
avoiding works.

So he avoided more.

And every time he avoided,
the relief came faster.

And the dread before came harder.

It was a perfect system
designed to make him smaller.

He tried to talk himself through it.
It's just a building.
You've done this before.
Nothing bad actually happened.

His body didn't care about logic.
It only knew what worked last time.

And last time, avoiding worked.

He tried pushing through once.
White-knuckled it.
Got through the call.

But the next one was worse.
Because now his body knew
he might force it,
so the alarm got louder.

Escape didn't work.
Fighting didn't work.
The only thing that worked was avoiding—
and avoiding was slowly erasing him.

A firefighter who couldn't do the job.

That's what he was becoming.
And he couldn't think his way out of it.
```

### Validation Notes
- Constraint loop: avoiding → relief → more avoidance → louder alarm
- Repeated failure: logic, pushing through — none work
- Pattern language: "every time," "perfect system"
- No instructions, no solution, no twist
- Resolution level: 1 ✓

---

## ET-TP-01: Turning Point (Exposure Tolerance)

**Template ID:** `firefighter_et_turning_survive_not_escape_v1`
**Content Type:** reframe
**Resolution Level:** 2

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{trigger.situation}}` | Avoided situation | high-rise |
| `{{location.detail}}` | Specific location | stairwell |

### Template

```
The call came in.
{{trigger.situation}}.
No way to trade out.

{{character.name}}'s body did what it always did.
Stomach dropped.
Chest tightened.
Every cell saying: get out.

He didn't get out.

Not because he was brave.
Not because he'd conquered anything.

Just because there was nowhere to go.

So he went.

In the {{location.detail}}, climbing,
his body screaming the whole way.

And somewhere around the eighth floor,
something strange happened.

The alarm was still there.
Loud as ever.

But he was still climbing.

Not fighting it.
Not ignoring it.
Just... moving with it.

The dread didn't disappear.
But it also didn't kill him.

He reached the top.
Did his job.
Body still buzzing.

And on the way down,
a thought he'd never had before:

I didn't escape it.
I survived it.

The alarm wasn't a prediction.
It was just noise.

Noise he could carry
and still keep moving.

Not comfortable.
Not easy.

But possible.

And possible was something he hadn't felt in a long time.
```

### Validation Notes
- Meaning inversion: "survived, not escaped"
- Alarm still present — no cure
- Shows the shift through action and changed interpretation
- "Possible" — tentative, not triumphant
- No permanence, no mastery
- Resolution level: 2 ✓

---

## ET-E-01: Embodiment (Exposure Tolerance)

**Template ID:** `firefighter_et_embodiment_carrying_it_v1`
**Content Type:** integration
**Resolution Level:** 3

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{trigger.situation}}` | Situation type | high-rise |
| `{{colleague.name}}` | Colleague name | Martinez |

### Template

```
{{character.name}} stopped trading shifts.

Not all at once.
Not perfectly.

Some days the dread won.
Some days he said not today
and meant it.

But more often now,
he went anyway.

Not because the fear stopped.
It didn't.

Every {{trigger.situation}} still lit him up.
Still made his body say wrong way.

But he'd learned something
his body hadn't caught up to yet:

The alarm could be loud
and he could still move.

The discomfort could be real
and he could still function.

He wasn't comfortable.
Wasn't "over it."

He was just willing to be uncomfortable
and do the job anyway.

{{colleague.name}} noticed.
Said something one day in the rig.

"Thought you hated these calls."

{{character.name}} shrugged.

"Still do."

But he was there.
Climbing the stairs with his stomach in his throat.
Doing the thing that scared him
because the alternative scared him more.

Not shrinking.
Not expanding either.

Just holding the line.

And some days, that was enough.
```

### Validation Notes
- Relational shift: going anyway, carrying discomfort
- Lived example: colleague notices, real interaction
- Fear still present — "still lit him up"
- No cure, no permanence ("some days that was enough")
- Grounded in ongoing reality
- Resolution level: 3 ✓

---

# SELF-TRUST REPAIR

> **Mechanism Truth:** "I can trust my responses even when they are imperfect."

---

## ST-R-01: Recognition (Self-Trust Repair)

**Template ID:** `firefighter_st_recognition_broken_signal_v1`
**Content Type:** identity
**Resolution Level:** 0

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{character.years_on_job}}` | Years of service | twelve |
| `{{trigger.event}}` | Incident type | the call last month |
| `{{location.station}}` | Station identifier | Station 7 |
| `{{body.primary_sensation}}` | Main physical sensation | hands shake |

### Template

```
{{character.name}} used to trust himself.

{{character.years_on_job}} years of calls.
Hundreds of decisions made in seconds.
Lives depending on his judgment.

He'd earned that trust.

But since {{trigger.event}},
something was different.

His {{body.primary_sensation}} sometimes.
Not during calls—
he was still solid when it counted.

But after.
Or before.
Or in the middle of nothing at all.

His body would react
and he wouldn't know why.

And that not knowing
was eroding something he'd built over years.

At {{location.station}}, he was still the guy
everyone counted on.

But inside, he wasn't sure anymore.

Can I trust this?
Can I trust me?

Every unexpected reaction felt like evidence.
Evidence that something was wrong.
That he was broken somehow.
That the guy who used to be steady
was coming apart at the seams.

He didn't tell anyone.
What would he say?

I don't trust my own body anymore.

That's not something you admit.
Not in this job.
Not when people depend on you.

So he carried it alone.
The doubt.
The watching himself.
The waiting for the next sign
that he wasn't who he used to be.
```

### Validation Notes
- Identity anchor: years on job, professional trust, station
- Internal stakes: losing trust in himself, isolation
- Somatic activation: hands shaking, unexpected reactions
- Doubt established, no resolution
- No insight, no relief
- Resolution level: 0 ✓

---

## ST-MP-01: Mechanism Proof (Self-Trust Repair)

**Template ID:** `firefighter_st_mechproof_monitoring_trap_v1`
**Content Type:** constraint
**Resolution Level:** 1

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{body.primary_sensation}}` | Main physical sensation | hands shake |

### Template

```
{{character.name}} started watching himself.

Every shift.
Every call.
Every quiet moment in between.

Checking: Am I okay?
Checking: Is this normal?
Checking: Did that reaction mean something?

He thought if he monitored closely enough,
he'd catch the problem before it got worse.

But the watching made it worse.

Every time he noticed his {{body.primary_sensation}},
he catalogued it.
Evidence.

Every time his heart beat faster than expected,
he noted it.
More evidence.

He was building a case against himself
one observation at a time.

And the more he watched,
the more he found.

Because bodies do things.
Random things.
Things that mean nothing
until you decide they mean everything.

He tried to control it.
Manage his breathing.
Stay calm.
Project steady.

But you can't control your way to trust.
You just get more rigid.
More careful.
More convinced that something's wrong.

The monitoring was supposed to help.
It was supposed to catch the break before it happened.

Instead, it just reminded him—
constantly—
that he was waiting for himself to fail.
```

### Validation Notes
- Constraint loop: monitoring → finding "evidence" → more monitoring
- Repeated failure: watching, controlling, managing — none work
- Pattern language: "every time," "more evidence"
- No instructions, no solution, no twist
- Resolution level: 1 ✓

---

## ST-TP-01: Turning Point (Self-Trust Repair)

**Template ID:** `firefighter_st_turning_protection_not_malfunction_v1`
**Content Type:** reframe
**Resolution Level:** 2

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{trigger.event}}` | Recent incident | the call last week |

### Template

```
{{character.name}} was in the bay
when his hands started shaking again.

No reason.
No call coming in.
Just standing there.

And instead of the usual—
What's wrong with me?
Why is this happening?
—he just looked at them.

Shaking.
Not dangerous.
Just... activated.

And for the first time, he wondered:

What if this isn't broken?

What if his body was doing exactly what it was built to do?

He'd spent {{character.years_on_job}} years in situations
where hyper-vigilance kept him alive.

Where reading danger before it arrived
meant everyone went home.

His body had learned that lesson perfectly.

Too perfectly, maybe.

But not wrong.

Not malfunction.
Protection.

A system that learned to stay ready
because staying ready worked.

It wasn't betraying him.
It was trying to help him.

The only way it knew how.

His hands were still shaking.
But he wasn't scared of them anymore.

They weren't proof he was falling apart.
They were proof he'd survived things
that required that kind of readiness.

Not broken.
Trained.

And maybe he could trust that—
even when it was inconvenient.
Even when it didn't make sense.

His system was on his side.
It just hadn't learned
that the war was over.
```

### Validation Notes
- Meaning inversion: "protection, not malfunction"
- Supporting reframe: "trained, not broken"
- Hands still shaking — no cure
- Insight feels discovered
- "Maybe" maintains tentativeness
- Resolution level: 2 ✓

---

## ST-E-01: Embodiment (Self-Trust Repair)

**Template ID:** `firefighter_st_embodiment_trusting_anyway_v1`
**Content Type:** integration
**Resolution Level:** 3

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{character.name}}` | First name | Derek |
| `{{colleague.name}}` | Colleague name | Martinez |
| `{{location.detail}}` | Specific location | kitchen |

### Template

```
The reactions still came.

{{character.name}} didn't expect them to stop.

His body still did things he didn't ask for.
Heart racing at nothing.
Hands shaking after routine calls.
That hum of readiness
that didn't match the situation.

But he stopped treating it like a verdict.

One morning in the {{location.detail}},
his hands were shaking
while he poured coffee.

{{colleague.name}} was right there.
Could've noticed.

Old {{character.name}} would've hidden it.
Tensed up.
Added it to the evidence file.

But this time,
he just let them shake.

Not because it felt good.
Not because he was "healed."

Because shaking hands
don't mean he can't be trusted.

They mean his body is doing something.
Something learned.
Something protective.
Something that doesn't need his permission
or his understanding.

He finished pouring the coffee.
Hands still unsteady.

And went about his day.

Not fixed.
Not broken.

Just a guy whose body had been through things
and was still figuring out
how much readiness was enough.

He could live with that.

He could trust himself
even when his body was loud.

Because trust isn't the absence of noise.
It's knowing you can handle the noise
and still show up.
```

### Validation Notes
- Relational shift: letting reactions happen without judgment
- Lived example: coffee, colleague present, lets it happen
- Reactions still present — "still came," "hands still unsteady"
- No cure, no permanence
- Trust redefined: "handle the noise and still show up"
- Resolution level: 3 ✓

---

# TEMPLATE METADATA SUMMARY

## File Structure for Implementation

```
templates/
├── firefighter/
│   ├── autonomic_regulation/
│   │   ├── recognition/
│   │   │   └── firefighter_ar_recognition_false_alarm_v1.md
│   │   ├── mechanism_proof/
│   │   │   └── firefighter_ar_mechproof_analysis_trap_v1.md
│   │   ├── turning_point/
│   │   │   └── firefighter_ar_turning_signal_not_command_v1.md
│   │   └── embodiment/
│   │       └── firefighter_ar_embodiment_landing_v1.md
│   ├── cognitive_defusion/
│   │   ├── recognition/
│   │   │   └── firefighter_cd_recognition_replay_loop_v1.md
│   │   ├── mechanism_proof/
│   │   │   └── firefighter_cd_mechproof_engagement_trap_v1.md
│   │   ├── turning_point/
│   │   │   └── firefighter_cd_turning_weather_not_orders_v1.md
│   │   └── embodiment/
│   │       └── firefighter_cd_embodiment_letting_pass_v1.md
│   ├── exposure_tolerance/
│   │   ├── recognition/
│   │   │   └── firefighter_et_recognition_avoidance_cost_v1.md
│   │   ├── mechanism_proof/
│   │   │   └── firefighter_et_mechproof_avoidance_loop_v1.md
│   │   ├── turning_point/
│   │   │   └── firefighter_et_turning_survive_not_escape_v1.md
│   │   └── embodiment/
│   │       └── firefighter_et_embodiment_carrying_it_v1.md
│   └── self_trust_repair/
│       ├── recognition/
│       │   └── firefighter_st_recognition_broken_signal_v1.md
│       ├── mechanism_proof/
│       │   └── firefighter_st_mechproof_monitoring_trap_v1.md
│       ├── turning_point/
│       │   └── firefighter_st_turning_protection_not_malfunction_v1.md
│       └── embodiment/
│           └── firefighter_st_embodiment_trusting_anyway_v1.md
```

## Variable Registry (Firefighter Persona)

```yaml
# persona_variables_firefighter.yaml

character:
  name: "string"           # First name only
  years_on_job: "string"   # Written out (e.g., "twelve")
  rank: "string"           # Engineer, Captain, etc.

location:
  station: "string"        # "Station 7"
  detail: "string"         # "apparatus bay", "kitchen", "bunk room"
  city: "string"           # Optional city name

trigger:
  time: "string"           # "3 AM", "0400"
  event: "string"          # "the warehouse fire", "the call last month"
  situation: "string"      # "high-rise calls", "structure fires"
  sound: "string"          # "tones", "the alarm"

body:
  primary_sensation: "string"    # "chest lock up", "stomach drop"
  secondary_sensation: "string"  # "pulse racing", "hands shake"

colleague:
  name: "string"           # First or last name
  role: "string"           # "his captain", "the probie"

relationship:
  partner: "string"        # "his wife", "his husband"
  partner_name: "string"   # Optional first name
```

## Validation Checklist (Per Template)

| Check | Pass Criteria |
|-------|---------------|
| Role contract | All must_include present; no must_not_include |
| Mechanism alignment | At least one signal; no contradictions |
| Forbidden content | No cure/instructional/technique language |
| Resolution timing | Matches expected level (0/1/2/3) |
| Variable discipline | ≤ 8 per 100 words; anchors only |
| Audio rhythm | Reads aloud cleanly; natural pauses |

---

*End of Firefighter Template Library*
