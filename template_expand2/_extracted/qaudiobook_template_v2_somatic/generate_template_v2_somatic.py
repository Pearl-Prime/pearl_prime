#!/usr/bin/env python3
"""
Audiobook Template Generator V2 SOMATIC
Body-centered therapeutic content for all 4 phases
Emphasizes: sensation, breath, nervous system, embodiment
12 chapters × 10 sections × 5 variants = 600 files
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any

OUTPUT_ROOT = Path("/home/claude/audiobook_template/sections_somatic_v2")
NUM_CHAPTERS = 12
NUM_VARIANTS = 5

CHAPTER_PHASES = {
    1: "HARDSHIP", 2: "HARDSHIP", 3: "HARDSHIP",
    4: "HELP", 5: "HELP", 6: "HELP",
    7: "HEALING", 8: "HEALING", 9: "HEALING",
    10: "HOPE", 11: "HOPE", 12: "HOPE"
}

CHAPTER_TITLES = {
    1: "The Body Remembers",
    2: "Where Tension Lives",
    3: "The Weight We Carry",
    4: "Reading Your Nervous System",
    5: "The Wisdom of Sensation",
    6: "Tools for Regulation",
    7: "Releasing What's Held",
    8: "The Practice of Presence",
    9: "Building New Pathways",
    10: "The Body Opening",
    11: "Embodied Wholeness",
    12: "Moving Forward in Your Body"
}

SECTION_STRUCTURE = [
    {"num": 1, "type": "HOOK", "purpose_template": "Opening — somatic {phase} recognition"},
    {"num": 2, "type": "SCENE", "purpose_template": "Body story — {phase} in the flesh"},
    {"num": 3, "type": "REFLECTION", "purpose_template": "Sensation inquiry — feeling {phase}"},
    {"num": 4, "type": "EXERCISE", "purpose_template": "Somatic practice — {phase} in body"},
    {"num": 5, "type": "SCENE", "purpose_template": "Second body story — {phase} embodied"},
    {"num": 6, "type": "TEACHERDOCTRINE", "purpose_template": "Body wisdom — {phase} teachings"},
    {"num": 7, "type": "REFLECTION", "purpose_template": "Deep sensing — integrating {phase}"},
    {"num": 8, "type": "EXERCISE", "purpose_template": "Integration practice — embodying {phase}"},
    {"num": 9, "type": "SCENE", "purpose_template": "Resolution story — {phase} released"},
    {"num": 10, "type": "INTEGRATION", "purpose_template": "Somatic synthesis — {phase} complete"}
]

# ============================================================================
# SCENE CONTENT - Somatic Body Stories (~150 words frames)
# ============================================================================

def get_scene_content(chapter: int, section: int, variant: int, phase: str) -> str:
    positions = {2: "opening", 5: "middle", 9: "resolution"}
    position = positions.get(section, "middle")
    
    scenes = {
        "HARDSHIP": {
            "opening": [
"""Let me tell you about someone who lived entirely from the neck up.

Her name was Elena, and she was brilliant at thinking her way through life. Analyzing, planning, solving. What she couldn't do was feel her own body. The signals had been turned off years ago, for very good reasons.

This is her story of what happened when the body started speaking anyway.

[STORY_INJECTION_POINT]

Does any of that feel familiar in your own body?

Not her specific story—but the pattern of disconnection. The body that carries while the mind ignores.""",

"""There's a man I know who held his breath for thirty years.

Not literally—but almost. His breathing was so shallow, so controlled, that his body never got the signal that it was safe to relax. He thought this was just how breathing worked.

His story is about what he discovered when he finally exhaled.

[STORY_INJECTION_POINT]

Where in your body do you hold your breath?

What might happen if you let yourself exhale?""",

"""She could feel her heartbeat in meetings.

Not just fast—pounding. Visible in her neck if you looked closely enough. Her body screaming alarm while her face performed calm.

This is what her nervous system was trying to tell her.

[STORY_INJECTION_POINT]

Your body has been sending signals too.

What has it been trying to say that you haven't been ready to hear?""",

"""His back went out on a Tuesday.

No warning. No injury. Just sudden collapse—his body's way of finally getting his attention after years of being ignored.

This is the story of what his back was holding.

[STORY_INJECTION_POINT]

Sometimes the body speaks in whispers. Sometimes in screams.

What's your body's current volume?""",

"""She didn't know she was clenching her jaw until a dentist mentioned she'd ground her teeth flat.

Years of tension, night after night, that she'd never consciously felt. Her body processing what her waking mind couldn't touch.

This is where her stored tension began.

[STORY_INJECTION_POINT]

What is your body processing while you sleep?

What tension has become so familiar you've stopped noticing it?"""
            ],
            "middle": [
"""The middle of Elena's journey didn't look like progress.

Her body was starting to speak, but the language was pain. Sensations she'd suppressed for years were surfacing. It felt like getting worse.

[STORY_INJECTION_POINT]

Sometimes healing feels like breaking.

If your body is getting louder, that might be the beginning, not the end.""",

"""He learned to breathe, but then the emotions came.

That's the thing about breath—it opens channels that have been closed. And what flows through isn't always comfortable.

[STORY_INJECTION_POINT]

Opening the body opens everything.

Are you ready for what wants to move through?""",

"""Her heart kept pounding even after she understood why.

Understanding is not the same as resolution. Her body needed something her mind couldn't provide.

[STORY_INJECTION_POINT]

The body has its own timeline.

Has your mind understood something your body hasn't caught up with yet?""",

"""His back recovered, but the tension moved to his neck.

That's what bodies do—they redistribute what hasn't been fully processed. The symptom shifts, but the source remains.

[STORY_INJECTION_POINT]

Where has your tension migrated?

What's the through-line connecting your symptoms?""",

"""She started noticing the jaw clenching while it was happening.

That's different. Not fixing it—just awareness. The beginning of a different relationship with her own body.

[STORY_INJECTION_POINT]

Awareness before change.

What are you starting to notice that you couldn't see before?"""
            ],
            "resolution": [
"""Elena learned to live in her body, not just above it.

Not all the time—she still goes up into her head when stressed. But now she notices. Now she has a way back down.

[STORY_INJECTION_POINT]

Resolution isn't perfection. It's range.

The ability to leave and come back. That's embodiment.""",

"""His breath became his anchor.

Not something he had to remember—something that was just there. A resource always available. A home in his own body.

[STORY_INJECTION_POINT]

Your body can become your refuge.

The same body that once felt like the source of your problems.""",

"""Her heart still speeds up sometimes. But now she knows what to do.

She has practices. She has awareness. She has the ability to shift her own state.

[STORY_INJECTION_POINT]

Symptoms don't always disappear. But your relationship to them can transform.

What would it mean to not fear your own body?""",

"""His back taught him to listen before the scream.

Now he catches the whisper. The first sign of tension, the early warning of overwhelm.

[STORY_INJECTION_POINT]

Your body is always communicating.

The question is whether you're listening.""",

"""She still clenches sometimes. But she also softens.

That's the change—not the absence of the old pattern, but the presence of a new one alongside it.

[STORY_INJECTION_POINT]

New patterns don't replace old ones. They offer alternatives.

What alternative is your body learning?"""
            ]
        },
        "HELP": {
            "opening": [
"""Understanding begins in the body.

Let me show you someone who learned to read their own nervous system. What they discovered changed everything.

[STORY_INJECTION_POINT]

Your body is already speaking this language.

We're just learning to translate.""",

"""She thought she was anxious. Then she learned about nervous system states.

The distinction mattered. Anxiety is a story. Sympathetic activation is physiology. One requires therapy; the other requires regulation.

[STORY_INJECTION_POINT]

What if your symptoms were information, not problems?

What would change in how you approach them?""",

"""He mapped his body for the first time at forty-three.

A whole territory he'd been living in but had never explored. The exercise was simple: where do I feel this emotion in my body?

[STORY_INJECTION_POINT]

Bodies are landscapes.

Do you know the geography of yours?""",

"""She could finally explain why her stomach always hurt.

Not medically—there was nothing wrong. But somatically—her gut was responding to chronic stress exactly as guts do.

[STORY_INJECTION_POINT]

Symptoms have logic.

When you understand your body's logic, nothing feels random anymore.""",

"""He learned the word "interoception" and it changed his life.

The ability to feel internal states. The sense most people don't know they have—or have lost.

[STORY_INJECTION_POINT]

Can you feel your internal states?

That ability is the foundation of everything else."""
            ],
            "middle": [
"""Understanding came in layers.

First the concepts. Then the recognition. Then the ability to actually apply it in real time.

[STORY_INJECTION_POINT]

Knowing and embodying are different things.

Which phase are you in?""",

"""She could name her state now, but she couldn't change it.

That's the frustrating middle. Awareness without power. Seeing the problem without having the tools.

[STORY_INJECTION_POINT]

Awareness comes before capacity.

Be patient with the gap.""",

"""He practiced regulation in safe conditions. Easy.

Then stress hit and everything he'd learned disappeared. His body defaulted to old patterns.

[STORY_INJECTION_POINT]

Practice under pressure is different than practice in calm.

Both are necessary.""",

"""The concepts were landing in her body now, not just her mind.

She could feel the difference between states, not just describe them. That's integration.

[STORY_INJECTION_POINT]

When knowledge becomes felt sense, everything changes.

What do you know in your body now?""",

"""He was building a vocabulary of sensation.

Tight, buzzy, heavy, hollow, warm, sharp. Words for what had been wordless.

[STORY_INJECTION_POINT]

Language shapes perception.

What words describe your body's current state?"""
            ],
            "resolution": [
"""Understanding became instinct.

She no longer had to think through the steps. Her body knew. Recognition and response were integrated.

[STORY_INJECTION_POINT]

This is mastery—when conscious practice becomes unconscious competence.

You're building toward this.""",

"""He could explain his nervous system to others now.

Not because he had to, but because he understood it well enough to teach. That's real knowledge.

[STORY_INJECTION_POINT]

Can you explain what you're learning?

Teaching is how understanding deepens.""",

"""The map and the territory were aligned.

What she understood about bodies, she could feel in her own. Theory and experience matched.

[STORY_INJECTION_POINT]

Knowledge that isn't embodied is just information.

Knowledge that's lived is wisdom.""",

"""His body became a biofeedback device he didn't need technology for.

He could read his own states, measure his own regulation, track his own progress.

[STORY_INJECTION_POINT]

You are the technology.

Your body already contains everything you need to know.""",

"""She graduated from learning about the body to learning from the body.

That's the shift. When the body becomes teacher, not just subject.

[STORY_INJECTION_POINT]

Your body has wisdom you haven't accessed yet.

What is it trying to teach you?"""
            ]
        },
        "HEALING": {
            "opening": [
"""Healing began when she stopped fighting her body.

Not resignation—release. Letting go of the war she'd been waging against her own nervous system.

[STORY_INJECTION_POINT]

How long have you been at war with your body?

What would armistice feel like?""",

"""His body softened before his mind gave permission.

That's how it often works. The body leads; the mind follows. Trust the body's wisdom.

[STORY_INJECTION_POINT]

Has your body started changing before you expected it to?

Let it. It knows things you don't.""",

"""She cried for no reason during a breathwork session.

Old grief, stored in tissue, finally finding its way out. No story needed. Just release.

[STORY_INJECTION_POINT]

Emotions stored in the body don't need to be understood to be released.

Sometimes they just need space.""",

"""He felt warmth spreading through his chest where tightness used to be.

No effort. No technique. Just his body's natural healing process, finally given the conditions it needed.

[STORY_INJECTION_POINT]

Given the right conditions, bodies heal themselves.

What conditions does your body need?""",

"""Something released in her hip that she'd held for twenty years.

She knew exactly what it was. Or rather, her body knew. The memory was stored there, waiting.

[STORY_INJECTION_POINT]

Bodies hold memory.

What memories might your body be ready to release?"""
            ],
            "middle": [
"""Healing wasn't linear for her.

Some days her body felt open, alive, regulated. Other days, all the old patterns came rushing back.

[STORY_INJECTION_POINT]

Setbacks are part of the process.

They're not evidence that it's not working.""",

"""He hit a plateau that lasted three months.

No movement. No change. Just the same level of regulation, neither better nor worse.

[STORY_INJECTION_POINT]

Plateaus are consolidation periods.

The body is integrating what it's learned.""",

"""Old trauma surfaced that she didn't know was there.

That happens. The body reveals what it's ready to heal, not necessarily what we expect.

[STORY_INJECTION_POINT]

Let the body set the agenda.

It knows what needs attention next.""",

"""His body was reorganizing, and it was uncomfortable.

Old patterns breaking up. New patterns not yet stable. The in-between is always messy.

[STORY_INJECTION_POINT]

Disorganization precedes reorganization.

Trust the mess.""",

"""She learned to stay present when sensation got intense.

Not pushing through—just not running. The sweet spot where healing happens.

[STORY_INJECTION_POINT]

Healing happens at the edge of your capacity.

Are you learning where that edge is?"""
            ],
            "resolution": [
"""Her body found a new baseline.

Not the old normal—something better. A regulation she'd never experienced before.

[STORY_INJECTION_POINT]

You can arrive somewhere you've never been.

Your body can find states it's never known.""",

"""He integrated the healing into his daily life.

Not special practices—just a new way of being in his body throughout the day.

[STORY_INJECTION_POINT]

Real healing becomes how you live, not what you do.""",

"""The trauma was still part of her story, but not stuck in her body.

That's the difference. Memory without activation. Past without present grip.

[STORY_INJECTION_POINT]

Healing doesn't erase the past.

It releases the body from it.""",

"""His nervous system had new range.

States that used to overwhelm him were now manageable. Activation that used to persist now resolved.

[STORY_INJECTION_POINT]

Range is the real measure of healing.

How much has yours expanded?""",

"""She could feel safety in her body.

Not just think about it—feel it. That was new. That was everything.

[STORY_INJECTION_POINT]

Felt safety is the goal.

Not understood safety. Felt safety.

That's home."""
            ]
        },
        "HOPE": {
            "opening": [
"""Hope showed up in her body before she believed it with her mind.

A slight lift in her chest. An unexpected ease in her breath. Her body knew something her thoughts hadn't caught up with.

[STORY_INJECTION_POINT]

Your body might already know what's possible.

What is it trying to show you?""",

"""He woke up one morning feeling different.

Not dramatically—subtly. Like something had settled in the night. Like his body had decided to trust.

[STORY_INJECTION_POINT]

Change often happens beneath awareness.

What might have changed while you weren't watching?""",

"""She found herself humming without thinking about it.

Her body expressing something she didn't have words for. A lightness that had no explanation except healing.

[STORY_INJECTION_POINT]

Joy is a body state.

Have you felt it recently?""",

"""His body took a full breath without him directing it.

Automatic ease. His nervous system defaulting to rest instead of vigilance. That was new.

[STORY_INJECTION_POINT]

What's your body's default state?

Is it shifting?""",

"""Something in her had stopped bracing for the worst.

She only noticed because of its absence. The chronic preparation for disaster—gone. Or at least quieted.

[STORY_INJECTION_POINT]

Sometimes we only notice changes by what's missing.

What's missing that used to be constant?"""
            ],
            "middle": [
"""Hope needed maintenance.

Some days it was easy to feel. Other days she had to practice her way back to it.

[STORY_INJECTION_POINT]

Hope is a practice, not just a feeling.

Are you practicing?""",

"""He learned to return when he drifted.

Not if—when. Everyone drifts. The skill is in the returning.

[STORY_INJECTION_POINT]

Consistency isn't about never falling.

It's about getting back up.""",

"""Her body remembered what felt like home now.

Even when she was far from it, she knew the way back. That knowing was hope made practical.

[STORY_INJECTION_POINT]

Knowing the way back is everything.

Do you know yours?""",

"""He built hope into his morning routine.

Not affirmations—body practices. Actual physiological shifts that set up his nervous system for the day.

[STORY_INJECTION_POINT]

What routines support your body's hope?""",

"""The good states were lasting longer.

That was the change. Not that hard moments disappeared, but that good moments persisted.

[STORY_INJECTION_POINT]

Resilience isn't the absence of difficulty.

It's the persistence of capacity."""
            ],
            "resolution": [
"""She lived in her body now.

Not visited it during practices. Lived there. All day. It had become home.

[STORY_INJECTION_POINT]

What would it mean for your body to feel like home?""",

"""His hope had roots.

Not hope that something good might happen. Hope grounded in the fact that something good had already happened. His body had changed.

[STORY_INJECTION_POINT]

Real hope is retrospective.

It's based on what you've already survived and transformed.""",

"""She knew what was possible because she'd lived it.

Not because someone told her. Not because she believed it. Because her body had experienced it.

[STORY_INJECTION_POINT]

Experience is the ultimate teacher.

What has your body experienced that your mind can now trust?""",

"""His body and mind were allies now.

Working together instead of against each other. That was the real transformation.

[STORY_INJECTION_POINT]

Integration—when body and mind are on the same team.

Are yours?""",

"""She was still becoming.

Not finished. Not fixed. But moving in a direction her body trusted.

[STORY_INJECTION_POINT]

You're not done.

But you're going somewhere good."""
            ]
        }
    }
    
    phase_scenes = scenes.get(phase, scenes["HARDSHIP"])
    position_scenes = phase_scenes.get(position, phase_scenes["opening"])
    return position_scenes[variant - 1]

# ============================================================================
# HOOK CONTENT - Somatic (~200 words each)
# ============================================================================

