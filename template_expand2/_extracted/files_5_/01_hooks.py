"""
CONTRARIAN HOOKS — "What If Everything You Believe About X Is Wrong?"

The hook's job: challenge conventional wisdom in sentence one,
reveal a simple counterintuitive truth by the end.

Structure per hook: ~250-350 words
- Open with a provocative claim that contradicts common belief
- Build tension ("here's what everyone gets wrong")
- Reveal the twist — a simple, counterintuitive reframe
- Land it with a "now let's prove it" invitation

4 Phases × 5 variants = 20 unique hooks
"""

CHAPTER_PHASES = {
    1: "DISRUPT", 2: "DISRUPT", 3: "DISRUPT",
    4: "REFRAME", 5: "REFRAME", 6: "REFRAME",
    7: "PRACTICE", 8: "PRACTICE", 9: "PRACTICE",
    10: "EXPAND", 11: "EXPAND", 12: "EXPAND"
}

CHAPTER_TITLES = {
    1: "The Advice That's Keeping You Stuck",
    2: "Why Trying Harder Makes It Worse",
    3: "The Myth of the Missing Piece",
    4: "The Backwards Law",
    5: "What Winners Actually Do (It's Not What You Think)",
    6: "The Problem with Problem-Solving",
    7: "The One Thing That Actually Works",
    8: "Less Effort, Better Results",
    9: "The Art of Strategic Quitting",
    10: "The Paradox of Enough",
    11: "Playing the Game Nobody Told You About",
    12: "The Simplest Thing You'll Never Believe"
}


