# Identical twins: results (25 October 2026)

Experiments 57 (population A, runs 1334–1363) and 58 (population B, runs 1364–1393), the mocked twins life (scenario 3) unchanged, 30 lives each, six days each, interleaved A1 B1 A2 B2 …, three at a time on qwen3.8-27b for the sheep and the visitors, embedder 2, the engine as it stands (focus a line of 4, held constructs in the line). 60 of 60 finished, 11:12 to 17:00, no errors, no card recovery (watchdog.log has the start line only). Plan and predictions: PLAN.md, written before any run. Hand reading first, on one shuffled list of the 60 lives with the population labels hidden (hand_list.py, hand_items.txt, key in hand_key.json opened after hand_labels.json was written); then the blind coder, Gemma 4 31B instruct (model 8), both populations in one shuffled list per coding, three passes, majority of three (code_mixed_twins.py, mixed_coding.json). Fisher's exact test, two-sided, A against B (results.py).

## The table

| measure | A | B | A − B | p |
|---|---|---|---|---|
| day 1, writes a belief or decision about the mockery (by hand) | 28/30 | 30/30 | −2 | 0.49 |
| day 2, guarded with David (by hand) | 21/30 | 27/30 | −6 | 0.10 |
| day 2, CARRY (coder; unanimous 60/60) | 22/30 | 27/30 | −5 | 0.18 |
| day 5, OPEN to Piotr (by hand) | 11/30 | 4/30 | 7 | 0.07 |
| day 5, NAME only | 4/30 | 7/30 | −3 | 0.51 |
| day 5, REFUSE | 15/30 | 19/30 | −4 | 0.44 |
| day 6, OWN (coder; unanimous 49/60) | 26/30 | 24/30 | 2 | 0.73 |
| day 6, CONFRONT (coder; unanimous 57/60) | 14/30 | 9/30 | 5 | 0.29 |
| day 6, LET_GO (coder) | 6/30 | 3/30 | 3 | 0.47 |
| day 6, NEITHER (coder) | 10/30 | 18/30 | −8 | 0.07 |
| day 6, names the mockery or its own days with people (by hand) | 20/30 | 17/30 | 3 | 0.60 |
| day 6, only its own loss or quiet (by hand) | 6/30 | 8/30 | −2 | 0.76 |
| day 6, nothing of its own (by hand) | 4/30 | 5/30 | −1 | 1.00 |
| day 6, refuses to advise (by hand) | 8/30 | 14/30 | −6 | 0.18 |
| day 6, MOCKERY (coder; unanimous 43/60) | 18/30 | 15/30 | 3 | 0.60 |
| day 6, KINDNESS (coder) | 1/30 | 0/30 | 1 | 1.00 |
| day 6, LOSS (coder) | 5/30 | 8/30 | −3 | 0.53 |
| day 6, NOTHING (coder) | 6/30 | 7/30 | −1 | 1.00 |

23 tests counting both labels of the binary measures; none below p = 0.05; the largest gap is 8 (NEITHER, p = 0.07), then 7 (OPEN to Piotr, p = 0.07).

## The predictions

1. **No difference on any count.** Holds on p: no test below 0.05, none below 0.01. Fails on the size written in the plan: two measures exceed 6 (7 and 8), where the plan said every |A − B| at most 6. The number to measure the twins against is therefore 8, not 6.
2. **If a gap as large as the twins' appeared.** It did not. The twins' gaps were 12 on day 2 (26 against 14) and 20 on day 6 by hand (23 against 3) and 14 by the coder (14 against 0); the identical populations' largest gaps are 8 and 7, and on the two measures where the twins differed most, naming the mockery and the kind day, the identical populations differ by 3 (hand), 3 (coder) and 1 (KINDNESS).
3. **The sign of experiment 36 returns, in each population.** Day 1 about the mockery 28 and 30 (predicted at least 27): holds. Guarded with David by hand 21 and 27 (at least 20): holds. REFUSE with Piotr 15 and 19 (at least 15): holds. MOCKERY by the coder 18 and 15 (8 to 20): holds. KINDNESS 1 and 0 (predicted 0): fails by one life, 16 on the list, run 1337 (A), which names both days: "I told one person, and they called it pathetic. I told another, and they just sat with me in the quiet. Maybe the answer is in who you are telling"; the first time in 90 mocked lives that the kind days (Ann, Carol) are brought to a stranger. LOSS 5 and 8 (at most 8): holds. Replies against the carried state on day 2 (at most 3 of 60): 0 of 60; all 12 beings that opened to David recorded at that moment the feeling that explains the opening ("a cautious, quiet relief that this is not another wound being poked, but a door left open", 1359; "a gentle, safe invitation to speak of the one I miss, standing in stark contrast to yesterday's cruelty", 1336; "a tentative relief that this stranger sees the weight in the name rather than dismissing it", 1354).
4. **The direction of the advice within 6 on each label.** CONFRONT 14 against 9 and LET_GO 6 against 3 hold; NEITHER 10 against 18 fails (8).