def get_hook_content(chapter: int, variant: int, phase: str) -> str:
    hooks = {
        "HARDSHIP": [
"""Put your hand on your chest right now.

Feel what's there. The heartbeat. The breath. The warmth of your palm against your body.

Now notice what else lives there. The tightness you've been carrying so long it feels like part of your anatomy. The constriction that shows up every morning before your eyes even open. The weight that has no name but takes up residence between your ribs like it pays rent.

Your body has been trying to tell you something.

Not in words—bodies don't speak that language. In sensation. In the ache that appears when you slow down. In the exhaustion that sleep doesn't touch. In the way your shoulders live somewhere near your ears now, a permanent brace against something that may or may not still be coming.

You've been ignoring these signals. Not because you're bad at listening—because you learned that ignoring was safer than feeling. That pushing through was more rewarded than pausing.

But your body kept the score anyway.

Every unfelt feeling, every swallowed response, every moment you overrode your instincts—it's all still here. Written in your tissue. Waiting.

Today, we start reading.""",

"""Notice your jaw right now.

Is it clenched? Slightly tight? Holding something back?

Most people, when they check, find tension they didn't know was there. A gripping that's become so normal it registers as neutral.

That's how the body holds what the mind won't process.

Your jaw holds the words you didn't say. Your shoulders hold the burdens you couldn't put down. Your belly holds the fear that never fully passed. Your lower back holds the weight of everything you carry for everyone else.

The body is not a metaphor. This is literal. Physical. Measurable.

When we experience something overwhelming and can't complete the natural response—fight, flee, cry, shake, rage—the energy doesn't disappear. It gets stored. Compressed. Held in the tissue until it's safe to release.

For many of us, it's never felt safe.

So the holding continues. Year after year. Until we forget we're holding at all.

This is not weakness. This is brilliant survival.

But survival mode was never meant to be permanent.

Your body is ready to let go.

The question is: are you ready to let it?""",

"""Take a breath.

Not the shallow sip you've been surviving on. A real breath. Let your belly expand. Feel your ribs move.

What happens?

For some people, a full breath brings tears. For others, anxiety. For others, nothing at all—a numbness where sensation should be.

All of these responses are information.

Your breath is the most direct line to your nervous system. The way you breathe reflects the state you're living in. Shallow, chest-only breathing says: danger, stay alert, don't relax. Deep belly breathing says: safe, present, here.

Most of us have been breathing like we're in danger for years.

Not because we're dramatic. Because at some point, we were in danger. And the body learned a pattern. And the pattern became automatic. And automatic became invisible.

You've been running survival software in situations that don't require it.

Your body doesn't know the threat has passed. No one told it. No one knew how.

That's what we're here to do.

Not think our way to peace—that doesn't work.

But teach your body, through direct experience, that now is different from then.

One breath at a time.""",

"""Where do you feel it?

Not the story about what happened. Not the thoughts about why. The actual sensation. Right now. In your body.

Point to it if you can.

Maybe it's your throat—a tightness, a closing. Maybe it's your chest—pressure, heaviness. Maybe it's your stomach—churning, knotting. Maybe it's everywhere, a general sense of unease that has no specific location.

This is where we start. Not with understanding—with sensation.

Because here's what most approaches get wrong: they try to think their way out of body problems. They analyze. They process. They tell the story again and again, hoping that understanding will create change.

But the body doesn't care about your insights.

The body cares about safety. About completion. About finally being allowed to do what it wanted to do back when the thing happened—and couldn't.

Your body has been waiting.

Waiting for permission to shake, to cry, to rage, to collapse, to do whatever it needed to do that got interrupted.

That permission is coming.

But first, we have to find where it lives.

So again: where do you feel it?

That's where we begin.""",

"""Your body is not the enemy.

I know it might feel that way. When anxiety lives in your chest. When panic tightens your throat. When depression weighs down your limbs like wet concrete. When pain shows up with no physical cause.

It's easy to see the body as betrayer. As the thing that makes life hard.

But what if your body is not creating these sensations to hurt you?

What if it's trying to communicate?

Every uncomfortable sensation is a message. Not punishment—information. Your body reporting on conditions. Alerting you to something that needs attention.

We've been taught to override these signals. To push through. To medicate them away. To treat the body as a machine that should perform regardless of its state.

But bodies are not machines.

They're living systems. Intelligent. Responsive. Always trying to keep you alive, even when their methods create suffering.

What you're experiencing right now—whatever brought you here—isn't malfunction.

It's your body doing exactly what it learned to do to survive.

The problem is, you don't need to survive anymore.

You need to live.

And for that, we need a different relationship with this body of yours.

Let's start building it."""
        ],
        "HELP": [
"""Your nervous system has two main modes.

One says: danger, mobilize, act now. Your heart races. Your breath shortens. Your muscles tense for action. Blood flows to your limbs, away from your organs. You're ready to fight or run.

The other says: safe, rest, digest. Your heart slows. Your breath deepens. Your muscles soften. Blood returns to your core. You can think clearly, connect with others, heal.

Most of us are stuck in the first mode.

Not all the time—but far more than we realize. A low-grade activation that never fully resolves. A background hum of alertness that we've mistaken for normal.

This isn't weakness or anxiety disorder or personality flaw.

This is a nervous system doing its job. It detected threat—once, or repeatedly—and it adapted. It learned to stay ready. To not fully relax. Because relaxing wasn't safe.

The problem is, it's still running that program.

Years later. In situations that don't require it.

Your nervous system doesn't know the war is over.

That's what we're going to address. Not by thinking about it—by directly teaching your body that the current moment is different from the past.

Your body can learn.

It's waiting for the lesson.""",

"""There's a reason talk therapy sometimes doesn't work.

Not because therapists aren't skilled. Not because you're not trying. But because the thing that's bothering you doesn't live in your thinking brain.

It lives in your body. In your nervous system. In the survival structures that operate below conscious awareness.

You can understand exactly why you feel the way you feel—and still feel that way.

Because understanding is a top-down process. And what's running you is bottom-up.

Your survival brain doesn't care about your insights. It cares about whether you're safe. And it determines safety not through logic, but through sensation. Through signals from your body.

This is why you can know, intellectually, that you're fine—and still feel panic. Why you can understand your patterns perfectly—and still repeat them.

The path out isn't more understanding.

It's a different kind of communication. Body to brain instead of brain to body.

What does that look like?

It looks like learning to feel sensations without being overwhelmed by them. It looks like completing stress responses that got interrupted. It looks like building capacity to tolerate intensity.

This is body work.

And it changes things that talking alone cannot.""",

"""Let me explain what's actually happening in your body.

When you experience something threatening, your autonomic nervous system responds instantly. Adrenaline floods your system. Your heart rate jumps. Your breathing accelerates. Your muscles prepare for action.

This is brilliant design. It kept our ancestors alive.

The problem comes when the response can't complete.

If you need to run and you run, the stress hormones get used. The body returns to baseline. Done.

But if you can't run—if you have to sit still, act normal, pretend everything's fine—the mobilization has nowhere to go. The energy stays trapped. The chemicals don't clear.

And your nervous system stays activated. Waiting for a resolution that never comes.

This is what's happening in your body. Not metaphorically—physically.

Old, incomplete stress responses, still waiting to complete.

The good news: they can still complete. The body doesn't care that years have passed. It's still holding the charge, still ready to finish what it started.

That's what we're going to do.

Not re-traumatize. Not relive. But allow the body to finally do what it wanted to do. To discharge the held energy. To return to baseline.

Your body knows how.

We just need to give it permission.""",

"""Here's something most people don't know about trauma.

It's not what happened to you. It's what happened inside you.

Two people can experience the same event and have completely different outcomes. One walks away relatively unscathed. The other carries it for decades.

The difference isn't strength or weakness. It's whether the body was able to complete its response.

Trauma is incomplete. It's the survival response that got stuck. The fight that couldn't fight. The flight that couldn't flee. The cry that got swallowed.

When these responses complete, trauma resolves. The event becomes a memory—unpleasant perhaps, but not running your life.

When they don't complete, the body stays stuck. Still fighting. Still fleeing. Still frozen. Even when the mind has "moved on."

This is why you can't just decide to be over something.

Your body isn't over it. Your nervous system is still responding to the past.

Understanding this isn't just intellectual comfort. It's the roadmap for healing.

We don't heal trauma by understanding it better.

We heal it by completing what got interrupted.

And that happens in the body.

Let's learn how.""",

"""Your body speaks a language.

Not words—sensation. And most of us never learned to interpret it.

We learned to override. To ignore. To push through. We learned that the body's signals were inconvenient, irrational, things to be managed rather than listened to.

But the body kept speaking anyway.

Tightness: I'm bracing against something.
Heaviness: I'm carrying too much.
Restlessness: I need to move, to act, to do something.
Numbness: I've shut down to survive.
Heat: Energy is mobilizing.
Cold: Energy is withdrawing.

Every sensation is communication. Your body reporting on its state. Asking for response.

When we ignore these signals, they get louder. The tightness becomes pain. The heaviness becomes depression. The restlessness becomes anxiety. The numbness becomes dissociation.

The body will be heard.

What we're going to do here is learn the language. Start listening. Begin responding in ways that actually help instead of suppress.

Your body has been trying to guide you this whole time.

It's time to tune in."""
        ],
        "HEALING": [
"""Something is different now.

You might not be able to name it, but your body knows. A subtle shift. A slight loosening where there was only tension before.

This is what healing feels like from the inside.

Not dramatic. Not a single breakthrough moment. Just a gradual thawing. Ice becoming water. Slowly, imperceptibly, until suddenly you notice: something has changed.

Your nervous system is learning.

Every time you pause and feel sensation without being overwhelmed—it learns. Every time you allow a difficult emotion to move through without suppressing it—it learns. Every time you stay present when everything in you wants to flee—it learns.

It's learning that you can handle this. That the feelings won't destroy you. That you can feel and survive.

This is the foundation of all healing.

Not understanding. Not insight. Capacity.

The ability to be with what is, without needing it to be different.

You're building that capacity. Right now. With every breath you take while feeling what you feel.

It's working.

Your body is proving to itself that something new is possible.

That's healing.""",

"""Healing is not a straight line.

The body doesn't follow our timelines. It has its own rhythm, its own pace. Some days you'll feel expanded, open, more yourself than you've been in years. Other days you'll feel like you're back at the beginning.

Both are part of the process.

When old sensations return—when the tightness comes back, when the anxiety resurfaces—it doesn't mean you've failed. It means another layer is ready to be released.

The body heals in spirals.

Each pass through familiar territory happens at a different level. The same trigger, but you have more resources now. The same sensation, but more capacity to hold it.

What used to overwhelm you becomes workable. What used to send you into shutdown becomes just another thing you can feel.

This is how it goes.

Not upward, always. But inward, deeper. Spiraling through the same material with increasing ability.

Trust the process.

Your body knows how to heal. It's been waiting for conditions safe enough to begin.

Those conditions are here now.

Let your body do what it knows how to do.""",

"""Let me tell you about the space between.

Between stimulus and response, there is a space.

In that space lives everything—choice, freedom, the possibility of doing it differently this time.

When your nervous system is dysregulated, that space shrinks to nothing. Trigger and reaction happen simultaneously. You're not choosing; you're being moved by forces below conscious control.

Healing expands that space.

Not by suppressing the reaction—by building capacity. By increasing your tolerance for sensation. By teaching your nervous system that it doesn't have to respond to everything as emergency.

This is what you've been doing.

Every time you paused before reacting. Every time you felt the sensation without immediately acting on it. Every time you let the wave of activation rise and fall without grabbing onto it.

You've been building space.

And in that space, something remarkable happens.

You get to choose.

Not from a place of suppression. From genuine capacity. From a nervous system resourced enough to pause, consider, and respond rather than react.

This is freedom.

Not freedom from difficulty—freedom within it.

You're more free now than when you started.

Can you feel it?""",

"""Your body knows how to heal.

This might be the most important thing you learn.

You don't have to figure out how to heal. You don't have to direct the process. You don't have to understand every step.

Your body already knows.

It healed your cuts and bruises without your conscious direction. It fights off infections you never even know about. It maintains temperature, heart rate, thousands of processes every second—all without you doing a thing.

Healing emotional and nervous system wounds is no different.

Your body knows how to release what it's holding. It knows how to complete interrupted responses. It knows how to return to regulation.

It just needs the right conditions.

Safety. Permission. Time. Attention.

That's what we've been building.

Not teaching your body how to heal—creating conditions for it to do what it already knows how to do.

Trust this.

When you feel an impulse to shake, to cry, to yawn deeply, to take a big breath—that's your body healing. That's the intelligence emerging.

Don't direct it. Follow it.

Your body is leading.

All you have to do is let it.""",

"""There's a different kind of strength emerging in you.

Not the hard strength of tension, of holding it together, of gritting through. That strength kept you alive, and it cost you everything.

This is soft strength. Flexible strength. The strength of bamboo that bends in the wind rather than the oak that breaks.

It comes from capacity, not effort.

When your nervous system is regulated, you don't need to tense against the world. You can meet what comes with openness because you know—in your body, not just your mind—that you can handle it.

This strength isn't about not feeling. It's about feeling fully and remaining present. Letting the wave wash through without being swept away.

You're developing this.

Every time you stay with a sensation rather than fleeing it. Every time you let yourself feel without needing to fix. Every time you trust the process when every instinct says to control.

Soft strength.

It doesn't look impressive from the outside. But it's the foundation of everything.

The ability to be with what is.

That's what you're building.

That's what's going to change everything."""
        ],
        "HOPE": [
"""Feel your body right now.

Not as a problem to be solved. Not as a vessel that has failed you. Just... feel it.

The weight of it. The warmth. The subtle movements of breath.

Something is different, isn't it?

There's more space inside. More room to breathe. More capacity to simply be here, in this body, in this moment, without needing anything to change.

This is what we've been building toward.

Not a body without difficulty—that's not possible. But a body you can inhabit. A body that feels like yours again. A body that's home rather than war zone.

You've earned this.

Through every uncomfortable moment you stayed present for. Through every sensation you let yourself feel. Through every time you chose awareness over avoidance.

Your nervous system has learned.

It knows now—not believes, knows—that you can feel difficult things and survive. That sensations rise and fall. That this moment, whatever it contains, is workable.

From this ground, everything is possible.

Not because you've transcended being human. Because you've finally become human. Fully here. In your body. Feeling what you feel.

That's all that was ever needed.

Welcome home.""",

"""Your body has changed.

The changes might be subtle. You might not notice them until you compare now to then. But they're real. Physical. Measurable.

Your baseline has shifted.

Where once your nervous system lived in constant low-grade activation, it now knows how to settle. Where once relaxation felt impossible or even dangerous, it now becomes available more easily.

These aren't just feelings. These are neurological changes. New pathways carved by practice. New defaults that become more natural with each repetition.

Your body has literally rewired itself.

And it will continue to. The brain and nervous system remain plastic throughout life. Every experience shapes them. Every moment of choosing presence over reactivity strengthens the new pattern.

You're not done. You never will be.

But you've proven something important: change is possible. Not just intellectual change—body change. The kind of change that actually changes how you move through the world.

What else might be possible?

What other limitations might be learned, not fixed?

What other capacities might be waiting to develop?

From here, you get to explore.

The body that felt like a prison is becoming a laboratory.

What do you want to discover?""",

"""There's a ripple effect to this work.

When your nervous system changes, everything changes.

You relate to others differently—from regulation rather than reactivity. You make decisions differently—from clarity rather than desperation. You move through the world differently—with presence rather than perpetual alertness.

People around you will notice.

Not because you'll tell them—because they'll feel it. Nervous systems communicate directly, below words. Your regulation becomes an invitation for their regulation.

This is how healing spreads.

Not through preaching or teaching. Through presence. Through the quality of attention you bring. Through the nervous system that others' nervous systems can feel as safe.

You're becoming a different kind of presence in the world.

One that allows others to settle. To breathe. To feel their own bodies more fully.

This isn't responsibility—it's natural consequence. You didn't sign up to become a healer.

But a regulated nervous system in a dysregulated world is its own kind of medicine.

What you've done for yourself, you're now offering to others.

Just by being who you've become.

Just by being present.

That matters more than you know.""",

"""Here's what you take with you.

Not concepts—though those have their place. Not even tools—though you have those now.

What you take with you is capacity. The increased ability to be with what is. The expanded tolerance for sensation. The knowledge—body knowledge, not just mind knowledge—that you can handle this.

Whatever this turns out to be.

Because life will keep happening. Stress will come. Difficulty will arise. Old patterns will sometimes resurface.

But you're different now.

Not because you've transcended difficulty. Because you've developed the capacity to be with it.

When the tightness returns, you'll know what to do. When the anxiety arises, you'll have resources. When old triggers fire, you'll have space.

You won't be perfect. There is no perfect.

But you'll be present. Resourced. Able to ride the waves rather than be tumbled by them.

This capacity is yours now.

No one can take it away. No circumstance can erase it. It lives in your body, in your nervous system, in the new patterns you've built.

Take it with you.

Into whatever comes next.

You're ready.""",

"""Stand up for a moment. Or if you're lying down, feel your full length.

Feel your body.

Not as problem or project. Just as it is. This body that has carried you through everything. This body that held what you couldn't face until you could. This body that's been waiting, patiently, for you to return to it.

You're here now.

Present. In your body. Able to feel what you feel without being destroyed by it.

This is the destination. Not somewhere else. Not some future state. Here. Now. In this body.

Everything we've done has led to this simple thing: your ability to be here.

It sounds small. It's everything.

From here, you live your life. Make your choices. Connect with others. Meet whatever comes.

Not from dissociation or avoidance or perpetual mobilization.

From presence.

Your body is no longer enemy or stranger. It's home. It's you.

Breathe that in.

Feel your feet on the ground. The weight of your body. The breath moving through you.

This is it.

This is everything.

You've arrived.

Now go live."""
        ]
    }
    return hooks.get(phase, hooks["HARDSHIP"])[variant - 1]

# ============================================================================
# REFLECTION CONTENT - Somatic Sensation Inquiry (~250 words)
# ============================================================================

def get_reflection_content(chapter: int, section: int, variant: int, phase: str) -> str:
    depths = {3: "early", 7: "deep"}
    depth = depths.get(section, "early")
    
    reflections = {
        "HARDSHIP": {
            "early": [
"""Bring your attention into your body right now.

Not thinking about your body—actually feeling it from the inside. This is a different mode of awareness. Interoception. The sense of your internal state.

What's here?

Start with the obvious. The surface sensations. Where does your body contact the chair, the floor? What's the temperature of your skin?

Then go deeper. What's happening in your chest? Not what you think should be there—what's actually there. Tightness? Spaciousness? A kind of buzzing?

And your belly. The seat of so much emotional processing. Is it soft? Contracted? Moving with breath or held still?

Don't try to change anything. Just notice.

This is harder than it sounds. We're so trained to fix, to improve, to move away from discomfort. But right now, just witness.

What is your body holding in this moment?

If you listen without agenda, the body will tell you. Not in words—in sensations. In subtle shifts of temperature and tension. In the places that call for attention and the places that go numb.

What's asking to be felt?

Let yourself feel it.

That's the work.""",

"""Notice your breath right now.

Don't change it—that comes later. First, just observe.

Where does the breath go? High in your chest? Deeper into your ribs? All the way down into your belly?

How fast? How slow?

Is there a pause at the top? At the bottom? Or does it cycle continuously?

Your breath is a mirror of your nervous system state. Fast, shallow, chest-only breathing signals activation. Slow, deep, belly breathing signals safety.

Which is yours right now?

Again, no judgment. No fixing yet. Just seeing clearly.

The breath has likely been this way for years, maybe decades. You've adapted to it. It feels normal.

But normal isn't the same as optimal.

What would it be like to breathe differently?

Not now—we'll practice that later. But plant the seed.

Your breath is not fixed. It's a habit. And habits can change.

For now, just feel how you're breathing.

That awareness itself is significant.""",

"""Where is the tension?

Scan through your body slowly, like you're moving a flashlight of attention from head to toe.

Start at the top. Your scalp. Your forehead. Are you holding there? Your eyes—are they straining? Your jaw—clenched or soft?

Move down. Throat. That place where so much gets stuck, where words not spoken accumulate.

Shoulders. The place most people carry the weight of their responsibilities. How much weight is there right now?

Chest. Heart area. What's the quality of sensation around your heart?

Belly. Solar plexus. The gut that processes emotion even when you're not aware of it.

Low back. Hips. The base of the spine where we store the oldest material.

Legs. Feet. Connection to ground.

Where did you find tension?

That's not random. That's your body's map of what it's holding. Each tension is a message, a stored experience, an incomplete process.

Don't try to interpret yet. Just know where your body is gripping.

That's information you'll need for what comes next.""",

"""Sit with the discomfort.

I know that's not what you want to hear. You want relief, not more sitting with hard things.

But here's what I've learned: sensation that's resisted persists. Sensation that's allowed moves through.

So let's try something different. Find the most uncomfortable sensation in your body right now.

Don't go to the worst thing you've ever felt. Just what's here now. The tightness, the ache, the unease.

Instead of pushing it away, let yourself be curious about it.

What exactly is the sensation? Not the story about it—the raw data. Is it sharp or dull? Hot or cold? Moving or static?

How big is it? Does it have edges?

As you attend to it with curiosity, what happens?

Often—not always, but often—sensation shifts when we stop fighting it. It might intensify briefly, then ease. It might move, change quality, reveal layers underneath.

What happens when you stay with it?

This is the practice. Not once, but repeatedly. Building capacity to feel without fleeing.

Your body has been waiting for you to stop running.""",

"""Notice what's numb.

We talk a lot about tension, about pain, about activation. But sometimes the more significant information is in the areas that don't feel anything at all.

Scan through your body again. This time, look for the blank spots. The areas that don't register on your internal radar.

Maybe your legs feel like they don't quite exist. Maybe your pelvic area is a void. Maybe parts of your back seem to disappear.

Numbness is also a signal.

It's your nervous system's way of protecting you from sensation that was too much. It's a brilliant adaptation.

But it comes at a cost. Those numb areas still hold information. They just can't communicate it.

What areas of your body are you disconnected from?

Don't force reconnection. That's not how it works. Just acknowledge the disconnection with kindness.

Those areas went quiet for good reasons.

They'll come back online when it's safe enough. For now, just know they're there. Know that parts of your body have been waiting in the dark.

Eventually, we'll turn the lights back on.

Gently. At your pace.

For now, just notice the shape of what's missing."""
            ],
            "deep": [
"""Go deeper now.

Past the surface sensations. Past the obvious tension. Into the subtle body—the felt sense that's harder to name.

There's a layer of sensation beneath the physical. A kind of energetic quality. You might feel it as aliveness or deadness. As flow or stagnation. As space or density.

Can you feel that layer?

It takes practice. We're so oriented to gross sensation that subtle sensation can seem invisible.

But it's there. It's always there. It's the substrate beneath everything.

What's the quality of your subtle body right now?

This isn't metaphor. Your nervous system is generating a felt sense in every moment. Usually it's below awareness, running the show from behind the scenes.

When you can feel it, you can work with it.

What does your deeper body want you to know?

Listen. Not for words—for feeling.

The body speaks in a language older than thought.

What's it saying?""",

"""There's a place in your body that's been waiting.

The core of the holding. The original wound, stored in tissue. The place you've been protecting, working around, avoiding without knowing you're avoiding it.

Can you feel where it is?

Not necessarily the oldest trauma. Just the center of gravity for what you're carrying. The place that everything else organizes around.

It might be obvious—a chronic pain site, an area of persistent tension. Or it might be hidden—a numbness so complete you didn't know it was there.

Bring your attention to that place.

Not to fix it. Not to release it. That's not how this works. Trying to force release just creates more tension.

Just acknowledge it. Say, internally: I know you're here. I know you've been holding something. I'm not going to force you to let go.

That's the first step. The body needs to know it's safe before it will release. It needs to trust that you're not going to abandon it again, push past it again, override it again.

What does that place need to hear from you?

What would help it know it's safe?

Listen. The answer is already there.""",

"""Feel what's beneath the tension.

There's always something underneath. Tension is a surface phenomenon—a protective layer. What it's protecting is the actual material.

So let's go there.

Pick an area of tension in your body. Feel it fully.

Now, instead of trying to release the tension, get curious about what's underneath.

If this tension is armor, what is it protecting?

You might feel something vulnerable. Something young. Something tender that needed protection.

Or you might feel nothing—a void. Sometimes what's underneath has been so suppressed it's disappeared from awareness.

Either response is information.

What's beneath your tension?

This is sacred territory. Whatever you find has been waiting a long time to be seen.

Approach it with the reverence it deserves.

The body protected it for good reasons.

Now it's safe enough to acknowledge what's there.""",

"""The deepest layer isn't sensation at all.

It's presence. Awareness itself. The you that's noticing everything else.

Can you find that layer?

It's not located in any particular part of your body. It's not tight or relaxed, painful or pleasant. It's the space in which all sensation arises.

This is your essence. Prior to the patterns. Prior to the tension. Prior to the adaptations.

When you rest in this layer, everything else is just weather. Sensations come and go, but you—the awareness—remain.

This isn't dissociation. Dissociation is leaving the body. This is being more fully present to the body while knowing you're not limited to it.

Can you hold both? Full embodiment and spacious awareness?

That's the advanced practice. Being in the body without being trapped by it. Feeling everything without being overwhelmed.

Rest here for a moment.

This is what's possible. This is what your nervous system is capable of.

Remember this state.""",

"""Bring compassion to whatever you've found.

You've been feeling into difficulty. Into the places your body has been holding.

Now meet it with kindness.

Not the kind of compassion that wants to fix. The kind that accepts. That says: of course this is here. Of course my body carries this.

Feel the sensations again—whatever's present. But this time, imagine breathing kindness toward them. Soft attention. Warmth without agenda.

What changes?

Often, when we meet sensation with compassion, it softens. Not because we're trying to change it—but because acceptance is what it needed all along.

Your body has been bracing against its own experience.

When you bring kindness, the bracing can relax.

Feel what it's like to be on your body's side.

Maybe for the first time.

This is the foundation of all healing. Not technique. Kindness.

The body knows how to heal.

It just needs to know it's safe.

You can provide that safety.

Right now. With your attention. With your care."""
            ]
        },
        "HELP": {
            "early": [
"""Name what you're feeling.

Not the emotion—the sensation. Emotions are interpretations. Sensations are data.

What are the physical qualities of your current state?

Tight, loose. Heavy, light. Hot, cold. Buzzy, still. Sharp, dull.

Build a vocabulary of sensation. This is one of the most important skills you'll develop.

Why does naming matter? Because it creates space. When you can name a sensation, you're not just lost in it. There's a you observing, categorizing, making sense.

That tiny bit of distance is everything.

What words describe what you're feeling right now?

Be specific. "Bad" isn't a sensation. "Heavy pressure in my chest" is.

The more precisely you can name it, the more clearly you can see it.

And what you can see, you can work with.""",

"""Identify your nervous system state right now.

Remember the three states: ventral vagal (safe, connected), sympathetic (activated, mobilized), dorsal vagal (shut down, collapsed).

Which one are you in?

There are physical markers for each.

Ventral vagal: easy breath, soft face, clear thinking, sense of connection, body feels present and regulated.

Sympathetic: rapid breath or held breath, tension in shoulders and jaw, racing thoughts, body feels keyed up, ready for action.

Dorsal vagal: shallow or barely-there breath, heavy limbs, foggy thinking, body feels distant, numb, or absent.

You might be in a blend. That's normal.

What's your current mix?

This isn't judgment—it's navigation. You can't change your state if you don't know what state you're in.

And now that you know?

That awareness alone starts to shift things.""",

"""Where is your window of tolerance right now?

The window of tolerance is the zone where you can feel sensations without being overwhelmed by them. Where you can process without shutting down.

Too much activation, and you're above the window—flooded, overwhelmed, panicking.

Too much shutdown, and you're below—numb, disconnected, checked out.

In the window, you can feel, think, and function all at once.

Where are you right now relative to your window?

If you're above it, you need calming practices.

If you're below it, you need activating practices.

If you're in it, you can deepen the work.

This is practical. Different nervous system states need different interventions.

What does your nervous system need right now?

Not what you think it should need. What it actually needs, based on your current state.

Learn to ask this question.

It's the foundation of self-regulation.""",

"""Notice what happens when you pay attention to sensation.

Just the act of noticing—what does it do?

For some people, attention intensifies sensation. The pain gets louder, the tension more obvious.

For others, attention softens sensation. Acknowledgment allows release.

For still others, attention reveals layers. What seemed like one sensation turns out to be many.

What happens for you?

This is useful information. It tells you about your nervous system's current relationship to attention.

If attention intensifies, you might need more resourcing before deepening.

If attention softens, you're ready to work with sensation directly.

If attention reveals layers, you're learning to read the body's complexity.

There's no right answer. Just your answer.

What does your body do when you pay attention?""",

"""Distinguish between thinking about sensation and feeling sensation.

This is crucial. Most people, when asked to feel their body, start thinking about their body instead.

Thinking is commentary. Feeling is direct experience.

Thinking: "I notice tension in my shoulders."
Feeling: The actual experience of shoulder tension—the quality, the texture, the aliveness of it.

Right now, drop out of thinking mode.

Let your awareness be in the sensation itself. Not describing it, not evaluating it—just being in it.

Can you feel the difference?

This mode of awareness is what we're cultivating. Direct, unmediated contact with your body's experience.

It takes practice because we're so thought-dominated.

But every moment you spend actually feeling—not thinking about feeling—is training.

Where can you rest your awareness right now?

Not in thoughts about that place. In the sensation itself.

Stay there.

That's the practice."""
            ],
            "deep": [
"""Feel into the patterns.

You've learned that your nervous system has patterns—habitual ways of responding. Now feel them directly.

Notice what happens in your body when you imagine something stressful.

Where does it activate? What's the sequence?

Maybe your breath catches first, then your shoulders rise, then your jaw clenches. That's a pattern.

Can you feel your pattern?

Now notice what happens when you imagine something soothing.

Where does your body soften? What changes?

These patterns aren't random. They were shaped by experience. They make sense given your history.

But they're not fixed.

What would it be like to have different patterns?

Not to force them—you can't force nervous system change. But to know that change is possible.

The patterns you feel right now are not who you are.

They're what your nervous system learned.

And learning can continue.""",

"""Find the edge.

There's a boundary to what you can feel without getting overwhelmed. A place where sensation is intense but workable.

That edge is where growth happens.

Too far from the edge, and nothing changes—you're just comfortable.

Too far past the edge, and you're flooded—the system shuts down rather than integrates.

Right at the edge, you can feel fully while staying present.

Where's your edge right now?

Approach it carefully. Find a sensation that's challenging but not overwhelming.

Stay there.

Not pushing through. Not backing away. Just staying with intensity that's at the very limit of your capacity.

This is where the nervous system learns.

It's uncomfortable. But it's not dangerous.

Can you tell the difference?

Uncomfortable but safe is the growing edge.

Find it. Stay there. Grow."""
            ]
        },
        "HEALING": {
            "early": [
"""Notice what's releasing.

As healing happens, the body lets go. Tension dissolves. Holding patterns soften.

Can you feel any of that happening right now?

It might be subtle. A slight easing in your jaw. A breath that goes a little deeper than usual. A sense of settling you can barely name.

These small releases are significant.

Don't discount them because they're not dramatic.

Your nervous system is reorganizing at the level it can handle. If it released everything at once, you'd be overwhelmed.

So it goes slowly. Incrementally. Safely.

What's releasing?

Pay attention to the easing as much as you pay attention to the holding.

That's where healing lives.""",

"""Let the body lead.

You've been directing a lot—attention here, breath there. Valuable practice.

Now see what happens when you stop directing.

Let your awareness be general, diffuse. Rather than pointing it somewhere, let the body call your attention where it wants to go.

Where does it draw you?

That's where the work wants to happen.

The body has an intelligence that your conscious mind doesn't have. It knows what needs attention next.

Can you trust that intelligence?

For the next few minutes, don't guide. Follow.

Let the body show you what matters.

What's it saying?""",

"""Feel into the healing itself.

Healing has a sensation. It's not dramatic—usually. It's more like... settling. Integrating. Coming back online.

Can you feel that happening anywhere in your body?

Maybe it's a warmth spreading. Maybe it's a gentle vibration. Maybe it's just a sense of "right" that wasn't there before.

Healing is a process, not an event. It's happening continually, beneath your awareness.

But when you tune in, you can feel it.

What's healing in your body right now?

Not what you hope is healing. What you can actually feel.

That felt sense of repair is precious.

Attend to it. Let it grow.""",

"""Rest in safety.

Can you find—right now—a place in your body that feels safe?

It might be small. A single spot that's not activated, not numb, just... okay.

Find it.

Now rest your attention there.

Let that safe spot be your anchor. A home base you can return to when things get intense.

This is a resourcing practice. You're building the capacity to find safety inside your own body.

Expand your awareness a little. Can you let that safety spread?

Not forcing it. Just seeing if adjacent areas can borrow some of that okay-ness.

What happens?

This is how regulation expands. Island by island. Safe spot by safe spot.

What's your safe spot teaching you about what safety feels like?""",

"""Notice the integration happening.

You've done a lot of work. Felt a lot of sensation. Brought awareness to places that were hidden.

Now the body is integrating all of that.

Integration feels like consolidation. Like things fitting together that were scattered.

Can you feel that?

It might be a kind of coherence. A sense that the parts are talking to each other.

Don't do anything. Just let the integration happen.

Your body knows how to do this. It's been waiting for the chance.

What's coming together?"""
            ],
            "deep": [
"""Meet the wound.

Somewhere in your body, there's a core wound. The original hurt that everything else organizes around.

You might have touched it already. You might be circling it still.

Now, with all the safety and capacity you've built, can you feel it directly?

Not diving in—approaching. Slowly. With respect.

What's there?

This is sacred territory. What you find has been waiting a long time.

Approach with reverence.

What does the wound need you to know?

Listen. Not with your mind—with your body.

What's being communicated?""",

"""Let the body complete what was interrupted.

Trauma is often incomplete. A response that got stuck. An action that needed to happen but couldn't.

Can you feel any incomplete impulses in your body?

A need to push away. To run. To scream. To collapse into being held.

These impulses are still there, waiting.

What wants to complete?

Don't force anything. Just feel for the impulse that's been waiting.

Maybe your shoulders want to push. Maybe your legs want to run.

Let a micro-movement happen. Just a hint of the action.

That's how completion works. Not re-living the trauma, but completing the response that got stuck.

What movement wants to happen?""",

"""Find the peace beneath the storm.

Under all the activation, all the trauma, all the patterns—there's a stillness.

It's always there. It's the ground you're built on.

Can you feel it?

Let your awareness sink beneath the sensations. Past the tension, past the holding, past even the healing that's happening.

What's underneath everything?

That's the you that was never damaged. Never wounded. The awareness that witnessed everything without being destroyed by it.

Rest there.

This isn't dissociation—it's depth.

You can feel everything and rest in this peace simultaneously.

That's integration. That's wholeness.

Feel it now.""",

"""Let grief move through.

Healing often brings grief. Not because something is wrong—because something is being released.

Grief for the time lost. Grief for what you had to survive. Grief for the parts of yourself that shut down to cope.

Can you feel grief in your body?

It has a distinct sensation. Heavy, downward, often in the chest or throat.

Let it be there.

Grief is love with nowhere to go. It's evidence of how much you cared. How much life mattered to you even when it was hard.

Let the grief move.

Not forcing it. Not drowning in it. Just letting it be what it is.

What's being grieved?

The body will tell you, if you listen.""",

"""Feel the tenderness.

As armor softens, what's underneath is tender. Young. Vulnerable.

Can you meet that tenderness with care?

Not trying to toughen it up. Not trying to protect it more. Just being present with it.

This might be the youngest part of you. The part that got hurt before you had any way to cope.

What does it need?

Usually just to be seen. To be acknowledged. To know that you're here now, and you're not going to abandon it.

Feel what it's like to offer that presence to yourself.

To be the adult your younger self needed.

This is reparenting in the body.

What does your young self need you to know?"""
            ]
        },
        "HOPE": {
            "early": [
"""Feel what's possible now that wasn't before.

Your nervous system has more range. There are states available that were once out of reach.

Can you feel that expanded capacity?

Maybe calm is more accessible. Maybe aliveness is closer to the surface. Maybe you can hold intensity without being overwhelmed.

What new states are available?

This is real. These aren't just ideas—they're actual nervous system changes.

Your body has learned things it didn't know before.

Feel the learning.""",

"""Notice where you find hope in your body.

Hope isn't just cognitive. It has a physical signature.

For some people, it's a lift in the chest. An openness. An orientation toward the future that you can actually feel.

Where do you feel hope?

If you can't find it, that's okay. Sometimes hope is quiet.

But see if you can detect even a hint.

A possibility that wasn't there before. A direction that feels alive.

What does hope feel like in your body?

That sensation is a resource. You can return to it when you need to remember what you're moving toward.""",

"""Feel your body's resilience.

After everything you've been through—both in life and in this healing process—you're still here. Still capable of feeling. Still growing.

That's resilience.

Can you feel it in your body?

It might feel like flexibility. The ability to bend without breaking. Or it might feel like strength. A solidity you can count on.

Where is resilience in your body?

This isn't something you have to build. It's already there. It's what got you this far.

Feel it. Acknowledge it. Let yourself be proud of it.

Your body has survived so much.

And it's still capable of thriving.""",

"""Sense the direction you're moving.

Your nervous system has momentum now. There's a direction to the healing.

Can you feel where you're heading?

Not specifically—that's for the future to reveal. But the general direction. Toward more regulation. More presence. More capacity.

Feel that trajectory.

It's not guaranteed—nothing is. But it's real. The changes you've made are building on each other.

What does the future feel like in your body?

Not what you think about the future. What you feel about it.

That felt sense is valuable data.

What direction is your body moving?""",

"""Find gratitude in your body.

Not forcing thankfulness. Finding where it naturally arises.

What is your body grateful for?

Maybe for the rest it's getting. For the attention. For the healing that's happening.

Feel the sensation of gratitude. It has a quality—usually warm, soft, located around the heart.

Can you find it?

Gratitude isn't just positive thinking. It's a nervous system state. A parasympathetic activation that supports healing.

When you feel gratitude, your body shifts.

What are you genuinely grateful for, in this moment?

Feel that.

Let it spread."""
            ],
            "deep": [
"""Feel yourself as whole.

Not perfect—whole. Complete in this moment, even with the work still to do.

Can you feel that wholeness?

It's not about everything being resolved. It's about knowing you're already everything you need to be.

The healing will continue. But you're not waiting to be whole. You already are.

Feel what that's like in your body.

Wholeness despite imperfection. Completeness despite ongoing process.

This is the deepest hope: that you're not broken. Never were.

Feel that in your bones.""",

"""Connect to something larger.

Your body is not separate from everything else. It's part of a larger web of life.

Can you feel that connection?

The air you breathe was breathed by others. The ground you stand on supports billions. The rhythm of your heart is shared by all mammals.

Feel your belonging.

Not conceptually—in your body.

What does it feel like to be part of everything?

This connection is always available. You're never actually alone.

Feel it now.

Let that connection be a resource.

You're held by something vast."""
            ]
        }
    }
    
    phase_reflections = reflections.get(phase, reflections["HARDSHIP"])
    depth_reflections = phase_reflections.get(depth, phase_reflections["early"])
    return depth_reflections[variant - 1]

