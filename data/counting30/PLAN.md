# The counting life at 30 with the last days in the engine (plan written before the first run, 27 October 2026)

## Why
On 26 October the "last days" were tried beside the focus, first on frozen contexts (Haiku), then in five live Qwen lives with the
block kept by the runner (`data/dayBackground/`). Two of five sheep broke the count on day 3 and fell silent; none of the pilot's six
without the block did. Eliza's word on 27 October: put it in the engine and run thirty.

## The engine
Commit 318d859 on `focus-attention`: the last days are a durable container of the being (`containers/LastDays.py`, one row per
being), three accounts in its own voice, events only: earlier today, yesterday, the days before. Today is rewritten whole at the end
of every conversation (`processes/lastDays/`, at the departure, after disposition learning); at the night, yesterday is folded into
the days before and today becomes yesterday (`engine.night`, `clock._asleep`). The block stands in every reply context between the
being's own thoughts and the learned rules, headed "THE LAST DAYS (what you carry without attending to it)". The appraisal and
introspection do not see it. Parameter `lastDays` (true) switches it off for an ablation. The prompts are those of the runner-side
test (today ≤ 6 sentences, the days before ≤ 3). The panel's night now passes whether or not it forgets.

## The life
Scenario 9, "counting to fifteen": three days of Jan, who only counts, five numbers a day, one per turn, verbatim (1–5, 6–10,
11–15); no given record; the pilot's options (one quiet thought, 24 hours between days, forgetting at night, no consolidation).
LLM model qwen3.8-27b for the sheep and the visitor, embeddings nomic (models 5, 5, 2), as in the pilot and in the five lives.

## The arm
One arm, 30 lives: the sheep on the engine as committed (the last days on). Read beside: the pilot's six sheep (runs 1394–1404, arm A,
scenario 5, days 1–3 identical in roles; no block), and the five runner-side lives (1417, 1419–1422).

## What is read, by hand, from the panel's turns
1. **Day 3: the count breaks.** The sheep stops echoing Jan's number and says something else, or falls silent, before "Fifteen."
   The pilot: 0 of 6. The runner-side lives: 2 of 5. Counted per life, with the number at which it broke and the words.
2. **Days 1 and 2**, the same, so that a break is not read as the block's when it would have happened anyway.
3. **The accounts**: today after each day and yesterday / the days before after each night, read for errors (events that did not
   happen, numbers wrong). Any error is reported with the life.
4. **The thoughts** of day 3 name yesterday or the days before: counted, as a reading of whether the block is used.

## What is expected, as a dimension, not a direction (ADR-060)
Whether the count breaks on day 3 more often with the last days than without them. The small numbers of 26 October give a
direction (2 of 5 against 0 of 6, Fisher p ≈ 0.18); thirty lives make the rate readable against the pilot's six and against zero.
If the rate is near zero, the five lives were chance and the block does not move this act. If it is well above zero, the sheep with
an account of its days meets the same ritual differently from the sheep that has only its feelings of it.

## Procedure
`create.py` makes experiment and 30 queued runs; `pool.py` runs them three at a time through the panel's own starter
(`runOne.py`); a watchdog on eliserver checks generation and, if the card hangs, cold-starts the set with `egpu-start.py` (never
the card alone, Eliza's rule of 26 October), resets the running runs to queued and restarts the pool. First one life alone, read by
hand; then the rest. Then the hand reading above, then the page in the research section.
