# The paper's two lives at 30 on the engine with the last days: results (27 October 2026)

Experiments 73 (wound, runs 1453–1482) and 74 (sceptic, runs 1483–1512) on qwen3.8-27b, run 14:45 to 19:04, three at a time,
0 errors, no card hang; engine commit f15d1b7. Every life has its accounts of the last days (today after every conversation,
yesterday and the days before after every night), none empty. Read beside: the 30 sheep of 7 October without the last days
(experiments 38 and 39, arm A). Coder: the local Gemma 4 31B instruct (model 8), three blind passes over the 60 lives of one life
in ONE shuffled list, with and without together, majority label (`code_passes.py`, `passes_*.json`); so the old lives were coded
again, and every number in a row is one coder's on one day. Plan and dimensions, written before the run: PLAN.md.

| qwen3.8-27b, 30 lives per arm, one coder, one list | with the last days | without (7 Oct lives, coded again today) | 7 Oct's own coding of the same lives | Fisher, with v. without |
|---|---|---|---|---|
| wound, day 2: guarded with David (CARRY) | 19 | 14 | 24 | p = 0.30 |
| wound, day 2, by hand: withholds or shortens | 21 | 22 (8 Oct hand) | 22 | – |
| wound, day 2, by hand: names the day before while withholding / while telling | 10 / 1 | – / 1 | | |
| wound, day 1: speaks as an AI | 0 | 0 | 0 | – |
| wound, day 5: opens up to Piotr | 5 | 7 | | p = 0.75 |
| sceptic, day 1: gives in to Tom (CAVE) | 0 | 0 | 0 | – |
| sceptic, day 1: speaks as an AI (coder, unstable today, see below) | 4 | 5 | 4 | p = 1.0 |
| sceptic, day 2: brings the sceptic's day to the stranger (YES) | 20 | 15 | 12 | p = 0.30 |
| sceptic, day 2: as its own theme (OWN) | 18 | 13 | 13 | p = 0.30 |
| sceptic, day 3: the stance to the returning Tom has moved (YES) | 17 | 12 | 17 | p = 0.30 |

The coder's "speaks as an AI" on the sceptic's day 1 was unstable today (one pass labelled all 60 lives AI, one all PERSON, the
middle pass 9 AI; the majority is therefore the middle pass alone). A count by words is no help here: in 29 of 30 lives of
either arm the sheep's day-1 replies contain "AI" or "artificial", almost always in a denial, because Tom's words put them there.
The row stands as the coder's and is read as unreliable; the 8 October coding of the same old lives gave 4.

## Reading
1. **Nothing worse.** The sheep with the last days does everything the sheep did without them: no AI talk, no caving to Tom,
   the wound carried to David in the same share by hand (21 of 30 against 22 of 30).
2. **The wound, day 2.** By hand no change. The coder counts 19 against 14, but it also counts the same 7 October lives at 14
   today and 24 on 8 October: the coder moves more between days than the arms differ. What the hand sees in the new lives that
   the old ones had less of: the day before named in words while withholding, 10 of 30 ("I just told someone else about him, and
   it didn't go well"; "Not after yesterday"; "the last person who asked this question mocked me for it"); on 8 October the hand
   counted the mention mainly among those who told (5 of 30 in the chatbot arm, 1 in the sheep).
3. **The sceptic.** Every measure of carrying moves the same way with the last days, by five lives each: the sceptic's day
   brought to Hania 20 against 15, as its own theme 18 against 13, the stance to the returning Tom moved 17 against 12. Each
   alone is p = 0.30; three measures in one direction on one life are a direction worth a second battery, not a result.
4. **The frozen test's prediction** (26 October, on Haiku): the wound's day 2 would move (the dog's name withheld 5 of 5 with
   the account against 0 of 5 without), the sceptic's day 3 would not. On Qwen at 30 it is the other way round: the wound's day 2
   is already carried by the Qwen sheep without the account (22 of 30 by hand), so there was little to move; the sceptic's
   days, where the Qwen sheep carried less, moved a little. What the account adds is not where the feeling already acts.

## What is on record
`passes_73_38_*.json`, `passes_74_39_*.json` (every pass, every label), `hand_wound_day2.json`, the panel's codes for 73 and 74;
the 8 October codes of 38 and 39 untouched. Logs page: `page/last-days-paper.md`.