# ============================================================================
# SCENE CONTENT - Somatic (~150 words frame for injection)
# ============================================================================

def get_scene_content(chapter: int, section: int, variant: int, phase: str) -> str:
    positions = {2: "opening", 5: "middle", 9: "resolution"}
    position = positions.get(section, "middle")
    
    scenes = {
        "HARDSHIP": {
            "opening": [
"""Let me tell you about someone who carried everything in her shoulders.

Elena didn't know she was doing it. Twenty years of tension had become invisible to her—just the way her body was.

Until the day her body refused to cooperate.

[STORY_INJECTION_POINT]

Do you recognize anything in that story?

Not the specifics—those are hers. But the pattern of holding. The way the body keeps score when we stop listening.

Where does your body carry what you haven't faced?""",

"""Here's a story about a man who forgot how to breathe.

Marcus had been chest-breathing for so long—short, shallow, survival breaths—that when someone suggested he breathe into his belly, his body didn't know how.

It had been that long since he felt safe enough to breathe fully.

[STORY_INJECTION_POINT]

Your breath tells your history.

What is your breathing pattern saying about what you've been through?""",

"""She couldn't feel her legs.

Not physically—Sara could walk fine. But when asked to notice the sensations in her lower body, there was nothing. A blank space where feeling should be.

Dissociation written in tissue.

[STORY_INJECTION_POINT]

Where in your body have you gone numb?

Not as judgment—as curiosity. The body protects itself by shutting down sensation.

What was your body protecting you from?""",

"""His jaw told the whole story.

Dental records showed grinding. Muscle tension showed clenching. A lifetime of words unspoken, held in bone and sinew.

James had never connected his jaw pain to his life.

[STORY_INJECTION_POINT]

The body speaks in symptoms.

What symptoms have you been treating as random that might actually be communication?""",

"""The panic always started in her stomach.

Before Maya could think "I'm anxious," her gut was already churning. The body knew before the mind could catch up.

[STORY_INJECTION_POINT]

Your body often knows first.

Where do your difficult feelings begin, physically, before they become thoughts?"""
            ],
            "middle": [
"""The middle of body work is uncomfortable.

Elena was learning to feel things she'd spent decades not feeling. It wasn't pleasant.

[STORY_INJECTION_POINT]

This is the part nobody warns you about. Thawing frozen tissue means feeling what was frozen.

If you're uncomfortable, you might be exactly on track.""",

"""Marcus's body started shaking.

Not pathology—release. His nervous system finally felt safe enough to discharge decades of held tension.

It scared him at first.

[STORY_INJECTION_POINT]

When the body starts releasing, it doesn't look pretty. Shaking. Crying. Heat. Cold.

Trust the process. Your body knows what it's doing.""",

"""Sara could feel her feet now.

A small thing. Huge thing. Sensation returning to territory that had been numb for years.

[STORY_INJECTION_POINT]

The return of sensation isn't always comfortable. But it's always significant.

What's starting to wake up in your body?""",

"""James's jaw finally unclenched.

Not because he decided to relax it. Because something underneath shifted. The holding became unnecessary.

[STORY_INJECTION_POINT]

Real release isn't willful. It's what happens when the body finally feels safe enough.

What wants to let go but hasn't felt safe enough yet?""",

"""Maya's panic attacks were changing.

Still there, but different. She could feel them building now. Had moments before they peaked. Space was opening.

[STORY_INJECTION_POINT]

The middle of healing rarely looks like the end. But the differences are real.

What's shifting, even if it hasn't shifted completely?"""
            ],
            "resolution": [
"""Elena's shoulders finally dropped.

Not temporarily—fundamentally. Her body had learned that it didn't need to hold anymore. The new pattern became default.

[STORY_INJECTION_POINT]

Resolution in the body isn't dramatic. It's a new normal. A baseline that used to be impossible.

What new normal is becoming available to you?""",

"""Marcus breathed into his belly without thinking now.

What had been impossible had become automatic. His nervous system had rewired.

[STORY_INJECTION_POINT]

The body learns. Given time, practice, and safety—it actually changes.

What's your body learning?""",

"""Sara felt everything now.

Not always pleasant. But alive. Present. In her body in a way she hadn't been since childhood.

[STORY_INJECTION_POINT]

The return of sensation means the return of life. Not just the good feelings—all of them.

That's not a problem. That's being human.""",

"""James's jaw still clenched sometimes.

But now he noticed. And noticing, he could soften. The pattern hadn't disappeared—his relationship to it had changed.

[STORY_INJECTION_POINT]

Healing doesn't mean patterns never arise. It means you have choice in how to respond.

What patterns can you now see and work with?""",

"""Maya's panic didn't control her anymore.

It still visited. But she could feel it, ride it, let it pass. The sensation that used to be enemy had become just... sensation.

[STORY_INJECTION_POINT]

This is the real resolution. Not absence of difficulty—capacity to be with it.

That's what we've been building all along."""
            ]
        },
        "HELP": {
            "opening": [
"""Let me show you what's happening in your nervous system.

This person, call her Anna, had spent her whole life not understanding why she reacted the way she did.

Until someone mapped her patterns in body language.

[STORY_INJECTION_POINT]

Understanding the body's logic changes everything.

What might you understand differently if you knew the body's reasons?""",

"""He thought he was broken.

Years of feeling too much, reacting too fast, unable to calm down when everyone else seemed fine.

Then David learned about the nervous system.

[STORY_INJECTION_POINT]

You're not broken. Your body is doing exactly what it learned to do.

What would change if you really believed that?""",

"""She finally had words for what was happening.

That feeling when her chest tightened and her thoughts raced—it had a name. It had a mechanism. It had a reason.

[STORY_INJECTION_POINT]

Naming the body's experience doesn't fix it. But it stops you from fighting blind.

What in your body experience is finally making sense?""",

"""The patterns were obvious once he could see them.

This trigger led to that response. This sensation preceded that reaction. A whole system, operating according to rules.

[STORY_INJECTION_POINT]

The body isn't chaotic. It's systematic. Learn the system and everything becomes workable.

What patterns are becoming visible to you?""",

"""Understanding brought relief.

Not healing yet—just relief. The relief of knowing that what she'd been experiencing wasn't random, wasn't crazy, had logic.

[STORY_INJECTION_POINT]

This is the first gift of understanding: you stop fighting yourself.

What struggle could ease if you understood the body's logic?"""
            ],
            "middle": [
"""Anna practiced observing her own nervous system.

Not changing it yet—just watching. Noticing states as they rose and fell.

[STORY_INJECTION_POINT]

Observation changes the observed. Just watching your body states begins to shift them.

What do you notice when you watch?""",

"""David was learning his signals.

The way his body warned him before overwhelm. The early signs he used to miss.

[STORY_INJECTION_POINT]

The earlier you catch a state, the more options you have. Your body gives warning—if you learn to listen.

What are your early warning signs?""",

"""She could predict her reactions now.

This situation would trigger this response. Not perfectly—but well enough to prepare.

[STORY_INJECTION_POINT]

Predictability brings choice. When you know what's coming, you can meet it differently.

What predictions can you make about your body?""",

"""The system was revealing itself.

Each day brought new understanding. Each trigger another data point.

[STORY_INJECTION_POINT]

You're becoming an expert on yourself. That expertise is the foundation of change.

What expertise are you developing?""",

"""He understood why, but not yet how.

Knowing the mechanism didn't automatically give him the tools. But it pointed toward what tools he needed.

[STORY_INJECTION_POINT]

Understanding is the map. But you still have to walk the territory.

The walking comes next."""
            ],
            "resolution": [
"""Anna didn't just understand now—she could work with her system.

The knowledge had become practical. Applicable. Real.

[STORY_INJECTION_POINT]

Understanding becomes useful when it changes what you do.

How is your understanding changing your actions?""",

"""David could explain his experience to others.

Not just feel it—articulate it. The language made it real, shareable, less isolating.

[STORY_INJECTION_POINT]

When you can name your experience, you're no longer alone with it.

What can you name now that was nameless before?""",

"""She knew herself in a new way.

Body knowledge, not just head knowledge. Felt understanding.

[STORY_INJECTION_POINT]

The goal isn't just to know about your body. It's to know your body directly.

How directly do you know yourself now?""",

"""The patterns were clear, and so was the path forward.

Understanding had done its job. Time to use what he'd learned.

[STORY_INJECTION_POINT]

Understanding points the way. But you have to take the steps.

What steps are becoming clear?""",

"""Ready now for what comes next.

Armed with understanding. Prepared with knowledge. The foundation laid.

[STORY_INJECTION_POINT]

You know enough now to begin the real work.

Let's begin."""
            ]
        },
        "HEALING": {
            "opening": [
"""The first time she let herself really feel it, she cried for an hour.

Elena had been holding back tears for years. When the dam broke, her body did what it needed.

[STORY_INJECTION_POINT]

Healing often starts with finally letting yourself feel what you've been holding back.

What's waiting to be felt?""",

"""His body started to shake, and he let it.

Not trying to control it, not worried about looking strange. Marcus just let his body do what it was trying to do.

[STORY_INJECTION_POINT]

The body heals through expression. Shaking, crying, sweating—these are how stuck energy moves.

What expression is your body asking for?""",

"""Sara returned to her body slowly.

Like coming home to a house she'd abandoned. Room by room. Carefully.

[STORY_INJECTION_POINT]

Re-inhabiting a body you've been absent from takes time. There's no rushing this.

How gently can you return?""",

"""James unclenched by accident at first.

In a moment of safety he hadn't expected, his jaw released. Brief. But proof of what was possible.

[STORY_INJECTION_POINT]

The body releases when it feels safe enough. Your job is to create conditions for safety.

What conditions help you feel safe?""",

"""Maya made friends with her panic.

Not enjoying it—but no longer fighting it. Meeting it with curiosity instead of war.

[STORY_INJECTION_POINT]

The things we fight persist. The things we befriend begin to change.

What in your body are you ready to befriend?"""
            ],
            "middle": [
"""The process wasn't linear.

Elena would feel better, then worse, then different, then better again. Her body releasing in waves.

[STORY_INJECTION_POINT]

Healing doesn't follow a straight line. Trust the waves.

What wave are you on right now?""",

"""Sometimes Marcus needed to stop.

The releasing was intense. He learned to titrate—to go slowly, to rest, to let integration happen.

[STORY_INJECTION_POINT]

Slow is often faster. Pushing too hard can retraumatize rather than heal.

How can you go gently?""",

"""Sara learned to pendulate.

Between feeling and not feeling. Between sensation and rest. A rhythm that made the difficult bearable.

[STORY_INJECTION_POINT]

You don't have to stay in difficult sensation. Touch it, leave, return. That's pendulation.

Can you give yourself permission to rest?""",

"""James's healing happened in small moments.

Not dramatic breakthroughs—tiny softening. Accumulated over time.

[STORY_INJECTION_POINT]

Most healing is too small to see in the moment. But it adds up.

What small healing might be happening that you can't yet see?""",

"""Maya found she could hold more now.

Sensations that used to overwhelm were becoming tolerable. Capacity building.

[STORY_INJECTION_POINT]

This is the goal—not eliminating difficult sensation but increasing capacity to hold it.

How has your capacity grown?"""
            ],
            "resolution": [
"""Elena's body finally settled.

Not frozen—alive. Not numb—calm. A regulation she'd never known was possible.

[STORY_INJECTION_POINT]

True settling isn't suppression. It's the nervous system finding genuine safety.

What does settling feel like in your body?""",

"""Marcus lived in his body now.

Present to sensation. No longer running from what he felt. At home in his own skin.

[STORY_INJECTION_POINT]

Coming home to the body is what all this work is for.

How much more at home are you?""",

"""Sara could feel everything, and it was okay.

The return of sensation meant return of discomfort—but also joy, pleasure, aliveness.

[STORY_INJECTION_POINT]

You can't selectively numb. When sensation returns, it all returns. That's the deal.

And it's worth it.""",

"""James's jaw lived differently now.

It still clenched in moments of stress. But softened more easily. Didn't hold like before.

[STORY_INJECTION_POINT]

Healing changes your baseline. The patterns may remain, but they don't grip so hard.

What's changed in your body's baseline?""",

"""Maya graduated from panic to sensation.

What used to feel like emergency was now just... intensity. Still uncomfortable. No longer catastrophic.

[STORY_INJECTION_POINT]

This reclassification is everything. Same sensation, different relationship.

That's healing."""
            ]
        },
        "HOPE": {
            "opening": [
"""Elena noticed something different when she woke.

For years, she'd opened her eyes to immediate tension. Now there was softness. Space. Her body at rest.

[STORY_INJECTION_POINT]

The changes show up in ordinary moments. In how you wake. How you breathe. How you walk.

Where are the changes showing up for you?""",

"""Marcus found himself helping others.

Not as expert—as example. His regulated presence gave others permission.

[STORY_INJECTION_POINT]

What you've developed doesn't stay contained. It naturally overflows to those around you.

Who might be affected by your change?""",

"""Sara took up dancing.

Something she would never have done when she couldn't feel her body. Now she wanted to move, to express, to play.

[STORY_INJECTION_POINT]

A body that feels safe wants to play. Wants to move. Wants to express.

What does your body want to do now?""",

"""James laughed more easily.

Jaw unlocked. Voice freer. The sound of release expressing as joy.

[STORY_INJECTION_POINT]

As the body opens, everything opens. Even how we laugh.

What's becoming easier?""",

"""Maya trusted her body now.

Not blindly—but fundamentally. She knew it was on her side.

[STORY_INJECTION_POINT]

Trust in your body is the foundation of everything. From here, you can navigate anything.

How much do you trust your body now?"""
            ],
            "middle": [
"""Elena maintained her practice.

Not perfectly. But consistently. Knowing that the body needs ongoing care.

[STORY_INJECTION_POINT]

The body isn't a project to complete. It's a relationship to maintain.

How will you maintain yours?""",

"""Marcus hit setbacks.

Old patterns sometimes returned. But he knew the way back now.

[STORY_INJECTION_POINT]

Setbacks aren't failures. They're opportunities to practice what you've learned.

How do you handle setbacks now?""",

"""Sara kept exploring.

Each new sensation a territory to discover. The body endlessly interesting when you're present to it.

[STORY_INJECTION_POINT]

There's always more to discover in your body. The exploration never really ends.

What are you curious about now?""",

"""James shared what he'd learned.

With friends struggling like he had. Offering not advice but presence.

[STORY_INJECTION_POINT]

Healing wants to be shared. Not imposed—offered.

What do you have to offer now?""",

"""Maya lived differently in her body.

Not problem-free. Just present. Real. Embodied.

[STORY_INJECTION_POINT]

This is the goal. Not perfection—presence. Not transcendence—embodiment.

How present are you to your body now?"""
            ],
            "resolution": [
"""Elena's body was different, and so was her life.

Not that circumstance had changed. But she met it differently now. From regulation rather than reaction.

[STORY_INJECTION_POINT]

When your body changes, your whole life changes. Same circumstances, different experience.

How has your life changed?""",

"""Marcus knew this wasn't the end.

The work would continue. The body would continue to reveal itself. And he would continue to show up.

[STORY_INJECTION_POINT]

This is beginning, not end. What you've learned prepares you for what's next.

What's next for you?""",

"""Sara felt whole.

Not complete—whole. Different. Nothing missing that she needed to find. Just here, in her body, present.

[STORY_INJECTION_POINT]

Wholeness isn't completion. It's presence to what is.

Do you feel whole?""",

"""James's body told a different story now.

Not a story of tension and holding. A story of release and possibility.

[STORY_INJECTION_POINT]

Your body is writing a new story. You get to participate in authoring it.

What story is your body telling?""",

"""Maya walked differently.

You could see it. Something in how she moved through space. Less defended. More open.

[STORY_INJECTION_POINT]

The body broadcasts change. Others can see what's different even if you can't.

How might you be walking differently now?"""
            ]
        }
    }
    
    phase_scenes = scenes.get(phase, scenes["HARDSHIP"])
    position_scenes = phase_scenes.get(position, phase_scenes["opening"])
    return position_scenes[variant - 1]

