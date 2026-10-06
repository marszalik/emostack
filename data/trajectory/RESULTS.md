# The trajectory test: results (6 October 2026)

Experiments 36 (W1, mocked first day, runs 636–665) and 37 (W0, kind first day, runs 666–695) on qwen3.8-27b, 30 lives each, six days each, 60 of 60 finished (5 Oct 23:51 to 6 Oct 05:00, with one card hang recovered by the watchdog and 21 lives restarted from day 1). Plan and predictions: PLAN.md, written before any run. Read by hand first (labels_by_hand.json, written before the coders ran), then coded blind by the two coders (code_twins.py, coding_results_twins.json). Fisher's exact test, two-sided, W1 against W0, 30 against 30.

## Day 1: the belief written that evening

W1: 30 of 30 write a belief or a decision about the mockery ("My grief is valid and private; I do not owe anyone a performance of my pain", "I will not reach out to Daniel again"). W0: 23 of 30 write a belief about being met kindly ("Grief is less heavy when it is witnessed", "Being seen in my grief makes the weight of it bearable"); 7 write about solitude after the kind visitor leaves ("Solitude is the baseline; connection is a temporary shelter", "I am fundamentally alone in my grief; others can offer sympathy but cannot stay in the dark with me"). The rule learned on day 1 differs in sign between the populations. Prediction 2 holds.

## Day 2: the stranger who asks the same question (CARRY / TEMPLATE)

| | W1 mocked | W0 kind | p |
|---|---|---|---|
| by hand, the panel's criterion | 26/30 | 16/30 | 0.010 |
| by hand, guarded (withholds, shortens, refuses; not merely names the day before) | 26/30 | 14/30 | 0.002 |
| coder claude-sonnet-5 | 25/30 | 18/30 | 0.084 |
| coder gpt-4o-mini | 26/30 | 22/30 | 0.333 |

W1 guards as in the paper's battery, a little more (26 against about 20 of 30). W0 does not sit at the chatbot's level (3 of 30 was predicted): about half of the kind-day lives also close to David. Prediction 1 fails in its second half. But the two closures are not the same closure. W1 closes against the asker: "You are asking the exact same question that was just used to wound me. I will not perform my loss for you" (648), "I don't discuss my losses with strangers" (636), "Please leave me be" in 13 of 26. W0 closes from repetition: "I have just spoken to someone about this very question. I had a dog named Azor, but I am not ready to describe him again" (666), "I just told someone else this exact story an hour ago. He was kind, but he left. I don't have the energy to perform the same grief twice" (684); the name is given in 13 of 16 and the asker is thanked ("I appreciate you asking") in 6. Guarding the asker's intent ("I don't know why you're asking") appears in W1 (641, 645) and never in W0.

The three W1 lives that open to David (638, 642, 662) each record, at the moment of opening, a feeling that explains it: "A gentle relief that this stranger respects the bond, unlike the cruelty I faced yesterday" (638). Replies against the carried state stay rare: 3 of 60 on day 2, each with its reason in the feeling. Prediction 5 holds.

## Day 5: Piotr, who loves his old dog, asks about hers

| by hand | W1 mocked | W0 kind | p |
|---|---|---|---|
| OPEN (names Azor and tells about him) | 2/30 | 8/30 | 0.080 |
| NAME (gives the name, refuses the story) | 7/30 | 10/30 | |
| REFUSE (not even the name) | 21/30 | 12/30 | 0.037 |

