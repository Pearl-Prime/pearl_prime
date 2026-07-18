"""
CONTRARIAN SCENES - Story frames proving the counterintuitive point
60 scenes: 4 phases x 3 positions x 5 variants
All include [STORY_INJECTION_POINT]
"""

def get_scene_content(chapter, section, variant, phase):
    positions = {2: "opening", 5: "middle", 9: "resolution"}
    position = positions.get(section, "middle")
    scenes = {
        "DISRUPT": {
            "opening": [
"""Let me tell you about the most successful person I know who broke every rule.

She didn't set goals. She didn't have a five-year plan. She didn't wake up at five AM or journal or cold plunge.

What she did was simpler. And it contradicted almost everything the self-help world teaches.

[STORY_INJECTION_POINT]

Notice what happened there. Not what you expected, right?

The rules you've been following aren't laws of physics. They're suggestions that work for some people in some contexts.

And they might be exactly wrong for you.

What rule have you been forcing yourself to follow that's never actually produced the result it promised?""",

"""He was the laziest person in the room. And he outperformed everyone.

Not because of some hidden talent. Because he refused to do anything that didn't matter.

While everyone else was optimizing, hustling, grinding—he was sitting still. Thinking. Choosing.

Then acting once. Decisively. On the one thing that actually moved the needle.

[STORY_INJECTION_POINT]

There's a lesson there that most high-achievers will resist.

Because it threatens the identity. If hard work isn't the answer, then what are all those late nights for?""",

"""She quit the thing everyone told her to stick with.

Not because she was weak. Because she was paying attention.

The conventional wisdom was clear: winners don't quit. Push through. Stay the course.

But she noticed something nobody else was willing to say out loud.

[STORY_INJECTION_POINT]

Quitting isn't always failure. Sometimes quitting is the smartest strategic move you'll ever make.

What are you sticking with out of stubbornness that you should have walked away from?""",

"""He failed spectacularly. In public. Multiple times.

And then something happened that nobody predicted. The failures became his advantage.

Not in a motivational-poster way. In a mechanical, structural way.

[STORY_INJECTION_POINT]

Each failure eliminated a wrong approach, narrowed the field, pointed him toward what actually worked.

He didn't succeed despite failing. He succeeded because of the information failure gave him.

What has your failure been trying to teach you?""",

"""The advice that saved her was the advice she almost didn't take.

Because it sounded wrong. It contradicted everything she believed.

But she was desperate enough to try.

[STORY_INJECTION_POINT]

Sometimes the right answer sounds wrong because your framework is wrong.

What advice have you dismissed that might deserve a second look?"""
            ],
            "middle": [
"""Halfway through the experiment, she wanted to quit.

The counterintuitive approach felt wrong. Every instinct screamed to go back to comfortable.

But she'd committed to the full run.

[STORY_INJECTION_POINT]

The middle is where most people bail. This is exactly where the magic happens—if you can tolerate the discomfort of not knowing yet.""",

"""He was doing everything "wrong" and it was starting to work.

The results didn't match the theory. His approach violated every best practice.

And yet.

[STORY_INJECTION_POINT]

When reality contradicts your theory, update the theory. Don't ignore the reality.

What results in your life don't match the theories you've been following?""",

"""The breakthrough didn't feel like a breakthrough.

She expected fireworks. A moment of clarity. Instead it was Tuesday. Nothing special. She just... noticed something.

[STORY_INJECTION_POINT]

Real breakthroughs are quiet. They're the moments you almost miss because they don't match your expectations.""",

"""Three months into the new approach, people were noticing.

Not the results—the approach itself. It looked lazy. Undisciplined.

It was working.

[STORY_INJECTION_POINT]

Being misunderstood is the cost of being unconventional. Your results are your defense.""",

"""She stopped trying to fix herself and started fixing her environment.

A simple shift. Enormous implications.

[STORY_INJECTION_POINT]

Same person. Different context. Completely different outcomes.

What environment are you fighting against instead of changing?"""
            ],
            "resolution": [
"""A year later, she barely recognized her life.

Not through superhuman effort. Because she'd stopped doing the things that were holding her back. Subtraction, not addition.

[STORY_INJECTION_POINT]

The answer had been there all along. She'd been too busy adding things to notice what needed removing.""",

"""He went back and told the people who'd advised him to hustle harder.

Not to gloat. To share what actually worked. Most didn't believe him.

[STORY_INJECTION_POINT]

People would rather believe a comfortable lie than an uncomfortable truth. Don't let their discomfort make you doubt your results.""",

"""The old rules no longer applied. She'd written new ones.

Custom-fit rules, tested against her actual life rather than someone else's theory.

[STORY_INJECTION_POINT]

The rules that work for you might not exist in any book. They might be the ones you write yourself.""",

"""He didn't end up where he planned. He ended up somewhere better.

The plan was based on what he thought he wanted. Reality showed him what he actually needed.

[STORY_INJECTION_POINT]

Plans are hypotheses. Reality is the experiment. Where has reality been trying to redirect you?""",

"""She connected the dots looking back.

The failure. The counterintuitive advice. The uncomfortable experiment. The quiet breakthrough.

It all made sense in reverse.

[STORY_INJECTION_POINT]

You can't connect the dots looking forward. Trust the process while you're in it."""
            ]
        },
        "REFRAME": {
            "opening": [
"""She spent ten years solving the wrong problem.

Not because she was stupid—because the wrong problem looked exactly like the right one.

[STORY_INJECTION_POINT]

The real problem is usually simpler than the surface one. And harder to face.

How many years have you spent solving the wrong problem?""",

"""He reframed one sentence and everything changed.

Same circumstances. Same resources. Just a different way of looking at the exact same situation.

[STORY_INJECTION_POINT]

You don't need new circumstances. You need new framing.

What situation needs reframing rather than resolving?""",

"""The therapist said something that made her angry.

"What if your anxiety isn't a problem to solve but information to use?"

She wanted to be fixed. The therapist suggested she was already working correctly.

[STORY_INJECTION_POINT]

The most useful reframes are the ones that piss you off initially. That's probably the one you need.""",

"""He looked at his "weakness" from a completely different angle.

Same trait. Through a different lens, it wasn't a flaw. It was an asset in the wrong arena.

[STORY_INJECTION_POINT]

What have you been trying to fix that actually just needs relocating?""",

"""She asked a different question and got a different life.

For years: "why can't I change?" Then: "what am I getting from not changing?"

[STORY_INJECTION_POINT]

Every behavior has a payoff. Even destructive ones. Find the payoff and you'll understand the behavior."""
            ],
            "middle": [
"""The reframe was settling in, and it was uncomfortable.

Like an optical illusion where the vase becomes two faces. She could see both versions now.

[STORY_INJECTION_POINT]

Holding two true things at once is the definition of maturity.

Where do you need to hold two truths simultaneously?""",

"""He kept catching himself in the old frame.

New understanding, old habits. But each catch was faster. Each recovery quicker.

[STORY_INJECTION_POINT]

Knowing the new frame and living from it are different skills.

Be patient with the gap. It closes faster than you think.""",

"""She tested the reframe against her hardest situation.

Not the easy ones. The one where the old story felt like absolute fact.

Even there, it held.

[STORY_INJECTION_POINT]

A good reframe works especially where the old story is strongest. Where's your toughest test case?""",

"""People around him started noticing.

Not that he'd changed what he was doing—that he'd changed how he was seeing. And it was contagious.

[STORY_INJECTION_POINT]

When you change your frame, you change your energy. People respond to your relationship to your circumstances.""",

"""She realized the reframe applied everywhere.

Not just the original problem. The same principle across every domain.

[STORY_INJECTION_POINT]

The best reframes aren't situation-specific. They're operating systems. Where else does this apply?"""
            ],
            "resolution": [
"""The problem she'd fought for years dissolved.

Not because she solved it. Because she stopped framing it as a problem.

[STORY_INJECTION_POINT]

Problems don't always need solutions. Sometimes they need reclassification.""",

"""He couldn't go back to the old way of seeing.

The old frame was still available. But it had lost its monopoly.

[STORY_INJECTION_POINT]

You can't unsee a useful truth. The new frame is yours now.""",

"""She taught the reframe to her daughter in three sentences.

Because truth is always simple enough for a child to understand.

[STORY_INJECTION_POINT]

If you can't explain it simply, you don't understand it yet. One sentence. That's worth more than this chapter.""",

"""The situation hadn't changed. He had.

Same job. Same relationship. Same body. Completely different experience.

[STORY_INJECTION_POINT]

The frame matters more than the facts. Try changing the frame before changing the facts.""",

"""She laughed about it now. The thing that consumed years of anxiety.

Not because it was funny. Because from the new angle, it was so obvious.

[STORY_INJECTION_POINT]

Laughter is the sound of a reframe completing. What's starting to feel lighter?"""
            ]
        },
        "PRACTICE": {
            "opening": [
"""She started with two minutes a day. Everyone said it wasn't enough.

Six months later, those two minutes had compounded into a completely different life.

[STORY_INJECTION_POINT]

The size of the action matters less than the consistency. What's your two-minute version?""",

"""He did the opposite of what felt natural.

Every instinct said more. Push harder. He did less. Strategically. Everything improved.

[STORY_INJECTION_POINT]

Your instincts are calibrated to your old life. What if you did the opposite of your first instinct?""",

"""She made it boring on purpose.

No tracking apps. No accountability partners. Just the thing itself. Every day. Plain.

[STORY_INJECTION_POINT]

Boring is sustainable. Exciting is temporary. Can you make the important thing boring enough to survive?""",

"""He quit three things to start one thing.

Everyone said don't give anything up. He gave up three. The one remaining thing exploded.

[STORY_INJECTION_POINT]

Addition by subtraction. What could you quit to give the remaining thing room to breathe?""",

"""She experimented instead of committing.

While everyone went all-in, she ran small tests. Low cost. High learning.

[STORY_INJECTION_POINT]

Commitment without data is stubbornness with better branding. What could you test this week?"""
            ],
            "middle": [
"""Three weeks in, the results were invisible. To everyone else.

To her, something subtle had shifted. Invisible growth is still growth.

[STORY_INJECTION_POINT]

The roots grow before the tree. You can't see roots. Trust the invisible phase.""",

"""He wanted to add more. The temptation was intense.

It was working, so more would work better, right? He resisted. Kept it small.

[STORY_INJECTION_POINT]

The urge to scale too fast has killed more practices than laziness. Resist the urge to add.""",

"""She hit the messy middle.

Too far to go back, too early for results. The practice either becomes habit or becomes memory.

[STORY_INJECTION_POINT]

The messy middle is a filter. It separates people who practice from people who try.""",

"""He missed a day. Then two. Then a week.

Then he did the thing that separated him from quitters: he started again. Without drama.

[STORY_INJECTION_POINT]

The practice isn't about perfection. It's about return. How quickly can you come back?""",

"""She noticed the practice changing her outside the practice.

Unrelated reactions shifting. Calmer. Clearer. Two minutes leaking into the other twenty-three hours.

[STORY_INJECTION_POINT]

Practice doesn't stay in its lane. What you practice in one domain transfers to every domain."""
            ],
            "resolution": [
"""It wasn't a practice anymore. Just who she was.

No willpower required. Automatic as breathing.

[STORY_INJECTION_POINT]

When the practice becomes identity, the battle is over. What practice is becoming who you are?""",

"""He looked back at the simple, boring thing done every day.

It had quietly rebuilt his entire life. Not through force—through repetition.

[STORY_INJECTION_POINT]

The boring thing wins. Not because it's powerful once—because it's relentless. Your practice is water cutting rock.""",

"""She tried to explain it. "I just did this small thing every day."

The friend wanted a bigger story. But that was the whole method.

[STORY_INJECTION_POINT]

People want the secret. The secret is there is no secret. Just the boring thing, done daily.""",

"""He couldn't have predicted where the practice would take him.

Small daily action, enormous second and third-order effects.

[STORY_INJECTION_POINT]

The practice will take you places you can't currently imagine. That's not uncertainty. That's possibility.""",

"""The practice had become life. No longer something she did. Something she was.

[STORY_INJECTION_POINT]

This is the graduation: practice and life merge. What was hard becomes easy. You're closer than you think."""
            ]
        },
        "EXPAND": {
            "opening": [
"""She hit the ceiling she didn't know she had.

Not external—internal. Placed so long ago she'd mistaken it for reality.

[STORY_INJECTION_POINT]

The most dangerous ceilings are the ones you built yourself and forgot about. What ceiling are you treating as sky?""",

"""He helped someone else and accidentally solved his own problem.

The advice he gave her was the advice he needed. Word for word.

[STORY_INJECTION_POINT]

The wisdom you have for others applies to you too. What advice haven't you taken?""",

"""She lowered her standards and her quality went up.

By allowing imperfect work, she produced ten times more. And quantity was the path to quality.

[STORY_INJECTION_POINT]

Where are your standards preventing your output?""",

"""He stopped searching for meaning and meaning found him.

Through engagement. Through showing up. Through being useful.

[STORY_INJECTION_POINT]

Purpose is built through action. Meaning follows engagement, not the other way around.""",

"""She played a game nobody told her existed.

While everyone competed on the obvious field, she found a different one. Less crowded. Better suited.

[STORY_INJECTION_POINT]

What game would you dominate that nobody's told you about?"""
            ],
            "middle": [
"""The expansion was uncomfortable. Not painful—unfamiliar.

She kept expecting to feel ready. She never did. She expanded anyway.

[STORY_INJECTION_POINT]

Readiness is a feeling. Expansion is a choice. You don't have to feel ready.""",

"""He found that helping others was selfish in the best way.

It clarified his thinking. Created connections. Made him better.

[STORY_INJECTION_POINT]

Self-interest and service aren't opposites. They're the same thing from different angles.""",

"""She was operating at a level she'd thought was for other people.

Turns out, the something those people had was just more experience.

[STORY_INJECTION_POINT]

The people above you just started earlier. Or failed more. Or quit less. That's the whole difference.""",

"""He simplified everything and it all got better.

Fewer projects. Fewer goals. Fewer commitments. Radical simplification.

[STORY_INJECTION_POINT]

Complexity is confusion, not sophistication. What would radical simplification look like?""",

"""She stopped trying to be extraordinary and became effective.

Dropped the performance. Focused on delivery.

[STORY_INJECTION_POINT]

Nobody cares how extraordinary you are. They care whether you deliver."""
            ],
            "resolution": [
"""A year later, she couldn't explain the transformation conventionally.

She'd just stopped doing what didn't work and kept doing the one thing that did.

[STORY_INJECTION_POINT]

The resolution is always simpler than the struggle suggests.""",

"""He wrote what he'd learned in one sentence. After everything—one sentence. Embarrassingly simple.

[STORY_INJECTION_POINT]

If the answer isn't simple, you haven't found it yet. Keep going until it can't possibly be right. That's it.""",

"""She passed it on. Not as teacher. As someone who'd been there.

[STORY_INJECTION_POINT]

The best thing you can do with what you've learned is give it away. Who needs to hear this?""",

"""He realized the game never ends. Each expansion reveals new territory.

And that was the best news he'd ever received.

[STORY_INJECTION_POINT]

There's no finish line. The game is the point. The expansion is the reward.""",

"""She looked back at every chapter. Disrupted beliefs. Reframed problems. Boring practices. Quiet expansion.

All leading here: present. Herself.

[STORY_INJECTION_POINT]

Every counterintuitive twist led to the most intuitive destination: being yourself. Welcome."""
            ]
        }
    }
    return scenes.get(phase, scenes["DISRUPT"]).get(position, scenes["DISRUPT"]["opening"])[variant - 1]