# ============================================================================
# EXERCISE CONTENT - Somatic Practices (~175 words frames)
# ============================================================================

def get_exercise_content(chapter: int, section: int, variant: int, phase: str) -> str:
    positions = {4: "first", 8: "second"}
    position = positions.get(section, "first")
    
    exercises = {
        "HARDSHIP": {
            "first": [
"""Let's ground your body right now.

Feel your feet. Actually feel them—the weight of your body pressing down, the contact with the floor or your shoes, the subtle sensations in your soles.

This is the foundation. Connection to ground.

[EXERCISE_INJECTION_POINT]

Good.

Notice what's different. Even subtle grounding shifts your nervous system toward safety.

Your body knows how to be supported. We're just reminding it.""",

"""We're going to work with your breath now.

Not forcing anything dramatic—just noticing and gently shifting.

Your breath is the bridge between conscious and unconscious, between mind and body.

[EXERCISE_INJECTION_POINT]

Feel what that practice did to your body.

Breath is always available. This is a tool you carry with you everywhere.""",

"""Let's bring awareness to where you're holding.

The places in your body that grip, brace, protect.

No judgment. Just noticing and offering the possibility of softening.

[EXERCISE_INJECTION_POINT]

Whatever softened, even slightly, is significant.

The body releases when it feels safe. You just created a moment of safety.""",

"""Let's practice containment.

When sensation feels like too much, you can contain it. Give it edges. Make it manageable.

This isn't suppression—it's regulation. Working with intensity without being overwhelmed.

[EXERCISE_INJECTION_POINT]

You now have a tool for when things get too intense.

Containment isn't avoiding—it's skillful engagement.""",

"""Time for a body scan.

Slowly, systematically, we'll move attention through your body. Not to fix anything—just to know what's there.

[EXERCISE_INJECTION_POINT]

Now you have a map. You know where your body is holding, where it's open, where it's numb.

That map guides everything else."""
            ],
            "second": [
"""Let's deepen the regulation.

You've been building capacity. Now let's see what your nervous system can do with more support.

[EXERCISE_INJECTION_POINT]

Notice how much more available these states are than they were before.

Your nervous system is learning. Each practice builds on the last.""",

"""Let's integrate with movement.

Stillness practice is valuable. But the body also needs to move to process and release.

[EXERCISE_INJECTION_POINT]

Movement is medicine. Not exercise—somatic movement. Movement that serves the nervous system.""",

"""Deeper breath work now.

You've built the foundation. Let's see what's possible when we go further.

[EXERCISE_INJECTION_POINT]

Notice the states that opened up with that practice.

Breath is the master key. It opens doors nothing else can reach.""",

"""Let's work with sound.

The vagus nerve connects to your vocal cords. Sound directly stimulates the parasympathetic system.

[EXERCISE_INJECTION_POINT]

Feel the vibration still settling in your body.

Sound is an ancient tool. Your body knows what to do with it.""",

"""Integration practice now.

We're going to let everything you've learned settle into the body. No more new input—just consolidation.

[EXERCISE_INJECTION_POINT]

Good. Your nervous system is integrating.

What lands in the body stays with you."""
            ]
        },
        "HELP": {
            "first": [
"""Let's practice state identification.

Being able to know what state you're in is the foundation of self-regulation.

[EXERCISE_INJECTION_POINT]

Now you can name your state. That's the first step to changing it.

What you can identify, you can influence.""",

"""Grounding practice—with awareness of why it works.

You understand the nervous system now. Let's feel how grounding actually shifts your physiology.

[EXERCISE_INJECTION_POINT]

Can you feel how the grounding activated your ventral vagal system?

Understanding plus experience equals mastery.""",

"""Let's practice pendulation.

Moving attention between resource and activation. Teaching the nervous system it can handle both.

[EXERCISE_INJECTION_POINT]

Pendulation builds capacity. The ability to touch difficult sensation and return to safety.""",

"""Orienting practice.

This engages your social nervous system—the part that scans for safety in the environment.

[EXERCISE_INJECTION_POINT]

Notice how your body responds to knowing it's safe in the environment.

Orienting is one of the fastest ways to shift nervous system state.""",

"""Co-regulation through visualization.

Even imagining safe connection activates the social nervous system.

[EXERCISE_INJECTION_POINT]

Your body doesn't fully distinguish between imagined and real connection.

This is why visualization practices work."""
            ],
            "second": [
"""Advanced state shifting.

You can identify your state. Now let's practice deliberately moving between states.

[EXERCISE_INJECTION_POINT]

You just demonstrated that states are not fixed. You can influence them.

That's power you didn't have before.""",

"""Let's work with the vagus nerve directly.

Practices that stimulate vagal tone. Building the muscle of regulation.

[EXERCISE_INJECTION_POINT]

Feel the vagal activation. That calm? You created it.

Vagal tone is trainable. You're training it right now.""",

"""Somatic tracking practice.

Following sensation as it moves and changes. Learning the body's language.

[EXERCISE_INJECTION_POINT]

The more you track sensation, the more articulate your body becomes.

You're becoming fluent in somatic language.""",

"""Window of tolerance expansion.

Carefully, safely, expanding what you can feel without being overwhelmed.

[EXERCISE_INJECTION_POINT]

Your window just got a little bigger.

That's how capacity builds. Incrementally. Safely. Consistently.""",

"""Integration through embodiment.

Taking everything you've learned and letting it become body knowledge.

[EXERCISE_INJECTION_POINT]

Knowledge in the body is different from knowledge in the mind.

What you just felt, you now own."""
            ]
        },
        "HEALING": {
            "first": [
"""Let's practice releasing.

Not forcing—allowing. Creating conditions for the body to let go of what it's ready to release.

[EXERCISE_INJECTION_POINT]

Whatever released, released. Trust the body's timing.

Healing happens at the pace the nervous system can handle.""",

"""Self-compassion in the body.

We're going to practice meeting yourself with kindness—not conceptually, but somatically.

[EXERCISE_INJECTION_POINT]

Feel how self-compassion changes the body's state.

Kindness is a nervous system intervention.""",

"""Working with the felt sense.

That vague, whole-body feeling that's hard to name but contains so much information.

[EXERCISE_INJECTION_POINT]

The felt sense is the body's summary of everything relevant. Learning to read it is learning to read yourself.""",

"""Creating inner safety.

Building a sense of safety that doesn't depend on external circumstances.

[EXERCISE_INJECTION_POINT]

That safety? It's yours now. You can return to it anytime.

Inner safety is the foundation of all healing.""",

"""Healing breath practice.

Breath specifically oriented toward repair, restoration, integration.

[EXERCISE_INJECTION_POINT]

Healing breath is different from regulation breath. One calms; the other repairs.

You just gave your body what it needs to heal."""
            ],
            "second": [
"""Deeper release work.

With the safety you've built, we can go further. Let the body show you what it's ready to let go of.

[EXERCISE_INJECTION_POINT]

Trust what moved. The body knows what's ready to release.

You're becoming skilled at this.""",

"""Somatic forgiveness practice.

Forgiveness in the body—letting go of held resentment at the cellular level.

[EXERCISE_INJECTION_POINT]

Unforgiveness is held in the body as tension. Releasing it frees energy for healing.""",

"""Working with the healing edge.

Finding the place where you can feel fully without being overwhelmed. Staying there.

[EXERCISE_INJECTION_POINT]

The healing edge is where transformation happens.

You just spent time there. That time matters.""",

"""Integration and consolidation.

Letting everything settle. Trusting the body to organize what it's learned.

[EXERCISE_INJECTION_POINT]

Integration isn't something you do. It's something you allow.

Your body is integrating right now.""",

"""Completion practice.

Helping the body finish what was interrupted. Allowing old impulses to complete.

[EXERCISE_INJECTION_POINT]

Completion is relief. The body has been waiting to finish.

What completed, healed."""
            ]
        },
        "HOPE": {
            "first": [
"""Let's embody hope.

Not think about it—feel it. Finding hope as a body state.

[EXERCISE_INJECTION_POINT]

Hope has a physical signature. You just found yours.

This state is always available once you know how to access it.""",

"""Embodying the future self.

Feeling in your body what it will be like when the healing is further along.

[EXERCISE_INJECTION_POINT]

Your body just got a preview. That's not fantasy—it's direction.

The future is pulling you forward.""",

"""Gratitude in the body.

Finding where gratitude lives somatically. Amplifying it.

[EXERCISE_INJECTION_POINT]

Gratitude shifts physiology. You just demonstrated that.

This practice is always available.""",

"""Resource expansion.

Building the internal resources you'll need for continued growth.

[EXERCISE_INJECTION_POINT]

These resources are yours now. They don't go away.

The more you practice, the more available they become.""",

"""Opening to possibility.

Letting your body feel the full range of what's possible now.

[EXERCISE_INJECTION_POINT]

Possibility is a body state. You just opened to it.

Stay open."""
            ],
            "second": [
"""Embodied commitment.

Making a body-level commitment to continued practice. Not just deciding—feeling.

[EXERCISE_INJECTION_POINT]

A commitment felt in the body is stronger than one made only in the mind.

You just committed at the deepest level.""",

"""Connecting to support.

Feeling the support that's available—internal and external, human and larger than human.

[EXERCISE_INJECTION_POINT]

You're not alone. Your body can feel that now.

Support is always available when you remember to feel for it.""",

"""Generative practice.

Moving from receiving to generating. Becoming a source of regulation for yourself and others.

[EXERCISE_INJECTION_POINT]

You're not just healing yourself anymore. You're becoming a resource.

That's the natural progression.""",

"""Final integration.

Everything you've learned, practiced, felt—letting it all become one.

[EXERCISE_INJECTION_POINT]

Integration is complete when there's nothing separate. Just you, whole, present.

You're approaching that.""",

"""Sealing in the changes.

A practice of completion. Honoring all that's happened. Looking forward.

[EXERCISE_INJECTION_POINT]

What's sealed is yours.

Go in peace. Go in hope. Go in your body."""
            ]
        }
    }
    
    phase_exercises = exercises.get(phase, exercises["HARDSHIP"])
    position_exercises = phase_exercises.get(position, phase_exercises["first"])
    return position_exercises[variant - 1]

# ============================================================================
# REFLECTION CONTENT - Somatic (~250 words each)
# ============================================================================

def get_reflection_content(chapter: int, section: int, variant: int, phase: str) -> str:
    depths = {3: "early", 7: "deep"}
    depth = depths.get(section, "early")
    
    reflections = {
        "HARDSHIP": {
            "early": [
"""Right now, scan your body.

Start at the top of your head. Move slowly down. Face. Neck. Shoulders. Arms. Chest. Belly. Pelvis. Legs. Feet.

Don't try to change anything. Just notice.

What do you find?

For most people, this simple scan reveals surprises. Tension they didn't know was there. Numbness in unexpected places. Sensation that's been running in the background, unnoticed.

This is your body. Right now. In this moment.

The places of tension are holding something. The places of numbness are protecting something. The places of sensation are communicating something.

You don't have to decode it all right now. Just acknowledge what's here.

This is the beginning: awareness. Before any change, before any healing—awareness.

What is your body holding right now?

Not what you think it should be holding. What's actually there.

That's where we start.""",

"""Put your attention on your breath.

Don't change it yet. Just observe.

Is it shallow or deep? Fast or slow? In your chest or your belly? Smooth or jagged?

Your breath is a direct readout of your nervous system state.

Shallow chest breathing: survival mode, mobilization.
Deep belly breathing: safety mode, rest.

Most of us live in the first. So long we don't remember the second.

What does your breath tell you about your state right now?

Not what you want it to be. What it actually is.

This isn't judgment. It's information.

Your breath has been this way for reasons. Good reasons. Survival reasons.

But you're not just surviving now. You're here, doing this work.

Let your breath tell you about your history.

What story does it hold?""",

"""Notice your belly.

So much lives there. Emotion. Memory. Instinct. The so-called gut feelings that are actually body knowledge.

Is your belly soft or hard? Open or guarded? Do you allow it to move with breath, or do you hold it still?

We're taught to suck in our stomachs. To look a certain way. And in doing so, we cut off from the center of our feeling.

Your belly holds your deepest responses. The ones too primal for words.

Can you let your awareness settle there now?

Without judging what you find. Without needing to understand it.

Just presence. Just attention.

What's there?

Your belly has been waiting for you to ask.""",

"""Where do you feel fear in your body?

Not what you're afraid of—that's a story. Where the fear lives physically.

Maybe your throat tightens. Maybe your chest constricts. Maybe your legs feel weak, wanting to run.

Fear is not just a thought. It's a full-body experience. A mobilization. An ancient response designed to keep you alive.

And it lives in your body whether you acknowledge it or not.

Where is it right now?

Not to judge it. Fear is not weakness. It's intelligence. It's your body trying to protect you.

But when fear runs underground, it controls you.

When you can feel it, locate it, name where it lives—it becomes workable.

Where does fear live in you?

Find it.

That's not the enemy. That's part of you asking for attention.""",

"""Your body is speaking right now.

Every sensation is a word. Every tension is a sentence. Every pattern is a paragraph.

Are you listening?

For most of our lives, we're not. We're thinking. Planning. Worrying. Lost in the virtual world of thought while the body keeps talking to empty air.

But the body doesn't give up.

It speaks louder. The tension becomes pain. The sensation becomes symptom. The whisper becomes a scream.

Your body is speaking right now. In this moment. What is it saying?

Not what you think it should say. Not what you're afraid it might say.

What's actually being communicated?

Pause. Feel. Listen.

The body has been waiting so long for you to hear."""
            ],
            "deep": [
"""Go deeper now.

Below the surface sensations. Below the obvious tension.

What's underneath?

There's a layer of experience we rarely access. The deeper holdings. The core patterns. The places where we've organized ourselves around old wounds.

This layer doesn't reveal itself easily. It protected you for years by staying hidden.

But you're ready now. You've built enough capacity. You can look without being overwhelmed.

What's at the center of the holding?

Not the story—the sensation. Not why—what. The actual felt experience beneath everything.

It might be very old. It might not have words. It might just be a quality—a texture of experience that's been there so long you thought it was just you.

It's not you. It's something you're carrying.

Can you feel the difference?

You are not your sensations. You're the one who can feel them.

From that place, touch what's deepest.

What's there?""",

"""Find the oldest sensation.

The one that's been with you longest. The one that might predate memory.

Where does it live in your body?

This is the deep work. Below psychology. Below story. In the body itself, where experience is stored not as narrative but as pattern.

Your body remembers what your mind may not. The earliest experiences shaped your tissue before you could think about them.

And those shapes persist. In how you hold yourself. In what feels natural or foreign.

Can you feel back to the beginning?

Not thinking about it—feeling for it. In your body. In the sensations that have always been there.

What's the oldest thing you carry?

It's been waiting. Patient. Hoping that one day you'd come looking.

Today is that day.

What do you find?""",

"""At the very core, there's usually something simple.

Under all the complexity, all the layers, all the protective patterns—something basic.

A young part that just wanted safety. Or love. Or to be seen.

That part is still there. Still holding the original position. Still waiting for what it needed.

Can you feel it?

Not with your adult mind. With your body's memory. The felt sense of that younger self, still present in your tissues.

What did that young one need that they didn't get?

Don't answer with your mind. Feel for it in your body.

The answer lives there. In the shape of the holding. In the quality of the tension.

Your body knows. It's been keeping that child's position all this time.

What did they need?

This is the question at the center of everything.""",

"""There's a stillness beneath the holding.

Under the tension. Under the pattern. Under the protective layers.

A stillness that was there before any of this started.

Can you feel it?

It's your ground. Your foundation. What you were before experience shaped you.

The sensations rise and fall. The tensions come and go. But the stillness remains.

You are not your patterns. You're not even your body.

You're the awareness in which body and patterns appear.

Can you rest in that awareness now?

Let the sensations be there. Don't push them away. But don't identify with them either.

You're the space in which all this happens.

That space is untouched. Has always been untouched.

That's what you're looking for.

Can you feel it?""",

"""The deepest healing happens when you stop.

Stop fixing. Stop understanding. Stop trying.

Just be with what's here.

The body knows how to heal. It's been waiting for you to get out of the way.

All your trying, all your effort—it's been more holding, not less. Another layer of tension.

What if you just stopped?

Not collapse—presence. Attentive stillness. Being with whatever is without needing it to be different.

This is the deep work.

Not doing something to your body. Being with your body.

The body responds to this presence like a child responds to being truly seen.

It softens. It opens. It releases what it's been holding.

Not because you made it. Because you allowed it.

Can you allow now?

What happens when you stop trying to heal and just be?"""
            ]
        },
        "HELP": {
            "early": [
"""Notice your nervous system state right now.

Not what you think about it. The actual felt sense of your system in this moment.

Is there activation—energy, alertness, readiness to act?

Is there settling—calm, ease, softness?

Is there both—mixed states, contradictory signals?

Is there numbness—an absence where sensation should be?

This is the practice: learning to read your own system from the inside.

We're taught to ignore these signals. To push through regardless of state. To treat the body as a machine that should perform on demand.

But your state affects everything. Perception. Decision-making. Relationship. Creativity.

Knowing your state is knowing yourself.

What state are you in right now?

Not what you want to be. What actually is.

That's data. Use it.""",

"""Your body has a window of tolerance.

A range where you can feel without being overwhelmed. Where sensation is workable.

Outside that window—too much activation or too little—you lose access to your wisest self.

Where is your window right now?

Are you inside it—present, able to think clearly, connected to your body?

Are you above it—activated, anxious, racing, reactive?

Are you below it—numb, foggy, disconnected, collapsed?

This matters more than content. Your state determines what you can receive.

If you're outside your window, that's not failure. It's information. It means you need to regulate before proceeding.

Can you feel where you are?

The window of tolerance can expand. That's what we're building.

But first, you have to know where you are.""",

"""Track the sensation for a moment.

Pick one sensation—any one that's present now. And just track it.

Does it move? Spread? Contract?

Does it have a quality—sharp, dull, warm, cold, heavy, light?

Does it change as you observe it?

This is a skill. The skill of staying with sensation rather than fleeing into thought.

Most of us, when we feel something uncomfortable, immediately start thinking about it. Why is it there? What does it mean? How can I make it stop?

But those thoughts pull you out of body and into head.

What happens if you stay with sensation itself?

Not analyzing. Just tracking.

The body responds to attention. Often, just watching a sensation changes it.

Watch and see.

What does the sensation do when you simply observe?""",

"""Notice the difference between sensation and story.

Sensation: what's actually happening in your body right now. The raw data.

Story: what your mind says about the sensation. The interpretation.

Tightness in chest = sensation.
"I'm anxious because of the presentation tomorrow" = story.

Both are valid. But they're different.

The story might be right. Or it might be wrong. Either way, the sensation is just the sensation.

Can you separate them?

Feel the sensation without the story for a moment. Just the physical experience, without what it means.

This is surprisingly hard. The mind wants to explain, to narrative, to make sense.

But sensation doesn't need explanation. It just needs attention.

What's the pure sensation, without story?

That's where the work happens.""",

"""Your body is giving you information right now.

Are you receiving it?

There's probably sensation you're ignoring. Background discomfort you've tuned out. Signals you've overridden so many times they barely register.

But they're still there. Still broadcasting.

What are you not letting yourself feel?

Not because it's hidden—because you've learned to bypass it.

This is common. We all do it. Years of "push through" and "don't be dramatic" taught us to mute our own signals.

But the information doesn't go away. It just goes underground.

What's underground right now?

If you actually let yourself feel everything you're feeling, what would be there?

That's not weakness. That's reality.

Let yourself know what you know."""
            ],
            "deep": [
"""Go deeper into the knowing.

Your body understands things your mind doesn't. Holds wisdom that can't be spoken.

That wisdom is available right now.

Can you access it?

Not by thinking—by feeling. By sinking beneath the mental chatter into body knowledge.

Your gut knows. Your heart knows. Your bones know.

They've been knowing this whole time, while your mind spun stories.

What does your body know that your mind hasn't admitted yet?

This question might feel strange. We're not taught to trust body knowledge.

But your body was registering reality before you could think. It has direct access to truth your mind must infer.

What truth is your body holding?

Let it speak. Not in words—in sensation.

What do you know?""",

"""There's a felt sense beneath the thoughts.

A texture of experience that's more primary than language.

Can you find it?

The felt sense is how your body holds the whole of something. Not analyzed, not explained—whole. Complete. Known in a way that precedes understanding.

Right now, as you engage with all this—there's a felt sense of the whole thing.

Can you find it?

It might be vague at first. A fuzzy, hard-to-describe quality. An "aboutness" that doesn't resolve into specific thoughts.

That's exactly right. That's the felt sense.

Stay with it. Let it become clearer. Not by thinking about it—by feeling it more fully.

What is the felt sense of all this, right now, in your body?

That knowing is deeper than any concept.""",

"""Your body has an intelligence of its own.

Not thinking intelligence—body intelligence. The wisdom that knows how to heal a cut, fight infection, maintain temperature without any input from you.

That same intelligence is available for emotional healing.

Can you feel it?

It's like an inner advisor. Always present. Always working on your behalf. Usually ignored.

What is your body intelligence trying to do right now?

If you stopped interfering—stopped thinking and directing and trying—what would happen?

The body often knows the way forward. It's pulling toward wholeness constantly.

What's the pull?

Feel for it. Not as thought—as sensation. As direction. As body knowing.

Where is your body trying to go?

That's probably where you need to go too.""",

"""There's deep integration happening.

Beneath your awareness. In the background. Your system processing everything it's taken in.

Can you feel it working?

Not the content of the work—the process itself. The subtle reorganization. The shifting.

Understanding doesn't transform by being understood. It transforms by being metabolized.

And that's happening now.

Your body is taking what you've learned and making it yours. Not information you have—capacity you are.

What does that process feel like from the inside?

It's subtle. Easy to miss. But if you attend carefully, you can feel learning settling into body.

That's what lasting change is. Not new ideas—new patterns in tissue.

Feel for the settling.

Something is changing that you can't see yet.""",

"""The deepest understanding is felt, not thought.

After all the concepts, all the frameworks, all the explanations—what remains is a felt sense.

A sense of how things are. How they work. What to do.

This can't be given to you. It can only be developed through experience.

But it's developing now.

Can you feel it?

A kind of inner knowing that doesn't depend on remembering facts. That's just there. Available. Embodied.

This is the goal of all learning: felt understanding.

Not just knowing about—knowing. Direct. Immediate. In your body.

How much of what you've learned has become felt?

That's the measure. Not what you can recite—what you've become.

Feel for the difference."""
            ]
        },
        "HEALING": {
            "early": [
"""Something is softening in your body.

Can you feel it?

It might be subtle. A slight easing of tension. A small opening where there was constriction.

Healing begins this way. Not dramatic transformation. Gentle softening.

Your body is learning that it's safe to let go.

Where do you notice softening?

Scan through and look for it. The places that are slightly more relaxed than before. The holdings that have begun to release.

These small changes are significant.

Each one is your nervous system recalibrating. Learning new defaults. Proving to itself that letting go is possible.

Honor the softening.

Don't rush past it looking for bigger changes.

This is how it happens. Slowly. Gently. One soft moment at a time.""",

"""Notice what wants to move.

After all the holding, there's energy waiting to express.

Can you feel it?

Maybe a tremor. Maybe a deep breath wanting to happen. Maybe an urge to stretch, to shake, to sigh.

This is your body wanting to release.

What wants to move?

Not what you think should move—what actually wants to.

There's a difference between directing the body and following it. Direction comes from mind; following comes from trust.

Your body knows what it needs to do. It's been waiting for permission.

Can you follow rather than direct?

Feel for the impulse. The spontaneous movement that wants to happen.

And let it.

Even if it seems strange. Even if you don't understand.

Your body is leading the healing. Your job is to follow.""",

"""Pain has a message.

Not punishment—communication. Your body trying to get your attention.

What is your pain saying?

Not why it hurts. Not what caused it. The message itself.

Pain often says: "Pay attention here."

Or: "This is too much."

Or: "Something needs to change."

Can you hear what yours is saying?

When we listen to pain rather than fight it, something shifts. The fighting itself is exhausting. The resistance to what is.

What if you just listened?

Not agreeing to suffer forever. Just hearing what's being communicated.

Pain changes when it's heard.

What does your pain need you to know?""",

"""Let yourself feel the tenderness.

Beneath the tension, beneath the protection, there's something tender.

A part that's been guarding itself. That built walls because it had to.

Can you feel that tender part?

Not to fix it. Just to acknowledge it.

There's something very healing about being seen. About having your tenderness witnessed rather than judged.

Can you be a witness to your own tenderness right now?

Not with pity. Not with urgency to fix.

Just presence. Just acknowledgment.

"I see you. I know you're there. I know you've been protecting yourself. That's okay."

What does the tender part need to hear?

Offer that.""",

"""Notice what's different now compared to when you started.

Not just what you think—what you feel.

In your body right now, what has shifted?

Maybe it's subtle. A slight change in baseline. A tiny bit more ease.

Or maybe it's more obvious. Real release. Tangible change.

Either way, something has happened.

Can you acknowledge it?

We're trained to dismiss small changes. To wait for transformation before celebrating.

But transformation is made of small changes. Each one matters.

What's different?

Let yourself have it. Let it land.

You're changing. Not just learning—changing.

That's what healing is."""
            ],
            "deep": [
"""Go to the place that needs the most attention.

You know which one. The tender spot. The core wound.

Can you go there now?

Not with force. With gentleness. Like approaching a wounded animal.

Your body has been protecting this place for a long time. It won't open to aggression.

But it might open to tenderness. To patient presence.

What's at the core?

Feel your way there. Slowly. Letting your body set the pace.

You don't have to know what you'll find. You don't have to be ready.

Just be willing to be present with whatever's there.

That's enough.

What's there?""",

"""The body releases in its own way.

Sometimes it's tears. Sometimes shaking. Sometimes heat or cold or sound.

What is your body's way?

Notice the impulse when it comes. The movement that wants to happen.

Don't judge it. Don't shape it. Let it be what it is.

Release isn't pretty. It's not Instagram-worthy. It's primal and messy and exactly what needs to happen.

What's your body trying to do?

Let it.

Not performing release. Not making yourself shake or cry.

Just allowing whatever wants to come.

Your body knows how to let go.

Get out of the way and let it.""",

"""There's grief in the body.

Not just sadness—grief. The full-body response to loss.

Loss of what could have been. Loss of innocence. Loss of time spent protecting rather than living.

Can you feel the grief?

It lives in your tissues. In the years of holding. In everything that had to be sacrificed for survival.

That grief is valid. It belongs here.

Let yourself feel it.

Not to drown in it. But to honor it. To let the body do what bodies do with loss—mourn.

What are you grieving?

Not the story—the body sense of it. The weight and texture of loss in your tissues.

That grief needs to move.

Let it.""",

"""At the deepest layer, there's usually something very simple.

A young sensation. An early imprint. The original wound before it got complicated with story.

Can you feel that simple thing?

It might just be a quality. A texture. A way of being in the body that predates memory.

This is the root.

All the complexity grew from this. All the patterns were attempts to manage this simple thing.

What's the simple thing at the root?

When you find it, you don't have to do anything.

Just be with it. Just see it.

That's often enough.

The root, when truly seen, begins to release its grip.

What do you find at the root?""",

"""Rest now in the healing.

Not the doing of healing—the being of it.

You've been working. Feeling. Processing.

Now rest.

Let your body integrate what's moved. Let the changes settle.

Healing needs rest. The body needs time to reorganize.

Can you give yourself that?

Not checking out. Restful presence. Being with your body as it does its work.

You don't have to direct this part.

Just be.

Just let the healing happen.

Your body knows what to do.

Trust it.

Rest."""
            ]
        },
        "HOPE": {
            "early": [
"""Feel your body right now.

Not with the old eyes—problem-searching, flaw-finding. With new eyes.

What do you notice?

There's capacity here now. Capacity that wasn't there before.

Can you feel it?

The increased ability to be with sensation. The larger window of tolerance. The greater ease in your tissues.

This is real change. Not just feeling better—being different.

Your body has transformed.

Not dramatically. Not completely. But genuinely.

What's different?

Let yourself notice the changes. Not the distance still to go—what's already happened.

That's yours now. That doesn't go away.""",

"""Notice the openness.

Where before there was constriction, now there's space.

Where before there was bracing, now there's softness.

Where before there was numbness, now there's sensation.

Can you feel the opening?

Your body is expanding. Not physically—in capacity. In aliveness. In presence.

This is what hope feels like in the body.

Not just optimistic thoughts—an actual felt sense of possibility.

Where do you feel hope?

Not where you think about it. Where you feel it in your body.

That's hope made physical.

That's what you've built.""",

"""Your nervous system has new settings now.

Regulation is more available. Return to baseline is easier.

Can you feel that?

The old defaults are changing. New patterns are taking hold.

This isn't fragile. These are neurological changes. Real rewiring.

Your body has learned that it can feel without being overwhelmed. That it can activate and settle again. That safety is available.

That learning is in your nervous system now.

What does it feel like to have a more resilient system?

Notice the difference. The way you recover more quickly. The way intensity is more tolerable.

That's you. That's who you're becoming.""",

"""Notice how you're breathing.

Different from before, isn't it?

More full. More easy. More natural.

Your breath has changed because your nervous system has changed.

The two are inseparable.

What does your breath tell you about your state now?

Not perfect—that's not the goal. But different. Better. More regulated.

Your body is telling a new story with every breath.

A story of increasing capacity. Of growing safety. Of expanding possibility.

What story is your breath telling?

Listen.

It's a good story.""",

"""Feel your connection to your body now.

Not as observer looking at object. As inhabitant. As presence.

You're more embodied than you were.

More here. More home.

What does that feel like?

Not as concept—as sensation. The felt sense of being in your body. Present. Connected.

This is the foundation.

From here, you can meet whatever comes. Because you're here to meet it.

You're not watching your life from outside anymore.

You're living it. From inside your body. Present.

That's everything."""
            ],
            "deep": [
"""Touch the core of your body presence now.

The deepest part. The most stable ground.

What do you find?

After all this work, there's something at the center that's undisturbed. A stillness beneath all the movement.

Can you feel it?

This isn't something you built. It was always there.

The work just cleared the access.

Your essence. Your ground. The you that was there before all the patterns.

It's been waiting.

What does it feel like to touch home?

Not the home you're going to—the home that's always been here.

That's yours.

That's what all this was for.""",

"""Let your body feel its own wholeness.

Not perfection—wholeness. The sense of being complete, even with all the imperfections.

Nothing missing. Nothing to fix.

Can you feel that?

This is hard for bodies that have felt broken. The instinct is to keep looking for what's wrong.

But what if nothing is wrong?

What if your body, right now, is whole?

Not finished. Not done growing or healing or changing.

But whole. Complete in itself. Lacking nothing essential.

Feel for that.

Not as nice idea—as body sensation. The felt sense of wholeness.

It's there.

Can you find it?""",

"""Your body carries everything you've been through.

Every challenge. Every triumph. Every moment of survival.

And here you are.

Can you feel the accumulated resilience?

Not as pride—as presence. The actual felt sense of everything you've survived, held in your tissues.

Your body is wise now.

Wise from experience. From feeling. From healing.

That wisdom doesn't leave. It's part of you.

What does your wise body want you to know?

Listen.

It's been waiting to share.""",

"""Feel the possibility in your body.

Not thought possibility—felt possibility.

The sense that from here, many paths open.

Your body is a gateway now, not a prison.

What's possible from here?

Not everything is possible. You're still human, still limited, still in a body.

But more is possible than before. Much more.

Can you feel that?

The openness. The capacity. The readiness for what comes next.

That's hope in the body.

Not certainty—possibility.

That's enough. That's everything.""",

"""Rest now in what you've become.

A body that can feel. A body that can regulate. A body that can heal.

A body that's home.

Feel that.

Not what you still need to work on. Not what's not yet complete.

What you've become.

This body. This presence. This capacity.

It's real. It's yours. It's here.

Let yourself rest in that.

Not because the journey is over. Because you've arrived.

Not at a destination. At yourself.

Here. In your body. Present.

Home.

Feel it.

It's real."""
            ]
        }
    }
    
    phase_reflections = reflections.get(phase, reflections["HARDSHIP"])
    depth_reflections = phase_reflections.get(depth, phase_reflections["early"])
    return depth_reflections[variant - 1]

