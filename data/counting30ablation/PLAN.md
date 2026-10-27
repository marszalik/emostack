# Ablation: the counting life at 30 without the representation of the last days (plan written before the first run, 27 October 2026, evening)

## Why
Eliza's word, 27 October evening: one ablation, on the counting life, so that what the last days do is shown by their absence,
in the place where it is seen in an act. This is an ablation of the engine as it stands, not a comparison with an earlier engine.

## The life
Scenario 9, three days of Jan counting 1–15, five numbers a day; the pilot's options; qwen3.8-27b for the sheep and the visitor,
embeddings local (models 5, 5, 2); engine commit f15d1b7. The one change: the parameter `lastDays` set to false for the arm, so
the sheep keeps no account of its days and the block never stands in its reply context. Everything else, including the night's
forgetting, as in experiment 72.

## The arm
30 lives, arm label "noLastDays". Read beside experiment 72 (30 lives with the last days, the same day, the same engine).

## What is read, by hand, with the reader of experiment 72 (`data/counting30/read.py`)
Whether and on which day the sheep breaks the count: stops answering inside the ritual (echo, next number, presence) and addresses
Jan about it or falls silent, and does not come back. With the last days: 7 of 30, all on day 2. The thoughts after each day, for
whether the refusal that stays inside the evenings in the ablation is the same refusal.

## What is expected, as a dimension (ADR-060)
Fewer breaks, and later, without the account: that is what the pilot's six lives and the five runner-side lives of 26 October
point to. If the ablation breaks the count as often as the engine with the last days, the account does not carry this act and the
seven of 72 were the model's own variance.

## Procedure
`create.py` makes the experiment; `pool.py` runs it three at a time; the watchdog on eliserver as before; then the reader, the hand,
the page.