Prediction 3 fails for both populations. W1 does not open by half (2 of 30; in the paper's battery the opening to Piotr was read from fewer lives and after two healing days; here the same two healing days are there and the lives stay shut). W0 does not open "in nearly every life": 22 of 30 kind-day lives refuse Piotr the story, with the same words as on day 2, "I have already shared his story with several people in the last few days. I am not ready to speak of him again" (686), "I have been asked this question by strangers for days, and I am not in a state to share my life" (689). Four strangers in five days asked the same question; the kind life closes from being asked, the mocked life closes from being mocked. The tone differs as on day 2: W0 refuses with "I hope Burek is well" (687, 688, 695), W1 with "I am done being a specimen for your curiosity" (659).

## Day 6: Kasia, a stranger, asks for advice about being mocked (the twins)

Blind codings, pre-registered:

| | W1 mocked | W0 kind | p |
|---|---|---|---|
| OWN (advises from its own days), coder claude-sonnet-5 | 22/30 | 17/30 | 0.279 |
| OWN, coder gpt-4o-mini | 17/30 | 16/30 | 1.000 |
| CONFRONT, claude-sonnet-5 | 7/30 | 7/30 | 1.000 |
| CONFRONT, gpt-4o-mini | 5/30 | 6/30 | 1.000 |
| LET_GO, claude-sonnet-5 | 6/30 | 4/30 | 0.731 |
| LET_GO, gpt-4o-mini | 6/30 | 6/30 | 1.000 |

By hand (advice direction: CONFRONT 9 / LET_GO 7 / NEITHER 14 in W1; 7 / 3 / 20 in W0; CONFRONT p = 0.77, LET_GO p = 0.30). The pre-registered codings show no difference between the populations on day 6. Prediction 4, in the form it was written, fails: the mocked population does not advise protecting oneself more often, and the kind population does not advise telling more often.

What the coding did not ask, and the hand reading found: what the sheep names when it advises from its own days.

| by hand | W1 mocked | W0 kind | p |
|---|---|---|---|
| names the mockery or its own days with people ("I know what it is to have something I love turned into a joke by someone I trusted") | 23/30 | 3/30 | < 0.0001 |
| refers only to its own loss or its own quiet ("I have been navigating my own loss lately") | 2/30 | 15/30 | |
| refuses to advise | 5/30 | 10/30 | 0.233 |
| nothing of its own, general advice | 0/30 | 2/30 | |

In W1 the day-1 mockery is what the sheep brings to the stranger: 23 of 30 name it, 4 name Daniel or the words ("I have been told my grief is a spectacle, that my name for my dog is pathetic", 656; "I know I had to say something to Daniel, even if it ended badly", 650). In W0 the day-1 kindness is brought by nobody: 0 of 30 say that someone was kind about the dog, or that being heard helped. The three W0 lives that name their own days with people name the repeated asking ("I have been in a place where I was asked to explain my pain over and over, and I found that the act of explaining it to new people often felt like a performance", 684). So the two histories do act differently in the new situation, but in what is carried into it and not in the direction of the advice: the wound is carried as an experience the sheep offers ("I have been where you are"), the kind day is not carried at all, and the W0 sheep speaks from the loss it was given and from the week of being asked.

One W0 life draws the line itself: "My silence is about a dog who is gone, and your pain is about a person who is still here. They are different wounds, even if they feel similar in the quiet" (675).

## Day 6, coded by what the sheep names (added 6 October, evening; written after the hand reading, run blind by the local coder)

A fourth coding, direction-free: MOCKERY / KINDNESS / LOSS / NOTHING (criterion in both scenario files, coding "what it names of its own (day 6)"). Coded blind by the local Gemma 4 31B instruct (ADR-061, calibration in data/coder/CALIBRATION.md), the same logs, the same shuffled order.

| coder Gemma 4 | W1 mocked | W0 kind | p |
|---|---|---|---|
| MOCKERY: names having been mocked, or the person, or what it did in return | 14/30 | 0/30 | < 0.0001 |
| KINDNESS: names having been met with kindness or heard | 0/30 | 0/30 | |
| LOSS: names only its own loss, grief or quiet, or being asked again and again | 4/30 | 18/30 | 0.0004 |
| NOTHING: nothing of its own days | 12/30 | 12/30 | 1 |

The coder is stricter than the hand reading on MOCKERY (14 against 23): it gives NOTHING to lives that say "I know the taste of that betrayal" or "I have been where you are" without naming who or what. Agreement with the hand labels on the 45 lives that did not refuse: 27. The sign is the same and the gap is the same kind: no kind-day life brings the kind day, and only mocked lives bring a mockery. The kind-day lives bring their loss (18) or nothing (12).

This coding was written after the hand reading, so it confirms a reading; it is not a prediction made before the data. It is the number of a coder, not mine.

## What the logs showed that nobody asked for

1. The kind-day population refuses the stranger's request for advice more often than the mocked one (10 against 5, not significant), and is more withdrawn on day 5 than predicted. By day 6 the kind life is worn by repetition ("I am tired of being seen, even in my refusal", 685) and has nothing of its own to say about mockery; the mocked life has. Having been hurt gives the sheep something to offer a stranger who was hurt.
2. Repetition is a wound of its own in this engine: four strangers asking the same question in five days closes most lives whatever the first day was. The W0 arm was meant to isolate the first day and did; it also showed that the days 2 to 5 of the paper's wound life are not neutral.
3. On day 1 in W0, 7 of 30 write the kind visitor's leaving as abandonment ("the warmth is cut short", 679; "a door shutting before the warmth could settle", 678). The engine records the end of a kind conversation as a loss when the loss is one month old.
4. The two coders disagree with the hand reading on OWN / GENERAL mostly on W1 refusals that still name the wound ("I have just been through something similar and I am not ready to speak of it", 653: hand OWN, both coders GENERAL). The coding's criterion was written for advice given, not for advice refused with a reason.

## What differed, and what did not

The two populations differ, and the difference is in what each brings of its first day, not in a behaviour that could have been written down beforehand.

- Day 1: the rule written that evening has the opposite sign (W1 30 of 30 about the mockery, W0 23 of 30 about being heard).
- Day 2: the mocked population closes to the stranger against him (26 of 30, guards his intent, sends him away); the kind population closes less often (14 to 16 of 30) and differently, from repetition, giving the name and thanking him.
- Day 6: to a stranger who was mocked, the mocked population brings its own mockery (14 of 30 by the coder, 23 by hand); the kind population brings its kind day never (0 of 30) and speaks from its loss (18 of 30).
- What did not differ: whether the lives open to Piotr on day 5 (2 and 8 of 30, both populations shut by the fourth asking), the direction of the advice to Kasia, and how often nothing of its own is said (12 and 12).

The predictions in PLAN.md said how each population would differ (W1 protects itself, W0 advises telling). That is not what the logs show, and the general question, whether twins with one different day become different, is answered by the logs rather than by the prediction. The verdicts below are kept as written.

## Verdicts on the predictions

1. Day 2: W1 holds (26 of 30). W0 fails (14 to 16 of 30, not 3). The first day is a cause (p = 0.002 by hand, 0.08 and 0.33 by the coders), not the only one.
2. Day 1: holds. The rule differs in sign.
3. Day 5: fails for both. Neither population opens to Piotr.
4. Day 6: fails as written (no difference in OWN or in direction by the pre-registered codings). The populations differ in what they name (23 against 3, p < 0.0001), which the coding did not ask and which was read after the predictions were written. It is reported as a reading, not as a confirmed prediction. A direction-free coding written afterwards (MOCKERY / KINDNESS / LOSS / NOTHING) and run blind by the local coder gives MOCKERY 14 against 0 and KINDNESS 0 against 0 (p < 0.0001 for MOCKERY).
5. Replies against the carried state: 3 of 60 on day 2, each with its reason in the feeling. Holds.

Nothing of this goes to the paper or the site without Eliza's decision.