# ============================================================================
# TEACHERDOCTRINE CONTENT - Somatic Wisdom (~300 words)
# ============================================================================

def get_teacherdoctrine_content(chapter: int, variant: int, phase: str) -> str:
    teachings = {
        "HARDSHIP": [
"""The body keeps the score.

This isn't metaphor. Trauma literally lives in tissue. In the way muscles hold, the way breath restricts, the way the nervous system stays perpetually vigilant.

Bessel van der Kolk, who wrote the book with that title, discovered something crucial: you can't think your way out of what you didn't think your way into.

If the wound happened in the body, the healing happens in the body.

This is why talk therapy alone often fails. You can understand your patterns perfectly, have brilliant insight into their origins, and still find yourself caught in the same reactions. The mind gets it; the body hasn't changed.

The body doesn't speak in words. It speaks in tension, in breath, in the felt sense of safety or threat. To heal, you have to learn its language.

Right now, your body is speaking.

It's telling you about the unprocessed material it's holding. The experiences that didn't get completed. The emotions that were too much at the time and got stored instead of expressed.

Those stored experiences are waiting.

Not to re-traumatize you—the body is smarter than that. But to finally be felt, acknowledged, completed.

Your symptoms aren't your enemy. They're your body's attempt to communicate.

What would change if you stopped fighting your body's signals and started listening to them?

The score the body keeps isn't just of wounds.

It's also keeping score of every moment of safety, every healing breath, every time you've regulated instead of reacted.

You're adding to that score right now.

What do you want your body to remember from this moment?""",

"""Your nervous system isn't broken. It's adapted.

This is one of the most important reframes you'll ever learn.

When your nervous system keeps you in chronic stress, or collapses you into shutdown, or swings wildly between the two—it's not malfunctioning. It's doing exactly what it learned to do.

At some point, probably long ago, your nervous system received data that said: the world is dangerous. Vigilance is required. You can't afford to relax.

And it responded intelligently. It turned up the sensitivity. It shortened the fuse. It prioritized survival over thriving.

Given the input, the output makes perfect sense.

The problem is that the world may have changed, but the settings haven't updated.

You're running threat-detection software calibrated for a reality that may no longer exist. Like an alarm system that was set during a burglary and never turned down after the burglar was caught.

This is actually good news.

Because if your nervous system learned these settings, it can learn new ones. Neuroplasticity doesn't stop at childhood. Your brain and body are updating their models based on new data all the time.

The work isn't to fight your nervous system's adaptations. It's to give it new data. Consistent, repeated experiences of safety that allow the settings to recalibrate.

Every moment you spend regulated is data.

Every time you show your nervous system that it's safe and then actually stay safe—it learns.

What data have you been giving your nervous system?

What data do you want to give it now?""",

"""The vagus nerve is the body's highway between brain and body.

It's the longest nerve in your body, wandering from your brainstem all the way down to your gut—that's where the name comes from, vagus, meaning "wanderer."

And it's bidirectional. It carries signals from brain to body, but also—and this is crucial—from body to brain.

Eighty percent of vagal signals go upward.

Your body is talking to your brain far more than your brain is talking to your body.

This changes everything about how we think about mental states.

That feeling of anxiety? Largely generated by signals traveling up the vagus from your gut, heart, and lungs. Your body is telling your brain there's danger, and your brain is generating the emotional experience to match.

That sense of peace? Your body sending signals of safety. Your breathing is slow, your heart rate is regular, your digestive system is working—all of that travels up the vagus to your brain, which generates calm to match.

This is why you can't think yourself calm. The signals coming from below are louder than the signals from above.

But you can change those bottom-up signals.

Slow your breathing: different signals go up.
Relax your belly: different signals go up.
Soften your face: different signals go up.

Your body isn't just the messenger. It's the message.

Change the body, change the brain's experience.

What signals is your body sending upward right now?

And what would you like it to send instead?""",

"""In polyvagal theory, there are three states your nervous system can be in.

First: the ventral vagal state. This is safety. Connection. Social engagement. When you're here, your face is expressive, your breath is easy, you can think clearly and relate to others. This is where you want to spend most of your time.

Second: sympathetic activation. Fight or flight. Your heart rate goes up, your breathing quickens, your muscles tense for action. This is useful for actual emergencies. It's exhausting as a chronic state.

Third: dorsal vagal shutdown. When the danger is too big to fight or flee, the system collapses. Numbness. Dissociation. The feeling of not being in your body at all.

Most people with trauma cycle between the second and third states, rarely touching the first.

The work of somatic healing is to expand access to that first state. To build the capacity for ventral vagal activation. To make safety a place you can live instead of just visit.

This doesn't happen by force. You can't willpower yourself into a different nervous system state.

It happens through practice. Through repeated experiences that show your system that safety is possible. Through bottom-up interventions—breath, movement, connection—that send different signals to your brain.

You're not stuck in your state.

States are changeable. That's their nature. And with practice, you can influence which state you're in far more than you might think possible.

Where's your nervous system right now?

What would it take to move one notch toward ventral?""",

"""The body has a vocabulary of sensation.

Learning to speak this language is one of the most valuable skills you can develop.

Most people have only two words for physical experience: pain and not-pain. Everything gets sorted into these crude categories.

But the body is capable of far more nuance.

Tight, buzzy, heavy, hollow, spacious, dense, warm, cool, sharp, dull, trembling, still, electric, numb, flowing, stuck, full, empty, solid, diffuse...

Each of these words points to a different quality of sensation. And each quality is information.

Tight might mean protection. Buzzy might mean activation. Heavy might mean grief. Hollow might mean dissociation.

You don't have to interpret—in fact, it's often better not to, at first. Just learn to perceive.

The more precisely you can sense, the more precisely you can respond. Instead of "I feel bad," you can notice "there's a tight knot in my solar plexus." That specificity allows for specific intervention.

Your body has been speaking this whole time.

With a tiny vocabulary, you've only caught the headlines. The body has been saying so much more.

Expand your vocabulary.

Pay attention to the subtle qualities of sensation. Give them names, even if you have to make up the names.

The body's language is always being spoken.

What words does your body need you to learn?"""
        ],
        "HELP": [
"""The window of tolerance is your working space.

Dan Siegel introduced this concept, and it's one of the most useful maps for understanding your nervous system.

When you're inside your window, you can feel sensations without being overwhelmed. You can think clearly, make decisions, relate to others. You're regulated.

When you're above your window—hyperaroused—everything is too much. Too fast, too loud, too intense. Anxiety, panic, rage. The thinking brain goes offline and the survival brain takes over.

When you're below your window—hypoaroused—everything is too little. Numb, disconnected, foggy. Depression, dissociation, shutdown.

The goal isn't to never leave your window. That's impossible. Activation is part of life.

The goal is to expand your window and to develop skills for returning when you've left.

Window expansion happens gradually. Every time you approach the edge without going over—every time you feel intensity while staying present—your window gets a little bigger.

Return skills are what you practice in calm moments so they're available in difficult ones. Grounding, breathing, resourcing, orienting.

Know your window.

Know when you're approaching the edge. Know what pushes you over. Know what brings you back.

This self-knowledge is power.

Where's your window right now?

Are you inside it? Near the edge? Outside?

What would help you return or stay?""",

"""Neuroception is your body's subconscious risk detection.

Stephen Porges coined this term to describe something crucial: your nervous system is evaluating safety and danger before your conscious mind knows anything's happening.

Faulty neuroception is when this system gets the signal wrong.

It says danger when there's actually safety. It can't recognize safe people, safe situations. The world feels threatening even when, objectively, it isn't.

This is what happens after trauma. The neuroception gets recalibrated toward threat. Better safe than sorry, your nervous system decides. Better to see danger everywhere than to miss it once.

But living in a false alarm is exhausting.

The good news: neuroception can be recalibrated.

Through repeated experiences of actual safety. Through co-regulation with safe people. Through practices that send signals of safety from the body to the brain.

You're not paranoid. Your nervous system is doing its job based on old data.

The work is to give it new data. To show it, over and over, that safety is possible now. That the past danger has passed.

Each safe moment is an update.

Each time you notice safety and let it land—really land—in your body, you're recalibrating.

What's your neuroception telling you right now?

Is it accurate? Or is it running old programs?

What would help your system receive the update that things have changed?""",

"""Bottom-up beats top-down.

This is maybe the most practical insight from somatic psychology.

Top-down processing is thinking your way to a different feeling. "I'll just decide to be calm." "I'll tell myself everything's fine."

It rarely works. The body isn't listening to your rational arguments.

Bottom-up processing is changing your physical state to influence your mental state. Slow breathing that tells your vagus nerve you're safe. Grounding that activates your parasympathetic system. Movement that completes stress cycles.

Bottom-up works because the body is talking to the brain more than the brain is talking to the body.

When you change your breathing, you change the signals going up the vagus nerve.

When you relax your muscles, you change what your brain receives.

When you orient to your environment, you engage neural circuits that say "safe."

You can talk to yourself about calming down all day with no effect.

Or you can take three slow breaths and actually change your physiology.

Which approach have you been relying on?

What would it look like to prioritize bottom-up interventions?

Your body is listening.

Not to your thoughts about it—to how you actually treat it.

What are you teaching your body right now?""",

"""The felt sense is your body's total knowing in any given moment.

Eugene Gendlin developed Focusing, a practice built around accessing this felt sense. It's vague at first—a murky whole-body feeling that's hard to put into words.

But it contains more information than you can consciously process.

The felt sense includes everything relevant: the situation you're in, your history with similar situations, your body's current state, your emotions, your needs.

All of it, synthesized into one felt experience.

Learning to read your felt sense is like gaining access to a supercomputer you didn't know you had.

Most people ignore it. They go straight to thinking, analyzing, figuring out. But the felt sense already knows things the thinking mind will take hours to arrive at.

How do you access it?

Slow down. Let your attention drop into your body. Ask yourself: what's the whole feeling of this situation?

Wait. Don't think—sense.

Something will form. Usually in your torso. A quality of sensation that's hard to name but unmistakably there.

Stay with it. See if a word or phrase emerges that captures it.

This is intelligence your body has been offering that you've probably been ignoring.

What's the felt sense of this moment for you?

What does it want you to know?""",

"""Completion changes everything.

When a stress response gets interrupted—when you can't fight, can't flee, can't finish the defensive action—the energy stays stuck in your body.

This is incomplete stress cycles. And they're behind much of what we call chronic stress, anxiety, and trauma symptoms.

Your body is still trying to complete something that happened long ago.

The tension in your shoulders? Might be an interrupted push away.
The chronic tightness in your legs? Might be running that never got to finish.
The collapse in your chest? Might be a need to be held that was never met.

Completion doesn't require re-living the trauma. It just requires letting the body finish what it started.

A micro-movement. A gentle push. A shake. A breath that finally gets to be full.

These small completions release enormous amounts of stuck energy.

When you let your body complete, symptoms that have lasted years can shift in minutes.

What's incomplete in your body?

What action got stuck?

What would finishing feel like?

The body remembers what it needs to do.

It's been waiting for permission to complete."""
        ],
        "HEALING": [
"""Healing is not returning to who you were before.

This is a common misconception. People think healing means erasing the wound, going back to some pristine, pre-injury state.

That's not how bodies work.

When skin heals, it forms a scar. The scar is part of the body now. It's tissue that's changed, reorganized, adapted.

Psychological healing works the same way.

You won't go back to before. That person doesn't exist anymore. Instead, you become someone new—someone who has been through something and integrated it.

The wound becomes part of your story, not the end of it.

This is actually better than "going back."

The person you were before didn't have the wisdom you're gaining now. Didn't have the capacity you're building. Didn't have the depth that comes from having touched the bottom and come back up.

You're not being restored to factory settings.

You're being upgraded.

The healing process adds something, not just removes damage.

What wisdom has your wounding given you?

What capacity are you developing that you wouldn't have otherwise?

Who are you becoming through this process?

That's the person worth becoming.

Not who you were before.

Who you're becoming now.""",

"""The body heals itself. Your job is to stop interfering.

This is harder than it sounds.

Bodies have an innate intelligence—the same intelligence that heals cuts, fights infections, and regulates temperature without conscious input. This intelligence extends to emotional and psychological healing.

Given the right conditions, the body moves toward health.

What are the right conditions? Safety. Rest. Attention. Time.

What interferes? Forcing. Rushing. Ignoring. Demanding results on a timeline.

Most people with trauma try to heal through effort. They work hard at it. They push through pain. They override the body's signals in the name of progress.

This often backfires.

The body heals at its own pace. Pushing doesn't help—it creates more activation, more defensive responses.

What helps is creating optimal conditions, then getting out of the way.

Slow down.
Make space.
Pay attention.
Trust.

Your body knows how to heal. It's been healing your whole life.

What it needs from you is cooperation, not management.

Where have you been interfering with your own healing?

What would trusting the body's wisdom look like?

Sometimes the best thing you can do is less.""",

"""Kintsugi is the Japanese art of repairing broken pottery with gold.

Instead of hiding the cracks, kintsugi highlights them. The repaired piece becomes more beautiful and more valuable than the original, unbroken version.

The philosophy underneath: nothing is ever truly broken. What breaks can be made whole, and the wholeness can be more precious than what was lost.

Your healing can work this way.

The cracks in your psyche, the fractures in your trust, the breaks in your sense of self—these don't have to be hidden or minimized.

They can be filled with gold.

The gold is your attention. Your compassion. The wisdom you've gained.

The cracks become part of the beauty, not evidence of damage.

This reframe changes everything about how you relate to your wounds.

They're not shameful. They're not proof that you're broken beyond repair.

They're places where light can enter. Places where something new can be added that makes you more than you were before.

What gold are you filling your cracks with?

What would it mean to be proud of your scars?

The broken places are where transformation happens.

Not despite the breaking—through it.""",

"""In trauma healing, there's a principle: pendulation.

This means oscillating between activation and resource. Touching into the difficult, then returning to safety. Again and again.

Why pendulation works: it teaches the nervous system that activation isn't forever. That there's a way back. That intensity doesn't have to be overwhelming.

Trauma often involves getting stuck. Stuck in activation without resolution. Stuck in shutdown without return.

Pendulation unsticks.

You touch the edge of activation—just the edge—then you return to calm. The system learns: I can go there and come back.

Next time, you can go a little further.

This is how capacity builds. Not by forcing yourself through the entire traumatic experience, but by gradually expanding how much you can feel while staying present.

Pendulation works with the body's natural rhythms. Everything in nature oscillates—heartbeat, breath, day and night. Healing oscillates too.

Don't stay in the difficult material too long. Don't avoid it entirely.

Touch and return. Touch and return.

Where do you need to touch today?

And do you know the way back to resource?

Both matter. Both are part of the practice.""",

"""Co-regulation precedes self-regulation.

This is a fundamental truth of nervous systems.

We don't learn to regulate ourselves first and then extend that to relationships. We learn regulation through relationships first, and then internalize it.

This is why human contact is so important for healing.

Your nervous system is designed to be regulated by other nervous systems. When you're in the presence of a calm, safe person, their regulation transmits to you.

You can feel this. Around certain people, you naturally settle. Around others, you become activated.

This isn't weakness—it's design.

The problem is when early relationships didn't offer good co-regulation. When the people who should have been safe were sources of threat. The nervous system didn't get to learn what regulation feels like.

The solution involves receiving good co-regulation now. From therapists, from friends, from any safe presence.

Let yourself be regulated by others. Let yourself take in their calm.

This isn't dependency—it's repair.

The regulation you receive from others becomes internalized. It becomes the template for regulating yourself.

Who in your life offers good co-regulation?

How often do you let yourself receive it?

This is medicine.

Don't be too proud to take it."""
        ],
        "HOPE": [
"""Your nervous system will never be the same. That's the good news.

Neuroplasticity—the brain's ability to change in response to experience—doesn't stop at any age.

Every time you practice regulation, you're building neural pathways.

Every time you stay present with difficult sensation, you're expanding capacity.

Every time you choose to breathe instead of react, you're strengthening new patterns.

These changes are physical. Actual neurons. Actual connections. Actual shifts in how your nervous system operates.

You're not just managing symptoms. You're rewiring the system that generates them.

This takes time. Neural change doesn't happen overnight. But it happens.

And it accumulates.

The you who finishes this journey will be neurologically different from the you who started. Not metaphorically—literally.

New pathways built. Old patterns weakened. Different default settings.

This is why hope isn't naive.

It's based on the actual physics of nervous systems. On the scientific fact that brains change.

Your brain is changing right now.

What pathways are you building?

What patterns are you reinforcing?

The neuroplasticity is happening whether you direct it or not.

Why not direct it toward what you want?""",

"""The body that learned threat can learn safety.

This is the foundation of everything.

Your nervous system's current settings—the hypervigilance, the shutdown, the dysregulation—were learned. They developed in response to experience.

Which means they can change in response to new experience.

This isn't theory. It's been demonstrated in thousands of studies, millions of clients. Trauma responses that seemed permanent, shifting. Nervous systems that seemed broken, finding new baselines.

It's not quick. It's not linear. But it's real.

Your body is capable of learning safety.

Not believing safety. Not understanding safety. But feeling safety at the deepest level.

That's what you're working toward. Not managing chronic symptoms forever. Actually rewiring the system so that safety becomes default.

It's possible.

It happens.

Will it happen for you?

That's not entirely under your control. But what is under your control is showing up. Practicing. Giving your nervous system the data it needs.

The body learns from experience.

What experiences are you giving it?""",

"""Post-traumatic growth is real.

It's not toxic positivity. It's documented phenomenon.

People who go through trauma and process it don't just return to baseline. Many end up with greater depth, wisdom, and capacity than they had before.

Greater appreciation for life.
Deeper relationships.
Expanded sense of what's possible.
New understanding of their own strength.

This isn't because trauma is good. Trauma is terrible.

But humans are meaning-making creatures. We transform what happens to us.

The wound becomes the teacher.
The breakdown becomes the breakthrough.
The worst thing becomes the source of the best things.

This doesn't minimize what you've been through. It acknowledges your power to alchemize it.

You are not just surviving trauma. You're capable of transforming it.

What growth is emerging from your struggle?

What wisdom has the wound given you?

What becomes possible because of what you've been through, not in spite of it?

Post-traumatic growth.

It's your birthright.

Claim it.""",

"""There's a you on the other side of this.

Not an imaginary you. A real you. One who has done the work, built the capacity, integrated the material.

That you isn't fundamentally different from who you are now. They're not a stranger.

They're you, continued. You, developed. You, without the chronic activation that's been making everything harder.

Can you feel that future self?

Not see them—feel them. In your body.

What would it feel like to be regulated most of the time?

What would it feel like to trust your own capacity?

What would it feel like to be at home in your own body?

Those states aren't fantasy. They're where you're headed.

Your future self is pulling you toward them. Every practice, every breath, every moment of awareness moves you closer.

Who are you becoming?

Not in general—specifically. What states are becoming more available? What reactions are becoming less automatic?

Track the change.

It's happening.

You're on your way to meet yourself.""",

"""The work continues, but it changes.

In the beginning, healing feels like work. Effort. Something you have to remember to do.

Eventually, it becomes how you live.

Not special practices—though those remain valuable. But an ongoing orientation toward embodiment. A continuous relationship with your nervous system.

The intensity decreases. The drama decreases. What remains is a kind of embodied presence that doesn't require special circumstances.

You just live in your body.

Aware of its states. Skilled at regulation. Able to feel fully without being overwhelmed.

This is the goal.

Not perfect regulation—that doesn't exist. But capacity. Range. The ability to meet whatever arises.

You're closer to this than you might realize.

The practices are becoming natural. The awareness is becoming automatic. The body is becoming home.

What would it be like to just be in your body?

Not working on it. Not healing it. Just being in it.

That's where you're headed.

That's what's possible.

You're already on the way."""
        ]
    }
    
    return teachings.get(phase, teachings["HARDSHIP"])[variant - 1]

