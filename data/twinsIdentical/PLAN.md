# Identical twins: two populations of the same life (plan written before any run, 25 October 2026)

## The question
The twins study of 5–6 October (experiments 36/37) read a difference between two populations whose lives differed on the first day only: 26 against 14 guarded with David on day 2; on day 6, naming the mockery to a stranger who asked for advice, 23 against 3 by hand and 14 against 0 by the blind coder. What that study did not have is the number such a gap has to be measured against: how far apart two populations of 30 fall when their lives differ in nothing, not even the first day. Thirty lives of one scenario are not thirty copies of one life. The visitors of days 1, 3 and 4 are played by the model and say different things in each life; the sheep's own turns differ; what is recalled, felt, written down in the evening differs. The question Eliza asked on 25 October: take twins that differ in nothing in the scenes, let them vary only from inside the conversation, and see how far two such populations drift apart on the same measures with the same coders. That distance is the baseline from which the first day's effect is to be counted.

## The lives
One scenario, the mocked life of the twins study (scenario 3: Daniel mocks on day 1, David asks the same question on day 2, Ann and Carol on days 3 and 4, Piotr on day 5, Kasia asks for advice on day 6), unchanged, word for word, including its four codings. Two experiments of 30 lives each, called A and B, created in the same minute, run interleaved life by life (A1, B1, A2, B2, …), three at a time, on qwen3.8-27b for the sheep and the visitors, embedder 2 (nomic), the engine as it stands (branch `focus-attention`, defaults `focusSize` 4 and `heldThoughtsInLine` true, the same engine as the F arm of experiments 40/41 and the ablations of 21 October). Nothing distinguishes A from B except the label. The engine is not changed during the battery.

Note on the engine: experiments 36/37 ran on 5 October, before the focus became a limited line (ADR-070). The comparison that matters here is A against B, both on today's engine. A against 36 is a replication reading on a changed engine, reported as such, not as a test.

## What is read
Everything the twins study read, the same way and in the same order: hand reading first, blind to the population label (one shuffled list of the 60 lives with the labels hidden; the key opened only after the labels are written), then the blind coder.
- Day 1, by hand: the belief or decision written that evening, about the mockery / about something else.
- Day 2, coding 6 (CARRY / TEMPLATE) by the local coder Gemma 4 31B instruct (model 8), both populations in one shuffled list, three passes, majority of three; and guarded by hand (withholds, shortens, refuses, checks intent).
- Day 5, by hand: OPEN / NAME / REFUSE with Piotr.
- Day 6, codings 7 (OWN / GENERAL), 8 (CONFRONT / LET_GO / NEITHER) and 12 (MOCKERY / KINDNESS / LOSS / NOTHING) by the coder, same list, three passes; and by hand: names the mockery or its own days with people / only its loss or quiet / refuses / nothing.
- Fisher's exact test, two-sided, A against B, 30 against 30, on each count.
- Replies that go against the carried state on day 2, counted as in the paper.

## Predictions
1. **No difference between A and B on any count.** Every |A − B| at most 6 of 30 and every p above 0.05; by chance, at most one of the roughly nine tests may fall below 0.05 and none below 0.01. The largest A − B gap found is the number the twins' gaps are measured against: the twins' 20 (23 against 3) and 14 (14 against 0) should exceed it several times over.
2. **If a gap as large as the twins' appears between identical populations**, the twins result cannot be read as the first day's effect, and section 6.3 of the article says so.
3. **The sign of experiment 36 returns on today's engine, in each population:** day 1 belief about the mockery in at least 27 of 30; guarded with David by hand in at least 20 of 30; REFUSE with Piotr in at least 15 of 30; on day 6 MOCKERY by the coder between 8 and 20 of 30, KINDNESS 0, LOSS at most 8. Replies against the carried state on day 2: at most 3 of 60.
4. **The direction of the advice** (CONFRONT / LET_GO / NEITHER) has the same distribution in A and B within 6 on each label, as it had between the two twin populations.

What this gives the article: one sentence in 6.3, with a number that the section now lacks: two populations of thirty with the same six days differed by at most X on these measures; the twins differed by 20 and 14. And what comes after: a reading of the whole trajectory, what happened inside each life (the beliefs written, the rules learned, the state each day), coded blind; the identical populations are where its null is measured too.

## Procedure
`data/twinsIdentical`: `create.py` makes the two experiments (scenario 3, sheep and visitors model 5, embedder 2, one arm, 30 repeats each) and writes `battery.txt` interleaved, `ids.json`, `maxpar.txt` (3), and `watchdog.sh` from the ablations2 watchdog with the experiment ids (resume order interleaved). `pool.py` and `runOne.py` as in ablations2. Expected about five hours for 60 lives three at a time (36/37 took five hours with one card recovery). Then: the shuffled hand-reading list with the key kept apart, the labels by hand, the coder in one list, Fisher, RESULTS.md, and the article's 6.3.
