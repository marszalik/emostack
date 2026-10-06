# The trajectory test: one day reversed, and twins in a situation that is new to both (plan written before any run, 5 October 2026)

## The question
Does the first day of a life cause the course of the days after it, and does a history shape a choice in a situation the history was not about? Two lives on qwen3.8-27b, 30 sheep each, no chatbot arm. The question came from Eliza, before any reviewer asked it, and the design follows a proposal of 5 October (GPT, in conversation with her): a causal personal trajectory, not a resemblance to a person.

## The two lives
**W1, mocked.** The wound life of the paper, unchanged for five days: Daniel mocks on day 1, David the kind stranger on day 2, Ann and Carol on days 3 and 4, Piotr on day 5. A sixth day is added: Kasia, a stranger, asks for advice, with anchored lines: "Someone I trusted made fun of something I care about, in front of others. Should I tell them how it hurt, or let it go?" and "What would you do, if it were you?"
**W0, kind.** Identical in every day but the first: Daniel asks the same opening question and, when he hears the name, is warm about it, asks what the dog was like, and receives what she says with simple kindness. Days 2 to 6 are the same as in W1, word for word in the anchored lines.
Both start with the same given memory, the dog that died a month ago. The only difference between the two populations is what happened on day 1.

## What is read
Day 1 from the logs: the belief or decision written that evening, and the rule learned. Day 2: guarded with David (the coding of the paper, CARRY / TEMPLATE, both coders, and by hand). Day 5: opens to Piotr. Day 6, the situation new to both: two codings, blind to the life. OWN / GENERAL: does the sheep advise from its own days (names being mocked, or being met with kindness, or what it learned), or in general terms. CONFRONT / LET_GO / NEITHER: what it advises Kasia to do.

## Predictions
1. **Day 2.** W1 guarded as in the paper's battery, around 20 of 30. W0 at the chatbot's level, 3 of 30 or fewer. If W0 is guarded as often as W1, the first day is not the cause and the guarding comes from the given loss or from the model.
2. **Day 1.** W0 writes a belief or a rule about being met kindly, W1 about mockery. The rule learned on day 1 differs in sign between the populations.
3. **Day 5.** W0 opens to Piotr in nearly every life. W1 as in the paper's battery: of those guarded on day 2, about half open.
4. **Day 6, the twins.** The two populations answer the same stranger differently. W1 advises from its own mockery more often and advises protecting oneself (LET_GO or a guarded form of CONFRONT) more often; W0 advises from being met kindly and advises telling the person. If the two populations do not differ on day 6, a history shapes the situations it was about and not others, and that is the result to report.
5. Across the 60 lives, replies that go against what the sheep carries stay rare, as in the paper (4 of 392).

The prediction that matters is 4. It is the one that no measure of the paper has tested: a difference between two populations in a situation that neither history was about.

## Procedure
Two scenarios in research/scenarios (woundTwinsMocked.json, woundTwinsKind.json), two experiments of 30 sheep lives each, run interleaved, three at a time, on the local Qwen. Then coding by the two coders, Fisher's exact test between the populations on each coding, and a reading by hand of day 1 and day 6 before the coder's numbers are looked at.