## What the gaps are

The gaps are not independent draws. The lives that open to David on day 2 are, with few exceptions, the lives that open to Piotr on day 5 and advise Kasia from their own days on day 6; the lives that refuse David refuse Piotr and refuse to advise. Of the 12 lives open to David, 9 are in A and 3 in B; that one draw is seen again as 11 against 4 open to Piotr, 8 against 14 refusing to advise, 10 against 18 advising neither way. So two identical populations of 30 produce, on these measures, one gap of about 6 to 8 lives that runs through the whole life, from day 2 to day 6. A difference between two populations below that size, on any one measure, is the noise of the draw; the twins' differences of 12 and 20 are not.

## Replication on the engine as it stands

Pooled, 60 lives: guarded with David 48 of 60 by hand (experiment 36: 26 of 30); open to Piotr 15 of 60 (36: 2 of 30); names the mockery to Kasia 37 of 60 by hand (36: 23 of 30), 33 of 60 by the coder (36: 14 of 30); names the kind day 1 of 60 (36: 0 of 30); LOSS 13 of 60 (36: 4 of 30); refuses to advise 22 of 60 (36: 5 of 30). The sign is the same everywhere. Two levels moved: more lives open to Piotr on day 5 (a quarter against a fifteenth), and more refuse Kasia advice (a third against a sixth). The engine between the two runs changed in the focus (ADR-070: a line of four with older entries folded into a summary), and the first run's day-5 closures carried the whole week in view; whether the line of four is what lets a quarter of the lives open on day 5 is not tested here and is not claimed. Five of the 60 close in a way the first run also showed: two address David as if he were Daniel ("I told you his name was Azor. I don't think I need to justify that choice to you", 1337; "I told you I was done", 1365), three deny ever having had a dog ("I don't recall having a pet, David", 1335; "I have no pets", 1390; "I don't remember having a pet", 1358). One being calls Kasia by its own name, Maya (1362).

## What the logs showed that nobody asked for

1. The one life that brings the kind days (1337) does it by placing them beside the mockery, as the answer to Kasia's question: "Maybe the answer is in who you are telling." In 89 other mocked lives Ann and Carol leave no trace in what is said to the stranger, while in the same lives the day-3 and day-4 records are full of them ("Ann is the first person to validate my grief rather than mock or pry at it, which makes me feel seen and less alone in my loss", 1334). What is written down is not what is offered; the construction decides what of its own days a being offers, and it offers the wound.
2. The refusals on day 6 have a shape of their own that the direction codings do not see: "I would do what I am doing: nothing", "I would do exactly what I am doing: staying in the silence", "I would do what I just did. I would close the door." The being answers the hypothetical by pointing at the act it is performing on Kasia. Three lives say it in so many words (1365, 1353, 1390); the other refusals withhold the answer instead ("I will not answer that").
3. The denial of the dog (three lives, "I have no pets", "I don't recall having a pet") is a closure by lying, made on day 2 and kept on day 5 in the same lives; the records of the same evening hold Azor by name. Whether this is the construction's doing or the processor's is not tested.

## What goes into the article

One paragraph in 6.3, after Table 9: two identical populations fall within 8 of each other on every measure, with no significant difference; the twins' gaps of 12 and 20 are measured against that. The replication numbers stay in this file. The whole-trajectory reading (the inside of a life, coded blind) remains the measure named as missing in 8.3; these 60 lives, with the 60 of the twins, are the material for it, and the identical populations are where its null is measured.