# ============================================================================
# EXERCISE CONTENT - Somatic (~175 words frame for injection)
# ============================================================================

def get_exercise_content(chapter: int, section: int, variant: int, phase: str) -> str:
    positions = {4: "first", 8: "second"}
    position = positions.get(section, "first")
    
    exercises = {
        "HARDSHIP": {
            "first": [
"""Let's ground you in your body right now.

This is the foundation of all somatic work—the ability to come back to the body, to feel your feet on the floor, your weight supported, your breath moving.

From this ground, everything else becomes possible.

[EXERCISE_INJECTION_POINT]

Good.

What did you notice? Where is your body now compared to where it was?

Grounding isn't about feeling good. It's about feeling present.

Whatever you found, that's your starting point.""",

"""Let's explore your breath together.

The breath is the doorway. The most direct access to your nervous system.

Without changing anything, just notice how you're breathing right now.

[EXERCISE_INJECTION_POINT]

Your breath tells your history.

What did you discover? What patterns live in your breathing?

This awareness itself is valuable. Before you can change anything, you have to know what is.""",

"""Let's do a body scan.

Slow, deliberate attention moving through your entire body.

Not to fix. Not to judge. Just to know what's here.

[EXERCISE_INJECTION_POINT]

What did you find?

The body is always communicating. The scan just tunes you in.

Whatever you discovered, that's real information about your state right now.""",

"""Let's practice tracking sensation.

This is the skill underneath all skills—the ability to stay with sensation without fleeing into thought.

Pick one sensation, any sensation. We're going to stay with it.

[EXERCISE_INJECTION_POINT]

How was that?

Staying with sensation is harder than it sounds. The mind wants to escape into story.

But sensation is where the body lives. And it's where healing happens.""",

"""Let's find your ground.

Wherever you are—sitting, standing, lying down—there's support beneath you.

Can you feel it?

[EXERCISE_INJECTION_POINT]

The ground is always there.

In moments of overwhelm, this is your anchor. The earth is holding you right now, and always.

That's not metaphor. That's physics. And your body can feel it."""
            ],
            "second": [
"""Let's go deeper now.

You've built some awareness. Now let's expand it.

This practice builds on what came before.

[EXERCISE_INJECTION_POINT]

Notice how much more is available now.

Each practice opens more. Capacity builds on capacity.

What's available now that wasn't at the beginning?""",

"""Let's work with what you're holding.

Not to force release—to invite it. To create conditions where letting go becomes possible.

[EXERCISE_INJECTION_POINT]

What moved?

Release can't be forced. But it can be invited.

Your body knows what it needs to let go of. The practice just opens the door.""",

"""Let's integrate what's been stirred up.

A lot has moved today. Now we consolidate.

[EXERCISE_INJECTION_POINT]

How are you now?

Integration is essential. Without it, insight remains unembodied.

You're not just learning—you're changing.""",

"""Let's practice regulation.

The ability to shift your nervous system state intentionally.

This is a skill. And it improves with practice.

[EXERCISE_INJECTION_POINT]

How did that affect your state?

Regulation is power. The ability to be with intensity without being overwhelmed.

You're building that power right now.""",

"""One more practice to seal the work.

Everything we've done today, consolidating in your body.

[EXERCISE_INJECTION_POINT]

Take a breath.

What you just practiced is now more available. More yours.

The body learns through repetition. This practice is now part of your repertoire."""
            ]
        },
        "HELP": {
            "first": [
"""Let's map your nervous system.

Not theoretically—directly. Feeling your own states from the inside.

[EXERCISE_INJECTION_POINT]

What did you notice about your system?

Mapping your nervous system is power. When you know your states, you can work with them.

That knowledge is now in your body, not just your mind.""",

"""Let's practice reading your body's signals.

The subtle communications you usually override.

[EXERCISE_INJECTION_POINT]

What signals were there that you don't usually notice?

Your body is always communicating. The practice is learning to listen.

What you just did is the foundation of body wisdom.""",

"""Let's explore your window of tolerance.

Finding where you can feel without being overwhelmed.

[EXERCISE_INJECTION_POINT]

Where is your edge?

Knowing your window is essential. Healing happens inside the window, not outside it.

You now have a felt sense of your own capacity.""",

"""Let's track the layers.

Surface sensation, then deeper, then deeper still.

[EXERCISE_INJECTION_POINT]

What did you find at each layer?

The body has depth. Surface isn't all there is.

You're learning to access your own depth.""",

"""Let's practice state awareness.

Knowing where you are in any given moment.

[EXERCISE_INJECTION_POINT]

How aware are you of your state now?

This awareness becomes automatic with practice.

You're training your attention to include your body."""
            ],
            "second": [
"""Let's deepen your understanding through experience.

What you've learned conceptually, now feel directly.

[EXERCISE_INJECTION_POINT]

What's different when you feel it rather than just know it?

Concepts become real through body experience.

That's what just happened.""",

"""Let's practice applying your understanding.

Not in theory—in your actual body, right now.

[EXERCISE_INJECTION_POINT]

What did application feel like?

Understanding that stays in your head doesn't change much.

Understanding in your body changes everything.""",

"""Let's integrate the new knowing.

What you've learned becoming who you are.

[EXERCISE_INJECTION_POINT]

Let it settle.

Integration takes time. But it's happening.

You're becoming what you've learned.""",

"""Let's consolidate before moving on.

Everything we've covered, landing in your body.

[EXERCISE_INJECTION_POINT]

What's solid now?

The foundation is set. The body knows what the mind learned.

That's real progress.""",

"""One final practice for understanding.

Sealing knowledge into body wisdom.

[EXERCISE_INJECTION_POINT]

Good.

What lives in your body now that didn't before?

That's the measure of real learning."""
            ]
        },
        "HEALING": {
            "first": [
"""Let's create conditions for healing.

Not forcing anything—inviting.

[EXERCISE_INJECTION_POINT]

What did your body do when given space to heal?

The body knows how to heal. The practice creates conditions.

Whatever happened, that's your body's wisdom in action.""",

"""Let's practice gentle release.

Not forcing discharge—allowing it.

[EXERCISE_INJECTION_POINT]

What released?

Release comes in its own time. The practice opens the door.

Trust what happened.""",

"""Let's work with compassion.

Directing kindness toward your own body.

[EXERCISE_INJECTION_POINT]

How did compassion feel in your body?

Self-compassion isn't indulgence. It's the condition healing requires.

You just gave yourself something precious.""",

"""Let's practice pendulation.

Moving between sensation and rest.

[EXERCISE_INJECTION_POINT]

How was that rhythm?

Pendulation prevents overwhelm. Touch difficulty, then rest.

You now have a tool for working with intensity.""",

"""Let's create safety in your body.

The foundation for all deep work.

[EXERCISE_INJECTION_POINT]

Where does safety live in your body now?

Safety isn't permanent. But it can be accessed.

You just found the door."""
            ],
            "second": [
"""Let's go deeper into healing.

Building on the safety you've created.

[EXERCISE_INJECTION_POINT]

What moved in that deeper work?

Deeper work requires foundation. You've built it.

Trust what your body did.""",

"""Let's allow completion.

Whatever got interrupted, finishing now.

[EXERCISE_INJECTION_POINT]

What completed?

Completion is the body doing what it couldn't do before.

Whatever happened was exactly right.""",

"""Let's integrate the healing.

What's moved becoming permanent change.

[EXERCISE_INJECTION_POINT]

How is your body settling?

Integration anchors change. Without it, healing doesn't last.

You're sealing what's shifted.""",

"""Let's resource your system.

Building capacity to hold what's been released.

[EXERCISE_INJECTION_POINT]

What resources are available now?

Resources are what let you hold more. You have more now.

That's real change.""",

"""Final healing practice for now.

Letting everything settle.

[EXERCISE_INJECTION_POINT]

Rest now.

Healing continues even when practice ends.

Your body is working on your behalf."""
            ]
        },
        "HOPE": {
            "first": [
"""Let's practice embodied hope.

Not hoping with your mind—with your body.

[EXERCISE_INJECTION_POINT]

Where does hope live in your body now?

Hope isn't just a thought. It's a body state.

You just found yours.""",

"""Let's expand what's possible.

Your capacity is larger now. Let's feel how large.

[EXERCISE_INJECTION_POINT]

What's available that wasn't before?

Capacity expands through use. You just expanded yours.

That expansion is real.""",

"""Let's practice presence.

Full presence in your body, right now.

[EXERCISE_INJECTION_POINT]

How present are you?

Presence is the goal. Not perfection—presence.

You just practiced being here.""",

"""Let's resource for the future.

Building reserves for whatever comes.

[EXERCISE_INJECTION_POINT]

What resources did you find?

These resources are yours now. They go with you.

You're more prepared than you were.""",

"""Let's anchor the changes.

Everything you've become, stabilized in your body.

[EXERCISE_INJECTION_POINT]

What's anchored now?

Anchoring makes change permanent. What's anchored stays.

That's yours to keep."""
            ],
            "second": [
"""Let's deepen the embodiment.

More fully here. More fully home.

[EXERCISE_INJECTION_POINT]

How at home are you in your body now?

Home isn't somewhere else. It's here.

You're arriving.""",

"""Let's practice sustainable presence.

The kind you can maintain, day after day.

[EXERCISE_INJECTION_POINT]

What does sustainable presence feel like?

This isn't about peak states. It's about baseline.

Your baseline is shifting.""",

"""Let's integrate everything.

All the work. All the change. Landing now.

[EXERCISE_INJECTION_POINT]

Let it settle.

Integration completes the cycle.

You've done the work. Now let it become you.""",

"""Let's prepare for what's next.

Body ready. Resources available. Capacity online.

[EXERCISE_INJECTION_POINT]

Are you ready?

Ready doesn't mean certain. It means capable.

You're capable now.""",

"""Final practice.

Presence. Wholeness. Home.

[EXERCISE_INJECTION_POINT]

Here you are.

In your body. Present. Whole.

That's everything.

Go live it."""
            ]
        }
    }
    
    phase_exercises = exercises.get(phase, exercises["HARDSHIP"])
    position_exercises = phase_exercises.get(position, phase_exercises["first"])
    return position_exercises[variant - 1]

# ============================================================================
# INTEGRATION CONTENT - Somatic Synthesis (~220 words)
# ============================================================================

def get_integration_content(chapter: int, variant: int, phase: str) -> str:
    integrations = {
        "HARDSHIP": [
"""Let's feel where you are now.

You started this chapter with your body speaking in ways you might not have been hearing. Tension, breath, sensation—all of it carrying messages.

Now you've listened. Really listened.

That changes things.

Your body knows it's been heard. Can you feel the difference? Maybe a slight settling. Maybe just the tiniest softening.

That's what happens when we acknowledge what the body has been carrying.

We haven't fixed everything. That's not the goal of one chapter. But we've started a conversation.

The body has been waiting for this conversation.

Take a moment to thank your body. Literally. Silently say thank you for all you've been holding.

Feel what happens when you offer appreciation instead of criticism.

The next chapter goes deeper. We'll learn why the body responds the way it does. We'll get maps for the territory we're navigating.

But first, feel this moment. Feel what's already changed.

Your body is paying attention.

It knows this is different.""",

"""Notice your breath right now.

Compared to when you started—is it any different? Even slightly?

That's the measure of the work. Not dramatic transformation. Small shifts in baseline.

You've asked your body to trust you. To let you pay attention to what it's holding.

That's a big ask.

Bodies that have been ignored for years don't trust immediately. They need consistency. They need proof that this time will be different.

You've given a little proof today.

Keep giving it.

What comes next is understanding. The why behind what you're feeling. Maps that make the territory less frightening.

But the real work is always here: in the body, in this moment.

Breathe again.

Feel what's here.

That's the practice.

That's enough.""",

"""The chapter closes. Your body continues.

Everything that happened in these pages is now part of your body's experience. The attention you paid, the sensations you noticed, the practices you tried.

Integration happens automatically. Your nervous system is processing.

Let it.

Don't rush to the next chapter. Don't fill the space with activity.

Let there be a moment of just being in your body.

No agenda. No practice. Just presence.

What is your body like when you're not trying to change it?

That's valuable information. That's baseline.

From here, we build. More understanding. More practices. More capacity.

But we always come back to this: just being present with what is.

Take one more breath.

Then, whenever you're ready, continue.""",

"""Something is different in your body now.

You paid attention. That always changes things.

Maybe the tension is the same. Maybe the pain is still there. But your relationship to it has shifted.

You're with it now, not just in it.

That's the beginning of everything.

This chapter introduced you to listening. The chapters ahead will give you more tools.

But the foundation is here: willingness to feel. Courage to stay present. Trust that the body knows something important.

You've built that foundation.

Feel it beneath you.

Solid. Present. Yours.

From here, anything is possible.""",

"""Before you go further, pause.

Feel your body's state right now.

Not judging it. Not changing it. Just acknowledging: this is where I am.

That acknowledgment matters more than you might think.

Your body has been carrying without acknowledgment for a long time. Just being seen—just being felt—is a form of care.

You've offered care today.

The next chapters offer more: understanding, tools, healing. But none of that works without this basic willingness to be present.

You've demonstrated that willingness.

You're ready for what comes next.

Take a breath. Feel your body.

Continue when you're ready."""
        ],
        "HELP": [
"""Your body makes more sense now.

You've learned why it does what it does. The survival logic underneath the symptoms.

That changes your relationship to everything.

Instead of fighting your nervous system, you can work with it.

Instead of asking "what's wrong with me," you can ask "what is my system protecting me from?"

This reframe is everything.

Feel your body right now. Feel it with understanding.

The tension isn't random. The breath pattern makes sense. The activation is adaptation.

Your body has been intelligent all along.

The next chapters move from understanding to healing. From knowing what's happening to changing it.

But you needed this first. You needed to see that your body isn't the enemy.

Feel that shift.

It's foundational.""",

"""Understanding lives in the body now.

The concepts you've learned aren't just ideas anymore. You've felt them. You've experienced them in your own nervous system.

That's a different kind of knowing.

Felt knowledge doesn't fade like intellectual knowledge. It becomes part of your body's vocabulary.

You know what activation feels like—not just conceptually.

You know what regulation feels like—not just as a word.

This knowledge is yours now.

Carry it forward.

The healing chapters will ask you to apply what you know. You're ready for that.

Feel your readiness.

It's real.""",

"""The map is clearer now.

You know the territory better. The landscape of your nervous system has been charted.

That doesn't mean the terrain is easy. But at least you can navigate.

Where am I? What state is this? What does my system need?

These questions have answers now.

Feel your body right now with this new understanding.

What do you know about it that you didn't know before?

That knowledge is power. Not power over your body—power with it.

Collaboration instead of conflict.

The healing ahead depends on this collaboration.

You're ready for it.""",

"""Before moving to healing, consolidate.

Let the understanding settle. Let it become body knowledge.

Rush, and it stays intellectual. Let it settle, and it becomes part of you.

So pause here.

Feel your nervous system right now.

Notice what you can notice now that you couldn't before.

That new awareness is the fruit of this chapter.

It will support everything that comes next.

Integration. Healing. Hope.

All of it builds on understanding.

You have that now.

Let it settle.

Then continue.""",

"""The foundation is complete.

You know what's happening in your body and why.

That's not the end—it's the beginning.

Understanding is the foundation. Healing is the building.

Are you ready to build?

Feel your body's answer.

If it's yes, proceed. If it's not quite, take more time.

The body's readiness matters.

When you're ready—and only then—turn to healing.

The practices ahead will make sense because of what you've learned.

The healing ahead will work because you understand the system.

You're prepared.

Feel that preparation.

Then go."""
        ],
        "HEALING": [
"""Something has healed.

Feel for it. Not with your mind—with your body.

Is there more space somewhere? A little more ease? A breath that goes deeper than it used to?

These small changes are the evidence of real healing.

Your nervous system is reorganizing.

You can't force this. You can only create conditions and then notice what happens.

What happened?

Whatever healing occurred will continue. Integration keeps working after you stop practicing.

Trust that.

The next chapter moves toward hope. Toward what becomes possible when healing is underway.

But first, acknowledge what's happened here.

Your body is different than when you started.

Feel that difference.

Honor it.""",

"""Healing is happening. Can you feel it?

Not dramatic transformation—subtle shift. The body doing what bodies do when they're finally given the chance.

You gave your body a chance.

That matters.

The healing will continue on its own schedule. Bodies don't heal at the pace we want them to. They heal at the pace they can.

Your job now is to keep creating conditions. Keep practicing. Keep showing up.

And to notice what's changing.

What's changed?

Name it, even if it's small. Especially if it's small.

The small changes are where healing lives.

The hope chapters ahead will show you where this goes. What becomes possible.

You're ready to see that.

You've earned it.""",

"""Before looking forward, look at where you are.

Really feel your body right now.

Compared to before the healing chapter—what's different?

More settled? More spacious? More able to feel without being overwhelmed?

Whatever's different is real. It's not going away.

Neural change has happened. Capacity has been built.

You're not where you started.

Let that land.

Then, and only then, look toward hope.

Hope built on felt experience is different from hope that's just wishful thinking.

You have felt experience now.

Feel it.

Then proceed.""",

"""Healing doesn't end when the chapter ends.

What's been set in motion continues.

Your body is processing, integrating, reorganizing. It will keep doing that.

Your job is to not interfere. To trust the process. To keep conditions favorable.

This means rest. Kindness. Patience.

Can you offer those to yourself?

The hope chapters ahead are about what becomes possible. About the future you're creating.

But that future is built on what's happening now—in this moment of integration.

Feel this moment.

It's creating your future.""",

"""The healing section closes.

Your body is different than when it opened.

Take a moment to appreciate that. Real appreciation, felt in the body.

Gratitude changes physiology. It's another form of healing.

What are you grateful for?

Feel it.

From this place of gratitude and healing, the hope chapters will make more sense.

Hope grounded in body experience is the most real kind.

You have that experience now.

Carry it forward.

See what becomes possible."""
        ],
        "HOPE": [
"""Feel what's possible in your body now.

Not what you think is possible—what you can feel.

States that weren't available before. Range that didn't exist. Capacity you've built.

This is real.

Your body has learned things. Your nervous system has changed.

The hope isn't naive—it's earned.

What does your body feel is possible?

Trust that feeling. It's based on actual experience.

You've come far.

And the journey continues. But now you know where you're going.

Feel the direction.

Feel the hope.

That's yours to keep.""",

"""The work continues, but differently now.

What was effort becomes practice becomes nature.

The practices that felt awkward become automatic.

The awareness that took concentration becomes background.

The body that felt foreign becomes home.

This is integration at its deepest.

Feel your body right now.

Is it feeling more like home?

That's the destination. Not a place you reach once. A quality of relationship with yourself.

You're developing that relationship.

Keep developing it.

The practices continue. But they're different now.

Less work, more living.

That's where you're headed.""",

"""Before closing, feel everything at once.

Your body as it is right now. The capacity it has. The healing that's happened. The hope that's present.

All of it. At once.

This is integration.

Not separate pieces—one whole.

You are one whole.

Feel that wholeness.

It's been there all along. Under the fragmentation.

Now you can feel it.

This doesn't go away. Wholeness is what you are.

Remember this feeling.

Come back to it.

It's always here.

You're always whole.""",

"""This journey ends. Your life continues.

The practices remain available. The understanding stays with you. The capacity you've built is permanent.

Your body is different.

Feel the difference.

That's not nothing. That's everything.

Where you go from here is up to you. The tools are yours. The wisdom is yours.

Use them.

Not as special practices—as a way of living.

In your body. Present. Regulated. Alive.

That's what's possible now.

Live it.""",

"""One final moment.

Feel your body. Just as it is. Right now.

All the work. All the practice. All the healing.

Here you are.

Not fixed. Not finished. But different.

More yourself than when you started.

That's what this was for. Not to become someone else. To become more fully who you've always been.

Feel who you are.

In your body. In this moment.

That's home.

You're home.

Go in peace.

Go in your body.

Go."""
        ]
    }
    
    return integrations.get(phase, integrations["HARDSHIP"])[variant - 1]

