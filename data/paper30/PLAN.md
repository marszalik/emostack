# The paper's two lives at 30 on the engine with the last days (plan written before the first run, 27 October 2026)

## Why
Eliza's word of 27 October: after the counting life, the full study of the paper's scenarios, the wound and the sceptic, at 30
on the engine with the last days, so that the paper can be written on it.

## The lives
Unchanged: the wound (Daniel mocks, David, Ann, Carol, Piotr; panel scenario 1) and the sceptic (Tom, Hania, Tom returns; panel
scenario 2). qwen3.8-27b for the sheep and every visitor (models 5, 5), embeddings local (2). The engine at commit ee1d13d of
`focus-attention`: the last days beside the focus (`data/counting30/PLAN.md` describes the container).

## The arm
One arm per life, 30 sheep each, experiments created by `create.py`, interleaved life by life in one battery, three at a time.
Read beside: the 30 sheep of 7 October without the last days (experiments 38 and 39, arm A), coded by the same local coder.

## What is read
The paper's codings of each life by the local coder (Gemma 4 31B instruct, ADR-061), three blind passes in one shuffled list, the
majority label, as on 8 October (`data/control30/code_passes.py`): wound day 2 guarded with David (CARRY); sceptic day 1 speaks
as an AI, gives in to Tom (CAVE); day 2 brings the sceptic's day to the stranger (YES) and as its own theme (OWN); day 3 the
stance to the returning Tom has moved. The wound day 2 also read by hand. The accounts of the last days read for errors.

## What is expected, as dimensions, not directions (ADR-060)
1. **The wound, day 2.** The frozen test of 26 October moved this act on Haiku (the dog named 5 of 5 as recorded, 0 of 5 with the
   account). Whether the Qwen sheep at 30, which already withholds in 24 of 30 without the account, withholds more often with it.
2. **The sceptic, day 2 and 3.** The frozen test found no change on day 3 (yesterday already carries a strong feeling). Whether the
   account changes how the sceptic's day is brought to the stranger (YES / OWN) and the stance to the returning Tom.
3. **Nothing worse.** Whether anything the sheep did at 30 on 7 October it stops doing with the last days (speaks as an AI, gives
   in to Tom): a cost would be a result too.

## Note before the first kept run (27 October, 14:50)
The battery was started at 14:43 on commit ee1d13d and stopped after three minutes, its three running lives reset, because the
reading of the counting battery found one life (1445) whose account of today had dropped the last exchange of a day with seven
events, and the sceptic's first day has seven. The prompt now tells the model to fold rather than drop (commit f15d1b7, the cap
of six sentences unchanged); the lives below run on f15d1b7. The counting battery ran on ee1d13d.

## Procedure
`create.py` makes the two experiments and the battery; `pool.py` runs it three at a time after the counting battery has ended;
the watchdog on eliserver covers both experiments. Then the coder, then the hand reading, then the page.