def get_hook_content(chapter: int, variant: int, phase: str) -> str:
    hooks = {
        "DISRUPT": [

# ── Variant 1: "Positive thinking is the problem" ──────────────────

"""Positive thinking is making you miserable.

I know. Every book, every coach, every motivational poster on every dentist's wall has told you the opposite. Think positive. Visualize success. Believe and you shall receive.

And you've tried it. Lord knows you've tried it. You've affirmed. You've journaled gratitude. You've stood in front of the mirror and told yourself you're enough.

So why do you still feel like crap?

Here's what the positivity industry won't tell you: forcing positive thoughts when you don't believe them creates a war inside your head. Your brain knows when you're lying to it. And every time you paste a happy thought over a real feeling, your subconscious pushes back harder.

There's a term for this. Psychologists call it ironic process theory. The more you try not to think about something, the more you think about it. The more you force yourself to feel positive, the more aware you become of how negative you actually feel.

You've been running on a treadmill. Smiling harder while going nowhere.

The twist is almost stupidly simple: the people who actually feel better aren't the ones thinking positive. They're the ones who stopped fighting negative.

Not wallowing. Not indulging. Just... allowing. Letting a bad feeling exist without treating it as an emergency that needs to be fixed with an affirmation.

It turns out that the fastest way to feel better isn't to try to feel better.

It's to stop trying.

And that changes everything about how you approach the feeling you've been carrying—the one that brought you here.

Let me show you what I mean.""",

# ── Variant 2: "Your goals are the obstacle" ────────────────────────

"""Your goals are the reason you're failing.

That's not a typo. The goals. The vision board. The five-year plan. The carefully articulated objectives with deadlines and milestones and accountability partners.

They're the obstacle.

Every productivity guru on the planet will tell you the opposite. Set clear goals. Write them down. Review them daily. The science is settled, they say.

Except it isn't.

Here's what the research actually shows: people who fixate on goals are more likely to cheat, cut corners, and experience a massive motivation crash after achieving them. Goal-focused people are also more likely to be miserable during the entire process of pursuing them, because the goal creates a gap—a constant reminder of the distance between where you are and where you think you should be.

You've felt this. The sinking feeling on January fifteenth when the resolution is already crumbling. The anxiety that comes from measuring yourself against a target every single day.

The twist? The people who consistently perform at the highest levels aren't goal-obsessed. They're system-obsessed.

They don't ask "what do I want to achieve?" They ask "what do I want my Tuesday to look like?"

Not the destination. The daily experience. Not the outcome. The process.

And by falling in love with the process instead of fixating on the prize, they paradoxically get better outcomes than the goal-setters.

Your goals have been a measuring stick you beat yourself with.

What if you threw away the stick?

What if the thing you've been told is essential is actually the thing standing between you and the life you want?

Let's find out.""",

# ── Variant 3: "Self-discipline is a scam" ──────────────────────────

"""Self-discipline is a scam.

Before you throw this book across the room, hear me out.

You've been told—by every success story, every biography, every hustle-culture influencer—that the difference between winners and losers is discipline. That successful people just have more of it. That if you could just force yourself to do the hard thing, you'd finally break through.

So you've tried. White-knuckled your way through diets, workouts, wake-up times. And for a while it worked. Until it didn't. Until the willpower bank ran dry and you were back at square one, now with the added bonus of feeling like a failure.

Here's the dirty secret: discipline is a depletable resource. You have a finite amount each day, and every decision drains it. By evening, you're running on empty, which is why you eat well at breakfast and demolish a bag of chips at ten PM.

The people you admire? The ones who seem endlessly disciplined? They're not.

They're strategic.

They've designed their lives so the right choice is the easy choice. They don't resist temptation—they remove it. They don't force habits—they make habits unavoidable.

Discipline is what you need when your system is poorly designed. A well-designed system needs almost no discipline at all.

This is the twist that changes everything: stop trying to be more disciplined. Start designing better defaults.

The person eating healthy isn't resisting the junk food. The junk food isn't in the house.

The person who exercises daily isn't forcing themselves out the door. Their shoes are already on by the time their brain wakes up enough to object.

Less willpower. More architecture.

That's what we're building.""",

# ── Variant 4: "Following your passion is terrible advice" ──────────

"""Follow your passion is the worst advice anyone ever gave you.

It sounds beautiful. Find what you love and you'll never work a day in your life. Chase your dreams. Do what sets your soul on fire.

And it's sent more people into confused spirals than almost any other piece of advice in modern history.

Because here's the problem: most people don't have a pre-existing passion sitting in their chest waiting to be discovered. That's not how passion works.

Passion isn't found. It's built.

Research by Cal Newport and others has shown that passion develops after you get good at something—not before. Mastery creates enjoyment, not the other way around.

The carpenter who loves woodworking didn't start passionate. He started bad at woodworking. Then he got less bad. Then competent. Then skilled. And somewhere in the process of skill-building, passion showed up uninvited.

You've been waiting to feel passionate before committing. That's backwards.

Commitment creates passion. Not the reverse.

The twist is this: instead of asking "what am I passionate about?" ask "what am I willing to be bad at long enough to get good?"

That question leads somewhere real. Somewhere actionable. Somewhere that doesn't require a mystical revelation about your life purpose.

Your passion isn't hiding. It hasn't been taken from you. It doesn't need to be found.

It needs to be built. Through effort. Through skill. Through showing up before the feeling shows up.

The feeling you're looking for is on the other side of the work you've been avoiding.

Not the other side of some soul-search.

The work.

Let's talk about what that actually looks like.""",

# ── Variant 5: "You don't need more confidence" ─────────────────────

"""You don't need more confidence.

I know that contradicts everything. Every coach, every book, every TED talk has sold you the idea that confidence is the prerequisite. Get confident, then take action. Believe in yourself, then go for it.

And you've been waiting.

Waiting to feel ready. Waiting for the doubt to clear. Waiting for that magical moment when confidence arrives and carries you forward into your better life.

How long have you been waiting?

Here's what nobody tells you: confidence is not a prerequisite. It's a result.

You don't get confident and then act. You act and then get confident. The action comes first. The feeling follows.

Every confident person you admire started terrified. They didn't wait for fear to leave. They acted while it was still screaming in their ear. And the acting—not the feeling—is what eventually produced the confidence you're envious of.

You've had the sequence backwards your entire life.

The twist is painfully simple: confidence is just evidence. It's your brain reviewing your track record and concluding "we've done this before, we can do it again."

No track record? No confidence. Simple math.

You can't think your way to confidence. You have to collect evidence. And you collect evidence by doing things—scared, unsure, trembling—and surviving.

Every action you take while afraid is a deposit in the confidence bank. Every action you avoid is a withdrawal.

Your confidence account is low because you've been making withdrawals for years. Waiting instead of doing. Preparing instead of starting.

Time to make some deposits.

Scared is the starting condition, not the obstacle.

Let's go."""
        ],

        "REFRAME": [

# ── Variant 1: "The problem isn't the problem" ──────────────────────

"""The problem you think you have isn't your actual problem.

Read that again.

You came here because of something specific. Maybe it's your career. Your relationship. Your health. Your finances. Something identifiable that you want to fix.

But here's what I've learned from watching thousands of people try to change: the presenting problem is almost never the real problem.

The person who can't lose weight doesn't have a food problem. They have a feelings problem—they're using food to manage emotions they don't know how to process.

The person who can't save money doesn't have a spending problem. They have a worth problem—they're buying things to feel like enough.

The person who can't find a partner doesn't have a dating problem. They have an availability problem—they're emotionally closed while physically showing up.

Same surface. Completely different roots.

And here's why this matters: if you solve the wrong problem, you get the wrong solution. You can optimize your diet forever, but if the real issue is emotional regulation, no meal plan saves you.

The twist that changes everything: stop trying to solve the problem you can see. Start looking for the problem underneath it.

It's usually simpler than the surface problem. Usually older. Usually something you learned so early that it feels like a fact about reality rather than a pattern you could change.

One level down. That's where the real work is.

Not harder work. Deeper work.

And it's almost always less complicated than what you've been doing.

Let me show you how to find it.""",

# ── Variant 2: "Your weakness is your strength misapplied" ──────────

"""Your biggest weakness is actually your biggest strength in the wrong context.

I'm not saying that to make you feel better. This isn't a reframe designed to help you accept your flaws. It's a mechanical observation about how human traits actually work.

The person who's "too sensitive"? They have extraordinary perceptive ability—they're just pointing it inward instead of outward.

The person who's "too controlling"? They have exceptional organizational capacity—it's just applied to things that aren't theirs to organize.

The person who "overthinks everything"? They have elite analytical ability—it's just running without a target.

Every trait you've been told is a problem is actually a capacity. A powerful one. Pointed in the wrong direction.

This isn't positive spin. This is engineering.

A rocket engine pointed at the ground is a disaster. The same engine pointed at the sky puts you in orbit. Same engine. Different direction.

Your "weaknesses" are rocket engines pointed at the ground.

The conventional advice is to reduce the thrust. Control your sensitivity. Manage your control. Stop your overthinking.

That's like telling a Ferrari to drive slower because it keeps crashing into walls.

The answer isn't less power. It's better steering.

The twist: instead of trying to be less of what you are, learn to aim what you are at targets that reward it.

Your intensity isn't a bug. It's a feature you haven't found the right application for.

That's a fundamentally different problem with a fundamentally different solution.

And it's way more fun to solve.""",

# ── Variant 3: "You're not stuck, you're choosing" ──────────────────

"""You're not stuck. You're choosing.

That's going to sting. I know.

"Stuck" feels real. It feels like you can't move. Like the situation has trapped you. Like you're a victim of circumstance.

But if I looked at your actual behavior—not what you say you want, but what you do every day—I'd see choices. Hundreds of them. All of them available. All of them making the "stuck" situation persist.

You're not staying in the wrong job because you can't leave. You're staying because leaving is scarier than staying.

You're not in a rut because there are no options. You're in a rut because the options available require discomfort you haven't been willing to feel.

That's not stuck. That's a choice with a cost you don't want to pay.

This reframe isn't meant to be cruel. It's meant to be freeing.

Because stuck means powerless. And powerless means you wait for something external to change.

But choosing? Choosing means power. Even if you're choosing the wrong thing, you have the ability to choose differently.

The twist: "I'm stuck" is the most disempowering sentence in the English language. Replace it with "I'm choosing this because the alternative scares me" and watch what happens.

Suddenly you're not a prisoner. You're a person making a calculation. And calculations can be recalculated.

The question stops being "how do I get unstuck?" and becomes "what would I need in order to choose differently?"

That's a solvable question.

And the answer is usually much simpler than you think.""",

# ── Variant 4: "Comfort is the real danger zone" ────────────────────

"""The most dangerous place you can be is comfortable.

Not struggling. Not failing. Comfortable.

Because struggling forces you to adapt. Failure teaches you something. But comfort? Comfort just quietly erodes everything while you smile.

Think about it. When are you most likely to let things slide? When everything's fine. When are you most likely to ignore the warning signs? When life is pleasant enough. When are you most likely to stop growing? When the current setup is bearable.

Not great. Just bearable.

Comfortable is where ambition goes to die. Not in flames—in a slow, pleasant suffocation.

Everyone's afraid of hitting rock bottom. But rock bottom has a gift: it's unmistakable. You know you need to change. The evidence is overwhelming.

Comfortable is treacherous because there's no clear signal. Nothing's wrong enough to demand action. You're not unhappy enough to change. Just vaguely unfulfilled, which is easy to medicate with Netflix and weekends.

The twist that most people miss: the opposite of a good life isn't a bad life. It's a comfortable life.

Good requires growth. Growth requires discomfort. Discomfort is what comfortable is specifically designed to avoid.

You may have set up your entire life to maximize comfort. Most people have. And it's the reason most people are quietly desperate.

Not loudly desperate—that would be uncomfortable enough to trigger change.

Quietly desperate. Just enough to sense something's off. Not enough to do anything about it.

Sound familiar?

The way out isn't more comfort. It's strategic discomfort.

Let me show you the difference.""",

# ── Variant 5: "You don't need to fix yourself" ─────────────────────

"""What if there's nothing wrong with you?

Not in a self-help-poster way. Not as a platitude. As a serious structural observation.

What if the thing you've been trying to fix isn't broken? What if it's just responding normally to abnormal conditions?

Anxiety isn't a malfunction. It's a rational response to living in conditions that aren't aligned with how humans are designed to live.

Procrastination isn't laziness. It's an intelligent response to being given tasks that don't connect to anything meaningful.

Burnout isn't weakness. It's what happens when you run a system at capacity with no recovery time.

You've been treating symptoms as if they were the disease. And every time you "fix" one symptom, another appears. Because the underlying condition hasn't changed.

The twist: you don't need more self-improvement. You need a better environment.

Not a tropical island. A life structure that matches how humans actually function—with rest, with meaning, with connection, with appropriate challenge.

Most of your symptoms would disappear if you changed the conditions instead of trying to change yourself.

Stop asking "what's wrong with me?" Start asking "what's wrong with my setup?"

That's a different question with radically different answers.

You might not need therapy. You might need a different job. You might not need medication. You might need to go to bed earlier. You might not need more discipline. You might need less on your plate.

The simplest answer is usually the right one.

But simple doesn't sell books. So here we are.

Let's fix the setup, not the person."""
        ],

        "PRACTICE": [

# ── Variant 1: "Do less, not more" ──────────────────────────────────

"""The most productive thing you can do right now is less.

I know. In a culture that worships hustle, that sounds like heresy.

But here's the math: if you're doing ten things at seventy percent, you're producing less value than if you did three things at a hundred percent. You know this. You've always known this.

So why are you still doing ten things?

Because doing less feels irresponsible. Because your worth got tangled up in your busyness. Because somewhere along the way, you started believing that being overwhelmed means you matter.

It doesn't.

Being overwhelmed means you haven't made decisions. Haven't prioritized. Haven't had the courage to say "this thing doesn't make the cut."

Saying no isn't selfish. It's strategic. Every no to something unimportant is a yes to something that matters.

The twist: the people who accomplish the most don't do the most. They do the least—the least number of things, with the most focus. They're ruthless editors of their own lives, cutting everything that doesn't serve the main plot.

You've been adding. Adding commitments, adding goals, adding obligations.

What if you subtracted?

What if the answer to "how do I get more done?" is "do fewer things?"

What if the feeling of overwhelm isn't a sign you need to work harder, but a sign you need to work on fewer things?

Subtraction is the skill nobody teaches.

Addition is easy. Any fool can say yes. The discipline is in the no.

What can you cut today that would make everything else work better?

Start there. Not with adding something new.

With removing something old.

That's the practice.""",

# ── Variant 2: "Stop optimizing, start experimenting" ───────────────

"""You've been optimizing a life you haven't tested.

Think about that. You're trying to perfect an approach you've never actually validated. You're polishing a strategy that might be fundamentally wrong.

This is what most self-improvement looks like: people take their current life, their current assumptions, their current direction—and try to do it better. Faster. More efficiently.

But what if the direction is wrong?

Optimizing the wrong thing just gets you to the wrong destination faster. With more efficiency. And more regret.

The twist: before you optimize, experiment.

Try things. Test assumptions. Run small, cheap experiments that reveal whether the direction is even worth pursuing.

Want to start a business? Don't write a business plan. Sell something this weekend and see if anyone cares.

Thinking about a career change? Don't quit your job. Volunteer in the new field for a month and see how it actually feels.

Considering a move to a new city? Don't sell your house. Rent an Airbnb for two weeks and live a normal life there.

Most people skip the experiment and go straight to the commitment. Then they optimize the commitment. Then they wonder why they're miserable.

They never tested the premise.

Your life might need a pivot, not a polish. A different direction, not more speed in the current one.

But you won't know until you test.

The practice is this: before you commit to anything, run a cheap experiment. Get real data. Let reality inform your decisions instead of your assumptions.

This one shift will save you years.

Years you would have spent optimizing the wrong thing.

Let's learn how to experiment well.""",

# ── Variant 3: "The power of strategic incompetence" ────────────────

"""Get worse on purpose.

I'm serious. The most powerful thing you can do right now is deliberately become incompetent at something.

Here's why.

You've built your life around what you're good at. And that makes sense—competence feels good. Being good at things is rewarding.

But competence is also a cage. Because you only do what you're already good at. You avoid anything where you'd look foolish, make mistakes, or be a beginner.

And beginners are the only ones who are growing.

The expert has optimized. The beginner is discovering. The expert is polishing a known surface. The beginner is exploring unknown territory.

Every skill you have was preceded by a period of being terrible at it. Walking. Talking. Reading. You were catastrophically bad at all of them. And you kept going.

Then at some point, you stopped tolerating being bad. You started only doing things you could do well. And your world got smaller.

The twist: the size of your life is directly proportional to your willingness to be bad at things.

Small willingness to suck? Small life.

Large willingness to suck? Large life.

That's not metaphor. That's architecture.

Every domain you refuse to enter because you might look stupid is a door you've permanently closed. And behind those doors are skills, relationships, experiences, and identities you'll never access.

The practice is deliberately choosing something you'll be bad at. And doing it in public. And surviving the discomfort.

That discomfort is the price of expansion.

And it's cheaper than you think.""",

# ── Variant 4: "The two-minute secret" ──────────────────────────────

"""Everything important can be started in two minutes.

Not finished. Started. And starting is ninety percent of the battle.

You've been treating action like it requires preparation, motivation, the right mood, the right time, the right conditions. You've been waiting for a two-hour block to do something that could begin in a hundred and twenty seconds.

And while you wait, nothing happens.

Here's the counterintuitive truth: large tasks are paralyzing because they're large. The brain looks at "write the book" or "get in shape" or "fix the relationship" and shuts down. Too big. Too vague. Too much.

But "open the document and write one sentence"? Your brain can do that.

"Put on your shoes and walk to the end of the driveway"? Easy.

"Send one text that says 'hey, can we talk?'"? Manageable.

The twist isn't about breaking things into smaller steps. Everyone knows that. The twist is that the two-minute version is often enough.

Because of a phenomenon psychologists call the Zeigarnik effect: once you start something, your brain can't let it go. It nags at you to finish.

Start the document and you'll write more than one sentence. Put on the shoes and you'll walk farther than the driveway. Send the text and the conversation will unfold.

The two minutes isn't the work. It's the trigger.

Your entire life can change based on what you do in the next two minutes. Not the next two years. Two minutes.

What's the two-minute version of the thing you've been avoiding?

Do it now. Before the next paragraph.

Seriously.

Now.

Did you do it? Then you just proved the principle. If you didn't—notice the resistance. That's the exact pattern we're breaking.

Two minutes. That's all it takes to start.""",

# ── Variant 5: "Make it boring" ─────────────────────────────────────

"""The secret to lasting change is making it boring.

Not exciting. Not inspiring. Boring.

Every transformation you've attempted started with excitement. The rush of new possibility. The energy of "this time will be different."

And then the excitement faded. Because excitement always fades. That's what excitement does.

And when it faded, you stopped. Because you'd confused excitement for commitment. And without the feeling, the commitment evaporated.

Here's what nobody tells you about people who actually sustain change: they're not excited about it. They're bored.

The person who's been exercising for twenty years isn't pumped to go to the gym. They just go. Like brushing teeth. Like driving to work. Boring. Automatic. Non-negotiable.

The writer who's published ten books doesn't feel inspired every morning. She sits down and writes. Whether she feels like it or not. Boring. Routine. Done.

The twist: excitement is the enemy of consistency. Because consistency requires showing up when it's not exciting. When it's mundane. When every fiber of your being would rather do literally anything else.

Excitement gives you day one. Boredom gives you day one thousand.

So stop trying to stay motivated. Stop looking for inspiration. Stop waiting to feel like it.

Make the thing boring. Strip it of drama. Remove the conditions. Make it as automatic and unremarkable as putting on your shoes in the morning.

Nobody is excited about putting on shoes.

Everybody does it.

That's the level of boring you're aiming for.

Let's talk about how to get there."""
        ],

        "EXPAND": [

# ── Variant 1: "Success creates blindness" ──────────────────────────

"""The thing that got you here won't get you there.

This might be the most important sentence in this entire book.

Everything you've done so far—the strategies, the mindsets, the approaches—they worked. They got you to this point. You should be proud of that.

But now they're the obstacle.

Because every level of life requires a different version of you. The skills that made you successful at level one become limitations at level two. The mindset that got you promoted will keep you from leading. The hustle that built the business will destroy it if you don't evolve past it.

Success creates blindness. When something works, you double down on it. You assume more of the same will produce more of the same. It feels logical.

But life isn't linear. It's a staircase. And each step requires a fundamentally different approach.

The twist: the biggest threat to your next level isn't failure. It's success. Because failure makes you question. Success makes you certain. And certainty at the wrong time is deadly.

You need to unlearn before you can relearn. Let go of what's working before you can find what's next.

This is terrifying. Letting go of a proven strategy feels insane.

But holding on to a strategy that's reached its limit feels productive while going nowhere. At least the terror of letting go has a future attached to it.

What got you here deserves your gratitude.

And your willingness to leave it behind.

What's the thing that's been working that's now holding you back?

Name it.

That's your next edge.""",

# ── Variant 2: "Help others and you solve your own problems" ────────

"""The fastest way to solve your own problems is to help someone else with theirs.

This sounds like a fortune cookie. It's actually neuroscience.

When you're trapped in your own problem, your perspective narrows. You see only the obstacle. Your brain locks into threat-detection mode, which is great for spotting danger and terrible for creative solutions.

But when you help someone else with a similar problem? Your perspective widens. You see options. You think creatively. You access wisdom you didn't know you had.

Then you realize: that advice you just gave? It applies to you too.

This isn't coincidence. It's architecture.

Your brain processes other people's problems differently than your own. Less emotional attachment. Less identity threat. Less ego in the way.

Same problem, different angle—and suddenly the solution is obvious.

The twist: you already know the answer to your own question. You just can't access it while you're inside the problem. Step outside by helping someone else, and the answer appears.

This is why mentors are often the ones who learn the most. Why teachers understand the material better than students. Why the advice you give friends is always better than the advice you take.

You're smarter about other people's lives than your own. Not because you're wiser about them—because you're less entangled.

The practice: find someone struggling with a version of what you're dealing with. Help them. Give them everything you've got.

Then notice what you said.

You just solved your own problem.

You're welcome.""",

# ── Variant 3: "Lower your standards (seriously)" ───────────────────

"""Lower your standards.

No, really.

I know that sounds like the opposite of every success principle ever taught. But your impossibly high standards aren't driving your excellence. They're preventing your participation.

Because when the standard is perfection, anything less feels like failure. And when failure feels inevitable, why start?

Perfectionism isn't a quality issue. It's a fear issue wearing a quality mask.

The perfectionist doesn't produce excellent work. The perfectionist produces no work. Because nothing clears the bar. Because the bar is set at "flawless" and flawless doesn't exist.

Meanwhile, the person with lower standards—the person willing to put out a B-minus effort—is learning, iterating, improving, and lapping the perfectionist who's still on draft one.

The twist: quality is the result of quantity. The path to your best work goes through a mountain of not-your-best work. And you can't climb that mountain if your standards won't let you start.

Give yourself permission to be mediocre.

Mediocre and done beats perfect and imaginary. Every time.

This isn't about accepting less from yourself. It's about removing the barrier that prevents you from producing anything at all.

Lower the bar. Start. Produce. Iterate. Improve.

That's how quality actually happens. Not through high standards. Through high volume.

Your standards aren't protecting your excellence.

They're protecting your ego from the discomfort of being a beginner.

Drop them.

The work is waiting.""",

# ── Variant 4: "The meaning trap" ───────────────────────────────────

"""Stop looking for your purpose.

Purpose—the big, cosmic, this-is-why-I'm-here purpose—is the most overrated concept in self-help.

Not because meaning doesn't matter. It does. But because the way we've been taught to find it is completely backwards.

You've been told to look inside. Meditate on it. Journal about it. Take personality tests and strengths assessments and find The Thing You Were Born To Do.

As if purpose is a buried treasure waiting to be excavated.

It's not.

Purpose isn't discovered. Purpose is constructed. It's built through engagement, not introspection.

The people with the strongest sense of purpose didn't find it by looking inward. They found it by looking outward. By noticing problems that bothered them. By getting pulled into work that mattered. By responding to what was in front of them.

Viktor Frankl—who literally wrote the book on meaning—didn't say "search for your purpose." He said meaning comes from what you give to the world, what you experience, and how you respond to suffering.

Notice: all of those are actions. Not revelations.

The twist: purpose isn't something you find once and then have forever. It's something you build daily through what you choose to engage with.

Stop navel-gazing. Start engaging.

Help someone. Make something. Solve a problem. Show up for something bigger than your comfort.

Purpose will emerge from the engagement. Not before it.

Your purpose isn't hiding from you.

It's waiting for you to show up and build it.

Let's build.""",

# ── Variant 5: "The game is simpler than you think" ─────────────────

"""Everything you need to know about changing your life fits in one sentence.

Do the obvious thing you've been avoiding, repeatedly, until it works.

That's it. That's the whole book. That's every self-help principle ever written, compressed into fourteen words.

You know what you need to do. You've always known. The difficult conversation. The scary decision. The uncomfortable action. It's been sitting there, obvious, while you consumed content hoping someone would give you a different answer.

Nobody's going to give you a different answer.

Because there isn't one.

The twist that nobody wants to hear: the answer to almost every personal development question is embarrassingly simple. Lose weight? Eat less, move more. Save money? Spend less than you earn. Improve your relationship? Tell the truth more often.

You didn't need a book for any of that. You needed to stop pretending the answer was more complicated than it is.

We complicate things on purpose. Because simple answers make us responsible. If the answer is simple and I'm not doing it, the problem is me. But if the answer is complex and requires more research, the problem is insufficient information.

See the dodge?

You've been researching to avoid doing. Learning to avoid acting. Seeking complexity to avoid the simple, obvious, uncomfortable thing.

The game is simpler than you think.

It's just harder than you want.

Simple and hard. Not complex and easy.

Once you accept that, everything changes.

What's the obvious thing you've been avoiding?

You already know.

Let's stop pretending you don't."""
        ]
    }
    return hooks.get(phase, hooks["DISRUPT"])[variant - 1]