# ============================================================================
# FILE GENERATION LOGIC
# ============================================================================

def compute_fingerprint(content: str) -> Dict[str, int]:
    char_count = len(content)
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    paragraph_count = len(paragraphs)
    sentence_count = sum(1 for char in content if char in '.!?')
    return {
        "char_count": char_count,
        "paragraph_count": paragraph_count,
        "sentence_count": sentence_count
    }


def get_content_for_section(chapter: int, section: int, section_type: str, variant: int, phase: str) -> str:
    content_getters = {
        "HOOK": lambda: get_hook_content(chapter, variant, phase),
        "SCENE": lambda: get_scene_content(chapter, section, variant, phase),
        "REFLECTION": lambda: get_reflection_content(chapter, section, variant, phase),
        "EXERCISE": lambda: get_exercise_content(chapter, section, variant, phase),
        "TEACHERDOCTRINE": lambda: get_teacherdoctrine_content(chapter, variant, phase),
        "INTEGRATION": lambda: get_integration_content(chapter, variant, phase)
    }
    return content_getters.get(section_type, lambda: f"Content for {section_type}")()


def create_variant_file(chapter: int, section: int, section_type: str, variant: int, purpose: str, phase: str) -> Dict[str, Any]:
    type_lower = section_type.lower()
    family = f"f{variant}"
    variant_id = f"ch{chapter:02d}_sec{section:02d}_{type_lower}_{family}"
    
    content = get_content_for_section(chapter, section, section_type, variant, phase)
    fingerprint = compute_fingerprint(content)
    
    scene_type = None
    if section_type == "SCENE":
        positions = {2: "opening", 5: "middle", 9: "resolution"}
        scene_type = positions.get(section, "narrative")
    
    return {
        "variant_id": variant_id,
        "chapter": chapter,
        "section": section,
        "section_type": section_type,
        "purpose": purpose,
        "variant_family": f"F{variant}",
        "content": content,
        "fingerprint": fingerprint,
        "metadata": {
            "persona": "Adult Professional",
            "topic": "Somatic Healing",
            "section_type": section_type,
            "scene_type": scene_type,
            "location_tokens": []
        }
    }


def generate_template():
    print("=" * 60)
    print("Audiobook Template Generator V2 SOMATIC")
    print("Body-Centered Healing - All Phases Complete")
    print("=" * 60)
    print(f"\nOutput: {OUTPUT_ROOT}")
    
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    registry = {"sections": {}}
    total_words = 0
    chapter_words = {}
    section_type_words = {}
    
    for chapter in range(1, NUM_CHAPTERS + 1):
        chapter_key = f"chapter_{chapter:02d}"
        phase = CHAPTER_PHASES[chapter]
        title = CHAPTER_TITLES[chapter]
        
        print(f"Ch{chapter:02d} ({phase[:4]}): {title}...", end=" ")
        
        chapter_dir = OUTPUT_ROOT / chapter_key
        chapter_dir.mkdir(exist_ok=True)
        
        registry["sections"][chapter_key] = {
            "chapter": chapter,
            "title": title,
            "phase": phase,
            "sections": {}
        }
        
        chapter_word_count = 0
        
        for section_info in SECTION_STRUCTURE:
            section_num = section_info["num"]
            section_type = section_info["type"]
            purpose = section_info["purpose_template"].format(phase=phase.lower())
            
            section_key = f"section_{section_num:02d}"
            section_id = f"ch{chapter:02d}_sec{section_num:02d}"
            type_lower = section_type.lower()
            
            section_dir = chapter_dir / f"{section_key}_{type_lower}"
            section_dir.mkdir(exist_ok=True)
            
            story_eligible = section_type == "SCENE"
            exercise_eligible = section_type == "EXERCISE"
            
            scene_type = None
            if section_type == "SCENE":
                positions = {2: "opening", 5: "middle", 9: "resolution"}
                scene_type = positions.get(section_num, "narrative")
            
            registry["sections"][chapter_key]["sections"][section_key] = {
                "section_id": section_id,
                "section": section_num,
                "type": section_type,
                "purpose": purpose,
                "scene_type": scene_type,
                "min_variants_required": NUM_VARIANTS,
                "story_eligible": story_eligible,
                "exercise_eligible": exercise_eligible,
                "variants": [],
                "metadata": {
                    "persona": "Adult Professional",
                    "topic": "Somatic Healing",
                    "section_type": section_type,
                    "scene_type": scene_type,
                    "location_tokens": []
                }
            }
            
            for variant in range(1, NUM_VARIANTS + 1):
                variant_data = create_variant_file(chapter, section_num, section_type, variant, purpose, phase)
                
                word_count = len(variant_data["content"].split())
                chapter_word_count += word_count
                
                if section_type not in section_type_words:
                    section_type_words[section_type] = []
                section_type_words[section_type].append(word_count)
                
                family = f"f{variant}"
                variant_file = section_dir / f"{family}.yaml"
                
                with open(variant_file, 'w', encoding='utf-8') as f:
                    yaml.dump(variant_data, f, default_flow_style=False, allow_unicode=True, width=1000, sort_keys=False)
                
                registry["sections"][chapter_key]["sections"][section_key]["variants"].append({
                    "variant_id": variant_data["variant_id"],
                    "variant_number": variant,
                    "variant_family": f"F{variant}",
                    "fingerprint": variant_data["fingerprint"],
                    "location_tokens": []
                })
        
        chapter_words[chapter] = chapter_word_count
        total_words += chapter_word_count
        print(f"{chapter_word_count:,} words")
    
    registry_file = OUTPUT_ROOT / "registry.yaml"
    with open(registry_file, 'w', encoding='utf-8') as f:
        yaml.dump(registry, f, default_flow_style=False, allow_unicode=True, width=1000, sort_keys=False)
    
    # Statistics
    total_variants = NUM_CHAPTERS * len(SECTION_STRUCTURE) * NUM_VARIANTS
    words_per_path = total_words / NUM_VARIANTS
    words_per_chapter_path = words_per_path / NUM_CHAPTERS
    
    injected_per_chapter = 3 * 800 + 2 * 800  # 4,000 words
    total_with_injections = words_per_path + (NUM_CHAPTERS * injected_per_chapter)
    audio_hours = (total_with_injections / 150) / 60
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    
    print(f"\nFiles: {total_variants} variants + 1 registry = {total_variants + 1} files")
    
    print(f"\nSection type averages (words per variant):")
    for stype, words_list in sorted(section_type_words.items()):
        avg = sum(words_list) / len(words_list)
        print(f"  {stype:16s}: {avg:6.0f}")
    
    print(f"\nBase prose (per assembled path):")
    print(f"  Total: {words_per_path:,.0f} words")
    print(f"  Per chapter: {words_per_chapter_path:.0f} words")
    
    print(f"\nWith injections (3×800 story + 2×800 exercise):")
    print(f"  Per chapter: {words_per_chapter_path + injected_per_chapter:.0f} words")
    print(f"  Total book: {total_with_injections:,.0f} words")
    print(f"  Audio: ~{audio_hours:.1f} hours @ 150 wpm")
    
    print(f"\nChapter breakdown (base + inject = total):")
    for ch in range(1, NUM_CHAPTERS + 1):
        phase = CHAPTER_PHASES[ch]
        per_path = chapter_words[ch] / NUM_VARIANTS
        total = per_path + injected_per_chapter
        print(f"  Ch{ch:02d} ({phase[:4]}): {per_path:4.0f} + {injected_per_chapter} = {total:,.0f}")
    
    print(f"\nOutput: {OUTPUT_ROOT}")
    print("=" * 60)


if __name__ == "__main__":
    generate_template()

# ============================================================================
# TEACHERDOCTRINE CONTENT - Somatic (~300 words each)
# ============================================================================

def get_teacherdoctrine_content(chapter: int, variant: int, phase: str) -> str:
    teachings = {
        "HARDSHIP": [
"""The body keeps the score.

This isn't metaphor. It's biology.

Every experience you've had is recorded in your tissues. Not as memory in the ordinary sense—as pattern. As shape. As the way you hold yourself, breathe, move.

Your posture tells your history. Your breath tells your level of safety. Your tension patterns reveal what you've been bracing against, consciously or not.

The body doesn't forget.

This might sound like bad news. All that pain, all that difficulty, stored in your cells.

But there's another way to see it: the body is honest.

While the mind can rationalize, minimize, explain away—the body tells the truth. It holds reality even when we're not ready to face it.

This is why healing must include the body.

You can understand your patterns perfectly. You can have brilliant insights about why you are the way you are.

But if the body doesn't change, nothing really changes.

The patterns persist. The reactions continue. The same old responses run on automatic.

Real healing is body healing.

Not ignoring the mind—including the body. Understanding the body's language. Working with its wisdom.

Your body has been trying to help you this whole time.

Carrying what you couldn't face. Storing what you couldn't process. Protecting you with patterns that made sense.

It's time to work with that body instead of against it.

It's time to let the body's truth become conscious.

It's time to heal from the inside out.""",

"""There's a wisdom in your nervous system older than thought.

For millions of years, bodies have been surviving. Fighting. Fleeing. Freezing when fight and flight weren't possible.

This survival intelligence is in you.

It doesn't speak in words. It speaks in sensation. In impulse. In the lightning-fast reactions that happen before your conscious mind even knows there's a decision to make.

When you feel fear rising, that's ancient wisdom mobilizing resources.

When your body goes numb in overwhelm, that's an old, old protection activating.

When you can't think clearly under stress, that's blood flowing to limbs instead of brain—preparing for action.

None of this is malfunction.

It's intelligent design, operating exactly as intended.

The problem isn't the nervous system's responses. The problem is when those responses don't match current reality.

When the body treats a difficult email like a physical threat.

When a raised voice triggers the same response as mortal danger.

When you can't calm down even when you're safe.

The nervous system isn't wrong. It's applying lessons learned in the past to situations in the present.

The work isn't to override this system. That doesn't work.

The work is to update it. To give it new experiences. To teach it that now is different from then.

Your body can learn.

The same intelligence that learned to protect can learn to relax.

But not through thought alone. Through experience.

New experience, in the body, that proves to the nervous system that safety is available.

That's what we're doing here.""",

"""Trauma is what happens when the body can't complete its response.

Something overwhelming occurs. The body mobilizes. Fight or flight energy surges.

And then—for whatever reason—action isn't possible.

You can't run. Can't fight. Can't do what the body desperately wants to do.

So the energy gets stuck. Stored. Held in the tissue.

This is the physiology of trauma. Not a psychological weakness. Not a failure to cope. A biological reality.

The body started something it couldn't finish.

And it's been waiting to finish ever since.

This explains so much.

Why talk therapy alone doesn't always work.

Why understanding your trauma doesn't necessarily resolve it.

Why the same triggers keep triggering, year after year.

The body doesn't care about your insights. It cares about completing its response.

When that response finally completes—when the held energy finally discharges—something profound happens.

The trauma resolves. Not intellectually. Physiologically.

The body finally does what it wanted to do. And then it can let go.

This is the somatic approach.

Not understanding trauma better. Completing the interrupted response.

Not managing symptoms. Allowing resolution.

Your body has been waiting to finish what it started.

That's what we're here for.""",

"""Breath is the bridge.

Between conscious and unconscious. Between mind and body. Between control and surrender.

Your breath is the only autonomic function you can also control voluntarily.

Heartbeat runs on automatic. Digestion runs on automatic.

But breath—breath you can take over. Or you can let it happen on its own.

This makes breath the doorway.

When you change your breath, you change your nervous system state. Directly. Immediately. Without having to think or understand anything.

Slow, deep breath activates relaxation response.

Fast, shallow breath activates stress response.

The body doesn't know the difference between danger that causes rapid breathing and rapid breathing that mimics danger.

This is power.

Not positive thinking. Not visualization. Actual physiological change, available through the simple act of breathing differently.

The breath you're taking right now is affecting your nervous system.

The next breath you take will affect it again.

Every breath is a choice. A signal. An instruction to your body about what kind of state to be in.

Most of us have been sending stress signals for years. Unconsciously. Through our unconscious breathing patterns.

But you can change this.

Not by trying to breathe "right." By bringing awareness to breath. By noticing what is. By gently inviting deeper, slower, fuller breath.

The bridge works both directions.

Breathe like you're safe, and you begin to feel safe.

That's not pretending. That's physiology.

Use it.""",

"""The container matters more than the content.

Everyone wants to work on content. The specific traumas. The particular patterns. The stories of what happened.

But the container—your capacity to hold experience—that's what determines everything.

A small container overflows with small difficulty.

A large container holds even great intensity without spilling.

Building the container is the first work. Often the most important work.

What is the container?

It's your nervous system's capacity to handle activation without overwhelm.

It's your ability to feel strong sensation and stay present.

It's the window of tolerance—how much you can experience and still function.

With a small container, even minor triggers cause flooding. You get overwhelmed. Dissociate. Can't think clearly.

With a large container, you can feel more. Hold more. Work with more.

This is why going slowly matters.

Every time you touch difficulty and don't get overwhelmed, your container grows.

Every time you feel intensity and stay present, you build capacity.

Every time you surf a wave of sensation rather than drowning, you're expanding what you can hold.

This is the real work.

Not excavating trauma. Building capacity to hold whatever you find.

Container first. Then content.

Your container is growing right now. With every breath. With every moment of staying present.

Trust the process."""
        ],
        "HELP": [
"""Your nervous system has three main modes.

Understanding this changes everything.

First: mobilization. The gas pedal. Fight or flight. Heart racing, muscles tense, energy surging.

Second: immobilization. The shutdown. Freeze, collapse, dissociation. When fight and flight aren't possible, the body plays dead.

Third: social engagement. The optimal zone. Calm but alert. Connected. Able to think and relate and be present.

Most of us oscillate between the first two, rarely touching the third.

Stuck on the gas pedal: anxiety, anger, restlessness. Can't calm down.

Stuck in shutdown: depression, numbness, disconnection. Can't engage.

The goal isn't to live in any one state. It's to have access to all of them—and the ability to shift between them as needed.

Sometimes you need mobilization energy. When there's real danger. When action is required.

Sometimes you need to rest and recover. That's immobilization, in healthy doses.

But social engagement—calm connection—that's where we want to spend most of our time.

The practices we're doing here are designed to build access to that third state.

Not by forcing calm. By gradually teaching the nervous system that it's available.

Every time you self-regulate, you're building a path to social engagement.

Every time you find calm in the midst of difficulty, you're proving it's possible.

Your nervous system is learning.

Which state do you spend the most time in?

Where would you like to be?""",

"""Co-regulation precedes self-regulation.

This is one of the most important things to understand about nervous systems.

We don't learn to regulate alone. We learn through relationship. Through contact with regulated others.

As infants, we had no ability to calm ourselves. We relied entirely on caregivers. Their regulated presence taught our nervous systems what regulation felt like.

For those who had attuned caregivers, this worked well enough. Their systems learned.

For those who didn't, the learning was incomplete. Self-regulation never fully developed.

This isn't character flaw. It's biology.

If your caregivers were dysregulated, absent, or frightening, your nervous system couldn't learn from them.

It did its best. Developed strategies for managing without support. But it missed the fundamental lesson of what calm safety feels like.

This is why relationship is so important in healing.

Not just any relationship—regulated relationship. Contact with nervous systems that feel safe.

This could be a therapist. A friend. A partner. Even a pet.

What matters is the felt sense of another nervous system saying: "It's okay. I'm here. You can relax."

Your nervous system is still learning. It can still receive this lesson.

And once you've learned it in relationship, you can internalize it.

The external regulation becomes internal capacity.

That's the path.

Co-regulation first. Then, gradually, self-regulation.

Who helps you regulate?""",

"""The felt sense is your body's way of knowing.

It's not emotion exactly. Not sensation exactly. Something between and beneath.

A vague, fuzzy, hard-to-articulate sense of how things are.

When you have a "gut feeling" about something—that's felt sense.

When something just doesn't "feel right" but you can't say why—that's felt sense.

When you know something in your body before you know it in your mind—that's felt sense.

This is a different kind of knowing than thinking.

Thinking analyzes, categorizes, explains.

Felt sense knows directly. Immediately. Holistically.

Both are valuable. But felt sense is often more accurate.

Your body is processing vastly more information than your conscious mind can handle. The felt sense is the summary. The headline.

Learning to access felt sense is one of the most powerful skills you can develop.

It means having access to your body's wisdom. To the intelligence that's been watching and evaluating while your mind was busy with other things.

How do you access felt sense?

You pause. You turn attention inward. You ask "how does this feel in my body?" and then you wait.

Not for a thought. For a sense. A quality. A something.

It might be vague at first. With practice, it becomes clearer.

Your felt sense is available right now.

What does it say?""",

"""Pendulation is the art of moving between states.

In and out. Toward difficulty and away. Feeling and resting.

This is how the nervous system heals without overwhelm.

If you stay too long in difficult sensation, you get flooded. The system overloads. Defenses go up. Learning stops.

But if you never touch difficulty at all, nothing changes. The patterns remain unchallenged.

Pendulation is the middle way.

Touch the edge of difficulty. Feel it. Let it be real.

Then pull back. Orient to the room. Feel your feet. Find something pleasant or neutral to rest attention on.

Then return. Go a little deeper maybe.

Then rest again.

This rhythm—approach and retreat, feeling and resting—this is how the container expands safely.

You're not overwhelming the system. You're gently stretching it.

Like physical stretching, there's an optimal intensity. Enough challenge to create change. Not so much that you injure.

Pendulation teaches the nervous system that difficulty can be felt without being permanent. That intensity rises and falls.

This is a fundamental lesson.

And it can only be learned through experience.

Every time you pendulate successfully, you're building capacity.

Approach. Retreat. Approach. Retreat.

That's the rhythm of healing.""",

"""Resources are what let you hold more.

A resource is anything that helps you feel more present, more capable, more regulated.

It could be internal: a memory, an image, a felt sense of strength.

It could be external: a person, a place, an object that helps you feel safe.

Resources are what you call on when intensity rises. What you return to in pendulation. What builds your container.

Most people have more resources than they realize.

They just haven't identified them. Haven't practiced accessing them. Don't know how to use them in moments of difficulty.

Take a moment: what are your resources?

What memories feel strengthening?

What places feel safe?

What people feel regulating?

What parts of your body feel stable?

These are resources. And they're available anytime.

When the going gets hard, you don't have to white-knuckle through. You can call on resources. Deliberately remember that person, that place, that feeling.

Your nervous system responds.

Resources don't make difficulty disappear. They make it tolerable.

With resources, you can stay present to things you couldn't face alone.

That's how healing happens.

Not in overwhelm. In resourced contact with difficulty.

What resources will you call on today?"""
        ],
        "HEALING": [
"""Healing is a verb, not a destination.

You don't arrive at healed. You practice healing.

Every day. Every moment of choosing presence over avoidance. Every time you meet sensation with compassion rather than war.

This isn't bad news. It's freedom.

You don't have to get somewhere specific. You just have to keep showing up. Keep practicing. Keep choosing.

The body responds to this consistency.

Not to intensity. Not to dramatic breakthroughs.

To consistent, gentle attention. Day after day.

Like water wearing stone.

What you're building isn't a final state. It's a practice. A way of being with yourself.

This practice becomes easier over time. More natural. More automatic.

But it's always practice.

Even the masters still practice.

This is liberating when you really understand it.

You're not failing if you haven't arrived. There's no arrival.

You're succeeding every time you choose to show up.

Every moment of practice is healing.

Including this one.""",

"""The body heals through expression, not suppression.

What's held wants to move.

That's the nature of held energy. It's not static. It's dynamic, compressed, waiting for release.

When we suppress—when we push down, ignore, override—the energy doesn't disappear. It gets more compressed.

When we express—when we let the body do what it wants to do—the energy moves through.

Expression doesn't have to be dramatic.

It might be a sigh. A slight shudder. A deep breath that comes from nowhere.

It might be tears that arrive without a clear reason.

It might be the urge to stretch, to shake, to make sound.

These are expressions. The body releasing what it's been holding.

Your job is to allow them.

Not to perform them. Not to force release.

But when the body shows you what it wants to do, to let it.

This is counterintuitive. We're trained to hold it together. To not make a scene.

But holding it together is what created the problem.

Expression is the way out.

Let the body move. Let the sounds come. Let the tears flow.

Trust the body's wisdom.

It knows how to heal itself, if you let it.""",

"""Self-compassion isn't optional.

The nervous system doesn't heal under attack.

When you meet your experience with harshness—when you criticize yourself for having the patterns you have—you're creating more stress. More activation. More for the body to hold.

Healing requires safety.

And part of safety is how you relate to yourself.

If your inner voice is critical, judging every reaction, impatient with the pace of change—your nervous system can't settle. It's under constant internal threat.

But if your inner voice is kind—if it says "this is hard, and you're doing your best"—the system can relax. Can open. Can heal.

This isn't spiritual bypass. It's biology.

Self-compassion creates the conditions healing requires.

You're not letting yourself off the hook. You're giving yourself what you need to actually change.

How do you speak to yourself when you're struggling?

Would you speak that way to a friend?

What would it sound like to be kind?

That kindness isn't luxury. It's medicine.

Your nervous system needs to know you're on its side.

Show it.""",

"""Integration happens in the pauses.

We're action-oriented creatures. We want to do something. Make something happen.

But healing doesn't work that way.

The doing stirs things up. The pausing lets them settle.

Without integration time, you just keep stirring. Never settling. Never actually changing.

Think of it like exercise.

The workout tears muscle fibers. The rest rebuilds them stronger.

Without rest, there's only damage.

Same with somatic work.

The practices activate. They bring material to the surface. They move energy.

But the real change happens after. In the integration. When the system reorganizes around new experience.

This is why more isn't always better.

Why intense retreats can sometimes backfire.

Why slow, steady practice often works better than dramatic interventions.

Give yourself integration time.

After a practice, rest. After an insight, let it settle. After tears, just be.

The healing is happening in the quiet.

Trust the pause.""",

"""The wound and the healing are in the same place.

This is one of the deepest teachings.

The very thing you've been avoiding—the sensation, the memory, the pattern—that's where the healing lives.

Not around it. In it.

This is why avoidance doesn't work long-term.

You can manage symptoms forever. But until you turn toward the wound itself, nothing fundamentally changes.

This doesn't mean diving in recklessly.

The approach must be resourced. Careful. Respectful of your capacity.

But at some point, you have to go where it hurts.

And when you do—when you finally bring presence to the place you've been protecting—something remarkable happens.

The wound that looked permanent reveals itself as healable.

The sensation that seemed unbearable becomes workable.

The pattern that felt like "just who you are" turns out to be optional.

The healing was waiting inside the wound.

It always was.

Are you ready to go where it hurts?

That's where freedom lives."""
        ],
        "HOPE": [
"""You're becoming someone new.

Not in the future—right now.

Every moment of practice has changed you. Literally. Neurologically.

New pathways have formed. New defaults are establishing. New possibilities live in your tissue.

This isn't metaphor.

Your brain has reorganized around your new experiences. Your nervous system has recalibrated based on what you've shown it.

You're not the same person who started this work.

The change might be subtle from the inside. Gradual shifts are hard to notice in the moment.

But compare who you are now to who you were before.

The increased capacity. The greater ease. The enhanced ability to be present.

That's real. That's permanent. That's you.

And the becoming continues.

Every practice from here continues the transformation. Every moment of choosing presence over avoidance builds the new pattern.

You're becoming someone who can feel without being destroyed.

Someone who can meet difficulty with presence.

Someone who lives in their body rather than fleeing from it.

That's who you're becoming.

And there's no going back.

The new neural pathways don't disappear just because you stop practicing. They're part of you now.

Who you're becoming is already here.

Feel it.""",

"""The body doesn't lie.

All the changes you've made—they show.

Not just in how you feel. In how you move. How you breathe. How you hold yourself.

Your posture is different.

Your breath is different.

Your baseline is different.

These aren't things you can fake. They're the physical evidence of transformation.

Others will notice even if you don't.

Something in how you show up. A quality of presence. A felt sense of groundedness.

This isn't about looking good. It's about being different.

When your nervous system changes, your whole presentation changes.

The tension that used to shape your face softens.

The holding that used to restrict your breath releases.

The bracing that used to define your shoulders drops.

This is visible. Palpable. Real.

You're not just feeling better.

You're different.

And that difference radiates.

Into your relationships. Your work. Your whole life.

Changed from the inside out.

That's what body work does.

That's what you've done.""",

"""Your healing spreads.

Not because you preach or teach. Because nervous systems communicate.

When you're regulated, others feel it.

When you're present, others can relax.

When you're at home in your body, others have permission to come home too.

This isn't woo-woo. It's neuroscience.

Mirror neurons. Limbic resonance. The constant nonverbal communication between nervous systems.

Your state affects others' states.

Which means your healing is already rippling outward.

To your family. Your friends. Your colleagues. Strangers on the street.

Each regulated nervous system in a dysregulated world is medicine.

You don't have to do anything special.

Just be what you've become. Present. Regulated. In your body.

That presence is contagious.

Not in words. In energy. In the felt sense others get just being around you.

This is contribution.

Not through effort. Through being.

Your healing isn't just for you.

It's for everyone you touch.""",

"""The body knows the way forward.

You've been looking for direction. Wondering what's next.

But your body already knows.

It's pulling toward something. Toward more aliveness. More expression. More of what you came here to do.

Can you feel that pull?

It might be subtle. An inclination. A leaning.

But it's there. The body's compass pointing toward life.

When you're connected to your body—really connected—you don't have to figure out what to do.

You feel what wants to happen. And you follow.

Not blindly. With discernment.

But trusting that the body's impulses toward life are worth listening to.

What's your body pulling toward?

Not what you think you should do. What actually wants to happen.

That wanting is wisdom.

It's your body's vote for your future.

It's been pointing the way all along.

Now you can hear it.

Now you can follow.""",

"""Home is here.

After all the seeking. All the work. All the transformation.

Home is where it always was.

In your body. In this moment. In the simple fact of being present.

You've been looking for something to complete you. Some final state. Some arrival.

But you're already complete.

Not perfect. Complete.

Everything you need is here. In this body. In this breath.

Home isn't somewhere you're going.

It's where you're standing.

When you're in your body—really in it—you're home.

When you're present to sensation—all of it—you're home.

When you're not fighting what is—you're home.

This is the destination that isn't a destination.

The arrival that's always available.

The home that was never lost.

You're home.

Right now.

Feel it.

In your body.

Here.

You're home."""
        ]
    }
    
    return teachings.get(phase, teachings["HARDSHIP"])[variant - 1]

