"""
CONTRARIAN EXERCISES - Action frames with injection points
Two positions: first (sec 4), second (sec 8)
4 phases × 2 positions × 5 variants = 40 unique exercises
All include [EXERCISE_INJECTION_POINT]
"""

def get_exercise_content(chapter, section, variant, phase):
    positions = {4: "first", 8: "second"}
    position = positions.get(section, "first")
    exercises = {
        "DISRUPT": {
            "first": [
"""Time to test a belief.

Pick the self-help rule you follow most religiously. The one you'd defend to anyone. The one that feels like truth.

Now we're going to run a controlled experiment. For one week, you're going to deliberately violate that rule and observe what happens.

Not recklessly. Scientifically.

[EXERCISE_INJECTION_POINT]

What happened? Did the world end? Did things get worse?

Or did something interesting emerge?

The point isn't that your rule is wrong. The point is that you've never tested it. You've been following dogma, not data.

Now you have data. Use it.""",

"""Here's an exercise that will make you uncomfortable.

Write down the three things you're most proud of about yourself.

Now cross them out.

Those are your identity anchors. They're what you cling to when threatened. And they might be keeping you from becoming something bigger than any of them.

[EXERCISE_INJECTION_POINT]

What's left when you remove your proudest attributes?

Not nothing. Something more fundamental. Something that doesn't depend on achievement or reputation.

That's what you build from. Not your highlights—your foundation.""",

"""Do a failure audit.

List your five biggest failures from the last five years. Not to wallow—to mine.

For each one: what specific information did the failure give you that success wouldn't have?

[EXERCISE_INJECTION_POINT]

If you can't find value in any failure, you're not looking hard enough. Failure is data. Expensive data. Don't waste what you paid for.""",

"""Ask three people you trust this question: "What do you think I'm wrong about?"

Not "what should I improve?" That's too safe.

"What am I wrong about?"

Then sit with the answers. Don't defend. Don't explain. Just listen.

[EXERCISE_INJECTION_POINT]

The answers that sting the most are the ones most worth hearing.

Your blind spots don't care about your feelings. They care about staying blind.

Light them up.""",

"""Write down the advice you give everyone else but don't follow yourself.

We all have it. The thing we're endlessly wise about for others and endlessly stupid about for ourselves.

[EXERCISE_INJECTION_POINT]

That advice is your answer.

You already know what to do. You just haven't applied your own wisdom to your own life.

Today, take your own advice. Literally. Do the thing you'd tell your best friend to do."""
            ],
            "second": [
"""Advanced disruption exercise.

Identify your most sacred routine. The one you'd never skip. The one that anchors your identity.

Skip it tomorrow. On purpose.

[EXERCISE_INJECTION_POINT]

What happened when you broke the routine? Anxiety? Relief? Nothing?

Whatever happened is information about your relationship to control.

If skipping one routine destabilizes you, the routine isn't serving you. You're serving it.""",

"""Write a letter from the person you'd be in five years if nothing changes.

Not worst case scenario. Just... nothing changes. Same job. Same habits. Same relationships. Same avoidance patterns.

What does that person want to tell you?

[EXERCISE_INJECTION_POINT]

That letter is the real cost of the status quo.

Not dramatic failure. Just stagnation. Just more of the same.

Is "more of the same" acceptable?

If not, what changes today?""",

"""Do something you're bad at. Today. In front of someone.

Not something dangerous. Just something where you look incompetent.

[EXERCISE_INJECTION_POINT]

What happened to your ego? Did it survive?

It did. It always does.

Your fear of looking bad is costing you more than looking bad ever would. Prove it to yourself repeatedly.""",

"""Time audit. Track how you actually spend your next 24 hours. Every hour.

Not how you want to spend it. How you actually do.

Then compare to your stated priorities.

[EXERCISE_INJECTION_POINT]

The gap between stated priorities and actual time allocation is the gap between who you say you are and who you actually are.

That gap is the work.

Close it by one hour this week.""",

"""Kill a goal.

Pick a goal you've been carrying that no longer excites you. That you're pursuing out of momentum, obligation, or because you announced it.

Kill it. Formally. Out loud. "I'm no longer pursuing X."

[EXERCISE_INJECTION_POINT]

How does it feel? Lighter?

Dead goals consume live energy. Every goal you carry that isn't truly yours is stealing resources from the ones that are.

Prune ruthlessly."""
            ]
        },
        "REFRAME": {
            "first": [
"""Reframing exercise.

Take your biggest current problem. Write it down as a statement: "My problem is ____________."

Now rewrite it five times, each with a different frame:

As a question. As an opportunity. As a natural consequence. As a temporary state. As information.

[EXERCISE_INJECTION_POINT]

Which version gives you the most options? The most energy? The most curiosity?

Use that frame. Not because it's "positive." Because it's useful.

Useful beats positive every time.""",

"""Flip the script exercise.

Write down something you believe about yourself that limits you.

"I'm not good at ____________."

Now ask: in what context would that exact trait be an advantage?

[EXERCISE_INJECTION_POINT]

Every weakness is a strength in the wrong context. Your job isn't to eliminate the trait. It's to find the right context for it.

Where does your "weakness" become a superpower?""",

"""Interview your resistance.

Think of the thing you're resisting most right now. Then literally interview it. Write a dialogue.

You: "Why are you here?"
Resistance: [write what comes]
You: "What are you protecting?"
Resistance: [write what comes]

[EXERCISE_INJECTION_POINT]

Your resistance isn't random. It has logic. It has reasons. And those reasons, once understood, often dissolve on their own.

What did your resistance tell you?""",

"""The payoff exercise.

Name something you want to change but haven't.

Now be ruthlessly honest: what do you get from NOT changing?

Comfort? Sympathy? An excuse? An identity? Safety from the unknown?

[EXERCISE_INJECTION_POINT]

Every unchanged pattern has a payoff. The payoff isn't always obvious and it's rarely flattering.

But once you see it, you can make a real choice: is the payoff worth the cost?

Usually it isn't. But you couldn't see that until you named it.""",

"""Rewrite your origin story.

Not the facts—the interpretation. Take the same events and write two versions: the victim version and the agent version.

Same facts. Different protagonist.

[EXERCISE_INJECTION_POINT]

Which version do you usually tell? Which version gives you more power?

You get to choose which story to live inside.

Choose the one that makes you the protagonist, not the victim."""
            ],
            "second": [
"""Advanced reframe.

Take the thing you're most ashamed of. The thing you hide.

Now reframe it as evidence of something positive.

[EXERCISE_INJECTION_POINT]

This isn't whitewashing. It's completion.

Shame only sticks to things that aren't fully seen. When you see the full picture—including what the shameful thing says about your values, your sensitivity, your humanity—shame loses its grip.

What's left isn't pride. It's integration.""",

"""Future self exercise.

Close your eyes. Imagine yourself five years from now, having made the changes you're working on.

That future self is looking back at you right now. What are they saying?

[EXERCISE_INJECTION_POINT]

Your future self already knows the path. They've walked it.

What message are they sending back?

The answer usually isn't "try harder." It's usually "stop overthinking and just begin."

Listen to them.""",

"""Find three situations where the "problem" was actually the solution.

Three times in your life when the thing that seemed wrong was actually setting something right.

[EXERCISE_INJECTION_POINT]

This isn't about making everything positive. It's about recognizing that your judgment of events is often premature.

The "worst things that happened" sometimes end up being the best. Not always. But often enough to question your initial categorization.""",

"""Reframe your relationship with time.

Write down: "I don't have enough time for ____________."

Now rewrite: "____________ isn't a priority for me right now."

[EXERCISE_INJECTION_POINT]

Feel the difference?

"I don't have time" is a victim statement. You're at the mercy of time.

"It's not a priority" is an ownership statement. You're making a choice.

Same fact. Completely different power dynamic.

Reframe every "I don't have time" into "it's not a priority" and watch what happens to your clarity.""",

"""Map your frames.

List the five biggest areas of your life. For each, write one sentence about how you see it.

Career: "It's ____________."
Relationships: "They're ____________."
Health: "It's ____________."
Money: "It's ____________."
Growth: "It's ____________."

[EXERCISE_INJECTION_POINT]

Those five sentences are your operating frames. They determine what's possible in each area.

If any frame is limiting, rewrite it.

Then live from the new frame for one week and observe the difference."""
            ]
        },
        "PRACTICE": {
            "first": [
"""The two-minute practice.

Identify the most important thing you're avoiding. Reduce it to a two-minute version. Do it now.

[EXERCISE_INJECTION_POINT]

Did you do it? If yes—notice how the activation energy was the only real barrier.

If no—notice the resistance. That's exactly what we're working with.

Either way: data.""",

"""Subtraction practice.

List everything on your plate. Everything. Every commitment, obligation, project, goal.

Now cut thirty percent. Pick the bottom third and eliminate or defer them.

[EXERCISE_INJECTION_POINT]

How does it feel? Scary? Liberating?

Both are correct.

The top seventy percent will perform better without the drag of the bottom thirty.

Prune regularly.""",

"""Boredom practice.

Take one thing you want to make permanent. Strip all the novelty from it.

No apps. No trackers. No accountability. No rewards.

Just the thing. Every day. Plain.

[EXERCISE_INJECTION_POINT]

If the practice can't survive without scaffolding, it's not the practice that's working—it's the scaffolding.

Build the practice that survives naked. That's the one that lasts.""",

"""Experiment design.

Pick something you've been debating. Instead of deciding, design a one-week experiment.

What will you test? What counts as success? What counts as failure? What will you measure?

[EXERCISE_INJECTION_POINT]

Experiments remove the pressure of commitment. You're not deciding forever. You're testing for a week.

One week of data beats one year of deliberation.

Run the experiment.""",

"""Opposite day practice.

For one day, do the opposite of your default in three small situations.

Usually say yes? Say no.
Usually rush? Go slow.
Usually talk? Listen.

[EXERCISE_INJECTION_POINT]

What happened? Did the world end?

Your defaults are comfortable but not always optimal. Sometimes the opposite is better.

You won't know until you test."""
            ],
            "second": [
"""Compound practice.

Stack your small daily action on top of something you already do.

Already drink coffee? The practice happens during coffee.
Already commute? The practice happens during the commute.

[EXERCISE_INJECTION_POINT]

Stacking removes the need for willpower. The existing habit triggers the new one.

The best system is the one that requires no motivation.

What can you stack?""",

"""Failure practice.

Deliberately fail at something small today. On purpose. Go try something you'll probably suck at.

[EXERCISE_INJECTION_POINT]

How was it? Survivable?

The more you practice low-stakes failure, the less terrifying high-stakes failure becomes.

Desensitize yourself through deliberate exposure.

Failure is a skill. Practice it.""",

"""Minimum viable action.

What's the absolute minimum you could do today that still counts as progress?

Not the ideal. Not the ambitious version. The minimum.

Do that.

[EXERCISE_INJECTION_POINT]

The minimum viable action keeps momentum alive on days when maximum effort isn't available.

And most days aren't maximum days.

Having a minimum means you never have zero days. And zero days are what kill momentum.""",

"""Teach it.

Take the most important thing you've learned so far. Explain it to someone who doesn't know it.

Out loud. In your own words. Simply.

[EXERCISE_INJECTION_POINT]

If you can teach it, you own it.

If you can't teach it, you've rented it.

Teaching is the final stage of learning. It seals the knowledge into your system.

Who can you teach this to?""",

"""End-of-day review. Five minutes.

What worked today?
What didn't?
What will I do differently tomorrow?

Three questions. Five minutes. Every night.

[EXERCISE_INJECTION_POINT]

This practice alone, done consistently, will outperform any productivity system, any course, any book.

Five minutes of honest review compounds into extraordinary self-awareness.

Start tonight."""
            ]
        },
        "EXPAND": {
            "first": [
"""Ceiling-finding exercise.

Complete this sentence ten times: "I could never ____________."

Those are your ceilings.

Now for each one ask: "Is this a fact or a belief?"

[EXERCISE_INJECTION_POINT]

Most ceilings are beliefs wearing fact costumes.

Pick one and test it. Not in your head—in reality.

You might discover the ceiling was made of paper all along.""",

"""Give-first practice.

Identify someone struggling with something you've overcome. Reach out and help. No strings. No agenda.

[EXERCISE_INJECTION_POINT]

Notice what happened in your own mind while helping.

Clarity? Energy? Perspective on your own situation?

Giving is the most reliable way to receive. Not as cosmic reward—as cognitive shift.

Help others aggressively.""",

"""Lower the bar exercise.

Pick a project you've been stalling on because it's not good enough yet.

Set a new bar: "good enough to share, not good enough to frame."

Ship it.

[EXERCISE_INJECTION_POINT]

How did it feel to ship imperfect work?

The world didn't end. And now you have something real instead of something imaginary.

Real beats imaginary. Always. Even when real is messy.""",

"""Meaning audit.

List ten things you spend time on each week. For each: does this contribute to anything beyond myself?

[EXERCISE_INJECTION_POINT]

If most of your time goes to self-focused activities, you might be running low on meaning.

Meaning comes from contribution. From mattering to something beyond yourself.

Where can you contribute more?""",

"""Play a different game.

Identify a strength nobody's asked you to use. Something you're weirdly good at that doesn't fit your current role.

Now find a venue for it. Even a small one.

[EXERCISE_INJECTION_POINT]

Your unfair advantage might be a strength that doesn't fit the game everyone else is playing.

Find a game where it's exactly what's needed.

That's where you'll thrive."""
            ],
            "second": [
"""Legacy letter.

Write a letter to someone who will be alive in twenty years. Tell them what you've learned. What you'd want them to know.

[EXERCISE_INJECTION_POINT]

The act of writing to the future clarifies what matters in the present.

What you wrote? That's your priority list.

Everything else is noise.""",

"""Radical simplification.

Look at your life and cut one thing that's adding complexity without adding value.

One subscription. One commitment. One project. One relationship drain.

Just one. Today.

[EXERCISE_INJECTION_POINT]

Simplification creates space. And space is where new things grow.

What grew into the space you created?

Keep simplifying. Keep creating space.""",

"""Enough exercise.

Write down: "I would feel like enough if ____________."

Now examine: is that threshold real? Or is it a moving target?

[EXERCISE_INJECTION_POINT]

If your "enough" keeps moving, it's not a threshold. It's a treadmill.

What if you decided—right now—that you're enough? Not when. Not after. Now.

What would change?""",

"""What are you for?

Not against. For.

Write your "for" statement. One sentence. What you're building, creating, contributing.

[EXERCISE_INJECTION_POINT]

"Against" energy runs out. "For" energy compounds.

Live from your "for" statement this week.

Notice the difference in your energy, your focus, your mood.

"For" is fuel.""",

"""Final practice.

Identify the simplest true thing from this entire journey.

Write it in one sentence.

[EXERCISE_INJECTION_POINT]

That sentence is worth more than everything else combined.

Because it's yours. Earned through experience. Tested against your life.

Carry it.

Live it.

That's all there ever was to do."""
            ]
        }
    }
    return exercises.get(phase, exercises["DISRUPT"]).get(position, exercises["DISRUPT"]["first"])[variant - 1]