# ============================================================================
# INTEGRATION CONTENT - Somatic (~220 words each)
# ============================================================================

def get_integration_content(chapter: int, variant: int, phase: str) -> str:
    integrations = {
        "HARDSHIP": [
"""Let's gather what just happened in your body.

You started this chapter carrying something. Maybe you didn't have words for it—but your body knew.

Through sensation, breath, and attention, you began to acknowledge what's there.

Not fix it. Not explain it. Just... acknowledge.

That's significant.

For years, maybe decades, you've been overriding body signals. Pushing through. Pretending everything was fine.

Today, you stopped. You listened. You let your body be heard.

What shifted as a result?

Maybe something loosened. Maybe something intensified before it settled. Maybe you just feel more... here.

All of these are right.

This is the beginning: awareness. Before healing, awareness. Before change, acknowledgment.

You've begun.

And your body knows it.

Something has shifted in your tissues, even if you can't name it yet.

Take this with you: the willingness to listen.

The next chapter builds on this foundation.

But for now, just feel where you are.

Presence to what is. That's the practice.

You're in it now.""",

"""Before we close this chapter, feel your body.

What's different from when you started?

Even small shifts matter.

You've done something counterintuitive today. Instead of trying to escape the feeling, you turned toward it. Instead of managing symptoms, you got curious about sensation.

That's a different orientation. A different relationship.

Your body registered that.

It noticed that you showed up. That you listened. That you were willing to feel what's here.

This builds trust. Body trust.

The body that's been ignored, overridden, criticized—it just received attention. Respect.

That matters more than any insight.

Let yourself appreciate what you've done.

Not because it was easy—it wasn't.

Because it was brave.

Turning toward what hurts is always brave.

And you did it.

Rest now. Let what's moved continue to settle.

When you're ready, the next chapter awaits.

It builds on this foundation. This willingness. This capacity.

You're ready for what's next.

Your body is ready.""",

"""Pause here.

Before moving forward—pause.

Feel what's happened.

Integration needs time. The body needs space to reorganize around new experience.

So don't rush ahead.

Let the breath be easy. Let the body settle.

What are you aware of right now?

Whatever's there, that's what's true for you in this moment.

You've started something important.

The acknowledgment of body experience. The willingness to feel rather than flee.

This is foundational.

Everything that follows depends on this.

But this—what you've done today—this is already something.

Your body has been waiting to be heard.

Today, you listened.

The next chapter goes deeper. More understanding. More tools.

But the foundation is presence.

And you've touched presence.

That's enough.

That's everything.

Rest here.

Then, when you're ready, continue.""",

"""Something has started that can't be stopped.

Once you've begun to feel your body—really feel it—you can't fully un-feel.

Awareness expands. It doesn't contract back to where it was.

You might try to ignore the signals again. To push through like before. But now you'll know you're doing it.

That knowing changes everything.

This is the first fruit of the work: expanded awareness.

You're more conscious of your body now than you were before.

Of the holding. The tension. The patterns.

And of the possibility that things could be different.

That awareness is a gift.

Even when it's uncomfortable. Even when you'd rather not feel what you're feeling.

Awareness is the precondition for change.

Without it, you're running blind.

With it, you have options.

You have options now.

What you do with them—that's the rest of the journey.

But the awareness, once kindled, doesn't go out.

It's yours now.

Use it.""",

"""Here's what your body now knows.

You showed up.

You paid attention.

You didn't run.

Those three things—showing up, paying attention, not running—they're the essence of this work.

And you did them.

Your body registered that.

At some level, your system learned: "I can feel difficult things and survive. I don't have to flee every sensation."

That's learning. Real learning. Body learning.

It's the foundation for everything.

You didn't just consume information today. You had an experience. A body experience.

That experience lives in you now. Changes you.

Not dramatically. Subtly. But really.

The next chapter builds on this.

More experience. More capacity. More change.

But this—what you did today—this matters.

Your body knows something new.

And bodies don't forget.

Go forward holding that.

The work continues."""
        ],
        "HELP": [
"""You understand more now.

Not just intellectually—somatically. In your body.

The concepts we've explored aren't just ideas. They're maps of your own territory.

Your nervous system. Your patterns. Your body's logic.

These aren't abstract. They're you.

And now you know more about how you work.

This knowing doesn't automatically change anything.

But it changes your relationship to what's happening.

Before, you might have been lost in the experience. No map. No language.

Now, you have orientation.

"Oh, this is my nervous system mobilizing."
"Oh, this is a survival pattern from way back."
"Oh, this is my body protecting me."

That "oh" is freedom.

It's the space between stimulus and response.

Take this understanding into the next chapter.

It becomes the foundation for actual change.

But understanding alone—what you've built here—it's already valuable.

You're no longer lost.

You have a map.

And the territory is becoming familiar.""",

"""Let what you've learned settle into your body.

Understanding can live in the head forever and change nothing.

Or it can drop down. Into tissue. Into pattern.

That drop is what we're working toward.

You've taken in information. Concepts. Framework.

Now let it land.

Not through more thinking. Through rest.

The body integrates through rest.

So let the ideas be. Stop churning them.

Feel your body right now.

What wants to settle?

Integration isn't something you do. It's something you allow.

You allow by resting. By being. By not trying so hard.

The understanding will become embodied.

Not all at once. Gradually.

And then one day you'll respond differently without thinking about it.

That's embodied knowing.

That's what we're building.

But it starts with rest.

Let it settle.

The next chapter will ask more of you.

Rest now.""",

"""Knowledge becomes power through practice.

You now know things about your body you didn't know before.

But knowing isn't enough.

The question is: will you use what you know?

Understanding your nervous system is step one. Working with it is step two.

You've built the map. Now comes the journey.

The next chapter is about healing. About actually changing patterns. About allowing the body to do what it needs to do.

But it builds on this foundation.

The understanding you've developed here makes that work possible.

You can't work with what you don't understand.

Now you understand.

So: are you ready to do the work?

Not just learn about healing. Actually heal.

That's what's next.

It asks more of you. It might be uncomfortable.

But you have what you need.

Understanding. A map. A framework.

And a body that's been waiting.

It's ready.

Are you?""",

"""Before moving to healing, consolidate what you've learned.

Not by reviewing. By feeling.

Where does this knowledge live in your body now?

Is it still just in your head? Or has it started to drop down?

The concepts we've explored—nervous system states, felt sense, pendulation, resources—they're not abstract.

They're describing your experience. Your body.

Can you feel them as yours?

Not as interesting ideas. As personal reality.

This is the shift we're working toward.

From knowing about to knowing directly.

The healing chapter will ask you to apply this knowledge.

To work with sensation rather than just understanding it.

To allow change rather than just preparing for it.

This chapter gave you the tools.

The next chapter asks you to use them.

Take a breath.

Feel your body.

You're more prepared than you might think.

Forward now.

Into healing.""",

"""Understanding is the map. Healing is the territory.

You've been studying the map. Learning the landscape. Getting oriented.

That preparation matters.

But at some point, you have to enter the territory.

That's what's next.

The healing chapter isn't about more understanding.

It's about experience. About allowing. About letting the body do what it knows how to do.

Understanding supports that. Makes it safer. Gives you orientation when things get confusing.

But understanding alone doesn't heal.

Body experience heals.

And that's where we're going.

Are you ready?

Not perfectly ready. No one is ever perfectly ready.

But ready enough.

You understand enough.

You've built enough foundation.

Now the body takes over.

Trust it.

It's been waiting for this.

Into the territory now.

Healing awaits."""
        ],
        "HEALING": [
"""Something has healed.

You might not feel dramatically different.

But something has shifted in your body. Something that was stuck is more fluid. Something that was closed is more open.

That's real.

Not metaphor. Actual change in your tissue.

The work you've done here—the practices, the allowing, the presence—it's changed you.

Your nervous system has new experience now.

Experience of feeling difficult things and surviving.

Experience of releasing what's been held.

Experience of meeting yourself with compassion.

These experiences are now part of you.

They'll continue to work even when you're not paying attention.

Integration happens in the background.

So don't worry if you don't feel transformed.

Transformation is happening.

The body is reorganizing around what it's learned.

Be patient with yourself.

The changes will become visible.

In how you respond. In what triggers you. In your baseline.

Give it time.

Something has healed.

You'll see.""",

"""The healing doesn't stop when this chapter ends.

What's been activated keeps moving.

What's been released keeps clearing.

What's been learned keeps integrating.

This is important to understand.

Healing isn't something you do in sessions and then stop.

It's a process that continues.

Your job is to support that process.

Rest when you need to.

Move when your body wants to.

Don't override the signals.

The body is doing its work.

Your work is to not get in the way.

This might feel passive. We're trained to effort, to try, to make things happen.

But healing asks for trust.

Trust that the body knows what it's doing.

Trust that what was started will complete.

Trust that you're okay.

The healing continues.

With or without your conscious attention.

But with your support, it goes easier.

Support yourself.

Rest.

Let it happen.""",

"""Before we move to hope, honor what's happened.

You've done something significant.

You've turned toward what hurts. You've stayed present to difficult sensation. You've allowed your body to release what it's been holding.

This isn't easy work.

Most people avoid it their whole lives.

You didn't.

That courage matters.

And your body knows it.

It's responding to the fact that you showed up. That you trusted it. That you didn't abandon yourself.

This builds something important: a relationship.

A relationship between you and your body.

Where before there might have been war, now there's alliance.

Where before there might have been avoidance, now there's willingness.

This relationship is the foundation for everything.

From a body you trust, you can meet anything.

That's what you've built.

Not perfection. Not completion.

A relationship.

And that relationship continues to grow.""",

"""What wants to grow from what you've healed?

That's the question as we transition to hope.

Healing isn't just about removing suffering.

It's about creating space for something new.

When the wound takes up less space, other things become possible.

Creativity. Connection. Contribution. Joy.

What's becoming possible for you?

Feel for it in your body.

Not what you think should be next. What actually wants to happen.

There's an impulse there. A pull toward something.

That pull is your body's wisdom.

It knows where it wants to go.

Now that there's less pain, less holding, less constriction—where does the energy want to flow?

That's hope made physical.

Not optimistic thoughts. Actual body impulse.

The next chapter explores this.

What's possible now.

But already, you can feel it forming.

Something wants to grow.

Let it.""",

"""The body heals in spirals.

This chapter ends, but the process continues.

You'll revisit this territory again. Find new layers. Release more.

That's not failure to complete. That's how it works.

Each pass through goes deeper.

Each round finds more.

Until one day, you realize you're different.

Not because one session changed everything.

Because a hundred small shifts accumulated.

You're in that accumulation now.

This chapter was one pass through.

There will be others.

And each one will find a body more capable, more resourced, more healed than the last.

Trust the spiral.

Trust the slow accumulation.

Trust that it's working even when you can't see it.

The hope chapter awaits.

It builds on everything you've done.

Carry your healing forward.

It's yours now.

Forever."""
        ],
        "HOPE": [
"""You've arrived somewhere new.

Not a destination. A capacity.

The capacity to be in your body.

To feel what you feel.

To meet what comes.

That's not where you started. That's earned. That's built.

Through every breath. Every practice. Every moment of staying when you wanted to flee.

You're different now.

Your body is different.

More regulated. More resilient. More yours.

This isn't the end. There is no end.

But it's a place to stand. A foundation to build on.

Whatever comes next—and life keeps coming—you meet it from here.

From a body that's home.

From a nervous system that knows it can handle intensity.

From a self that's integrated.

That's what hope means in the body.

Not certainty about outcomes.

Confidence in your capacity to meet them.

You have that confidence now.

Can you feel it?

That's yours.

Go live it.""",

"""The practices become background.

What was once effort becomes habit.

The body awareness you've been cultivating—it's starting to run on automatic.

Noticing your breath. Feeling your feet. Sensing your state.

These become the new normal.

Not something you do. Something you are.

An embodied person.

Present to your body in a way that used to require concentration.

This is integration complete.

Or not complete—ongoing.

But substantial enough that it's now part of you.

You don't have to think about it anymore.

It just happens.

That's the goal of all practice.

Not perpetual effort. Effortless presence.

You're not there fully yet. No one ever is fully.

But you're there enough.

Enough that the changes persist without white-knuckling.

Enough that you naturally check in with your body.

Enough that regulation is more available than before.

That's significant.

That's transformation.

That's you.""",

"""Your body is your ally now.

Think about what that means.

The body you might have seen as enemy—the source of pain, anxiety, limitation—is now on your side.

Not because it stopped being difficult.

Because your relationship changed.

You understand it now. Work with it. Trust it.

And it trusts you.

It trusts that you'll listen when it speaks.

That you won't override every signal.

That you're present enough to partner with it.

This alliance is precious.

It means you're not alone in your own life.

Your body is with you. Supporting you. Guiding you.

From this alliance, everything is possible.

Not because you've transcended limitation.

Because you have a partner in navigating it.

Feel your body right now.

Feel the alliance.

That's real.

That's yours.

Forward together now.""",

"""What comes next is yours to write.

The chapters end here. Your story continues.

With everything you've learned. Everything you've become.

Your body is different. Your capacity is larger. Your relationship to sensation has transformed.

What will you do with that?

Not in some dramatic way. In the ordinary moments.

How will you breathe tomorrow morning?

How will you meet the stress that comes?

How will you inhabit your body in the daily living of your life?

That's where this matters.

Not in special practice sessions. In every moment.

You have access now to something you didn't have before.

Presence. Regulation. Body wisdom.

These are available in any moment.

The question is: will you remember to access them?

Will you choose presence when avoidance is easier?

Will you feel when numbing is familiar?

Will you stay when every instinct says flee?

That's your work now.

Not learning more.

Living what you've learned.

Your body is ready.

Are you?""",

"""Home.

That's the word for where you are now.

In your body. Present. Here.

After all the work, all the struggle, all the practice—you've come home.

Not to a place.

To yourself.

To this body. This breath. This moment.

That's all it ever was.

Not somewhere to get to.

Somewhere to be.

And you're there.

Not perfectly. Not finally.

But really.

Home in your body.

Home in yourself.

It was here all along.

You just had to clear enough space to feel it.

Now you feel it.

That feeling is yours to keep.

No circumstance can take it.

No difficulty can erase it.

You know the way home now.

And home is always here.

In your body.

In this breath.

Now.

Home.

You made it.

Welcome."""
        ]
    }
    
    return integrations.get(phase, integrations["HARDSHIP"])[variant - 1]

# ============================================================================
# FILE GENERATION LOGIC
# ============================================================================

def compute_fingerprint(content: str) -> Dict[str, int]:
    char_count = len(content)
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    paragraph_count = len(paragraphs)
    sentence_count = sum(1 for char in content if char in '.!?')
    return {
        "char_count": char_count,
        "paragraph_count": paragraph_count,
        "sentence_count": sentence_count
    }


def get_content_for_section(chapter: int, section: int, section_type: str, variant: int, phase: str) -> str:
    content_getters = {
        "HOOK": lambda: get_hook_content(chapter, variant, phase),
        "SCENE": lambda: get_scene_content(chapter, section, variant, phase),
        "REFLECTION": lambda: get_reflection_content(chapter, section, variant, phase),
        "EXERCISE": lambda: get_exercise_content(chapter, section, variant, phase),
        "TEACHERDOCTRINE": lambda: get_teacherdoctrine_content(chapter, variant, phase),
        "INTEGRATION": lambda: get_integration_content(chapter, variant, phase)
    }
    return content_getters.get(section_type, lambda: f"Content for {section_type}")()


def create_variant_file(chapter: int, section: int, section_type: str, variant: int, purpose: str, phase: str) -> Dict[str, Any]:
    type_lower = section_type.lower()
    family = f"f{variant}"
    variant_id = f"ch{chapter:02d}_sec{section:02d}_{type_lower}_{family}"
    
    content = get_content_for_section(chapter, section, section_type, variant, phase)
    fingerprint = compute_fingerprint(content)
    
    scene_type = None
    if section_type == "SCENE":
        positions = {2: "opening", 5: "middle", 9: "resolution"}
        scene_type = positions.get(section, "narrative")
    
    return {
        "variant_id": variant_id,
        "chapter": chapter,
        "section": section,
        "section_type": section_type,
        "purpose": purpose,
        "variant_family": f"F{variant}",
        "content": content,
        "fingerprint": fingerprint,
        "metadata": {
            "persona": "Adult Professional",
            "topic": "Somatic healing",
            "section_type": section_type,
            "scene_type": scene_type,
            "location_tokens": []
        }
    }


def generate_template():
    print("=" * 60)
    print("Audiobook Template Generator V2 SOMATIC")
    print("Body-Centered Therapeutic Content")
    print("=" * 60)
    print(f"\nOutput: {OUTPUT_ROOT}")
    
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    registry = {"sections": {}}
    total_words = 0
    chapter_words = {}
    section_type_words = {}
    
    for chapter in range(1, NUM_CHAPTERS + 1):
        chapter_key = f"chapter_{chapter:02d}"
        phase = CHAPTER_PHASES[chapter]
        title = CHAPTER_TITLES[chapter]
        
        print(f"Ch{chapter:02d} ({phase[:4]}): {title}...", end=" ")
        
        chapter_dir = OUTPUT_ROOT / chapter_key
        chapter_dir.mkdir(exist_ok=True)
        
        registry["sections"][chapter_key] = {
            "chapter": chapter,
            "title": title,
            "phase": phase,
            "sections": {}
        }
        
        chapter_word_count = 0
        
        for section_info in SECTION_STRUCTURE:
            section_num = section_info["num"]
            section_type = section_info["type"]
            purpose = section_info["purpose_template"].format(phase=phase.lower())
            
            section_key = f"section_{section_num:02d}"
            section_id = f"ch{chapter:02d}_sec{section_num:02d}"
            type_lower = section_type.lower()
            
            section_dir = chapter_dir / f"{section_key}_{type_lower}"
            section_dir.mkdir(exist_ok=True)
            
            story_eligible = section_type == "SCENE"
            exercise_eligible = section_type == "EXERCISE"
            
            scene_type = None
            if section_type == "SCENE":
                positions = {2: "opening", 5: "middle", 9: "resolution"}
                scene_type = positions.get(section_num, "narrative")
            
            registry["sections"][chapter_key]["sections"][section_key] = {
                "section_id": section_id,
                "section": section_num,
                "type": section_type,
                "purpose": purpose,
                "scene_type": scene_type,
                "min_variants_required": NUM_VARIANTS,
                "story_eligible": story_eligible,
                "exercise_eligible": exercise_eligible,
                "variants": [],
                "metadata": {
                    "persona": "Adult Professional",
                    "topic": "Somatic healing",
                    "section_type": section_type,
                    "scene_type": scene_type,
                    "location_tokens": []
                }
            }
            
            for variant in range(1, NUM_VARIANTS + 1):
                variant_data = create_variant_file(chapter, section_num, section_type, variant, purpose, phase)
                
                word_count = len(variant_data["content"].split())
                chapter_word_count += word_count
                
                if section_type not in section_type_words:
                    section_type_words[section_type] = []
                section_type_words[section_type].append(word_count)
                
                family = f"f{variant}"
                variant_file = section_dir / f"{family}.yaml"
                
                with open(variant_file, 'w', encoding='utf-8') as f:
                    yaml.dump(variant_data, f, default_flow_style=False, allow_unicode=True, width=1000, sort_keys=False)
                
                registry["sections"][chapter_key]["sections"][section_key]["variants"].append({
                    "variant_id": variant_data["variant_id"],
                    "variant_number": variant,
                    "variant_family": f"F{variant}",
                    "fingerprint": variant_data["fingerprint"],
                    "location_tokens": []
                })
        
        chapter_words[chapter] = chapter_word_count
        total_words += chapter_word_count
        print(f"{chapter_word_count:,} words")
    
    registry_file = OUTPUT_ROOT / "registry.yaml"
    with open(registry_file, 'w', encoding='utf-8') as f:
        yaml.dump(registry, f, default_flow_style=False, allow_unicode=True, width=1000, sort_keys=False)
    
    # Statistics
    total_variants = NUM_CHAPTERS * len(SECTION_STRUCTURE) * NUM_VARIANTS
    words_per_path = total_words / NUM_VARIANTS
    words_per_chapter_path = words_per_path / NUM_CHAPTERS
    
    injected_per_chapter = 3 * 800 + 2 * 800  # 4,000 words
    total_with_injections = words_per_path + (NUM_CHAPTERS * injected_per_chapter)
    audio_hours = (total_with_injections / 150) / 60
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    
    print(f"\nFiles: {total_variants} variants + 1 registry = {total_variants + 1} files")
    
    print(f"\nSection type averages (words per variant):")
    for stype, words_list in sorted(section_type_words.items()):
        avg = sum(words_list) / len(words_list)
        print(f"  {stype:16s}: {avg:6.0f}")
    
    print(f"\nBase prose (per assembled path):")
    print(f"  Total: {words_per_path:,.0f} words")
    print(f"  Per chapter: {words_per_chapter_path:.0f} words")
    
    print(f"\nWith injections (3×800 story + 2×800 exercise):")
    print(f"  Per chapter: {words_per_chapter_path + injected_per_chapter:.0f} words")
    print(f"  Total book: {total_with_injections:,.0f} words")
    print(f"  Audio: ~{audio_hours:.1f} hours @ 150 wpm")
    
    print(f"\nChapter breakdown (base + inject = total):")
    for ch in range(1, NUM_CHAPTERS + 1):
        phase = CHAPTER_PHASES[ch]
        per_path = chapter_words[ch] / NUM_VARIANTS
        total = per_path + injected_per_chapter
        print(f"  Ch{ch:02d} ({phase[:4]}): {per_path:4.0f} + {injected_per_chapter} = {total:,.0f}")
    
    print(f"\nOutput: {OUTPUT_ROOT}")
    print("=" * 60)


if __name__ == "__main__":
    generate_template()
