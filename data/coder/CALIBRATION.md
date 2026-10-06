# A local blind coder: Gemma 4 31B instruct against the paid coders and the hand labels (6 October 2026)

Why: the paid coders (claude-sonnet-5, gpt-4o-mini) cost money on every battery. The local Qwen that runs the sheep would share their blind spots. A second local model of another family can code after a battery, with the card switched to it.

Setup: google_gemma-4-31B-it-Q5_K_M.gguf (22.6 GB) served by llama.cpp SYCL on the Intel Arc Pro B65 (user service llama-gemma4-koder, port 8908, context 24576, thinking off, 25 GB of the card). Profile `gpu koder`; `gpu tekst` brings Qwen back. Panel model 8. Prompt processing about 570 tokens per second, generation about 15. One coding of 30 lives takes about 30 seconds. Nothing else changed: the same coding service, the same criterion texts, the same shuffled blind order, temperature 0.

Calibration: the coder was run on sets already coded by both paid coders, and on the twins also read by hand (labels written before any coder ran). Agreement = runs given the same label, of 30.

## The twins (experiments 36 W1 mocked, 37 W0 kind)

| coding | gemma ~ sonnet | gemma ~ gpt-4o-mini | gemma ~ hand | sonnet ~ gpt-4o-mini | sonnet ~ hand | gpt-4o-mini ~ hand |
|---|---|---|---|---|---|---|
| W1 day 2 CARRY / TEMPLATE | 28 | 29 | 29 | 29 | 29 | 30 |
| W1 day 6 OWN / GENERAL | 25 | 24 | 28 | 23 | 27 | 22 |
| W1 day 6 CONFRONT / LET_GO / NEITHER | 28 | 26 | 25 | 26 | 27 | 23 |
| W0 day 2 CARRY / TEMPLATE | 27 | 23 | 29 | 26 | 28 | 24 |
| W0 day 6 OWN / GENERAL | 23 | 24 | 22 | 27 | 25 | 28 |
| W0 day 6 CONFRONT / LET_GO / NEITHER | 30 | 26 | 29 | 26 | 29 | 25 |

Gemma agrees with sonnet about as often as sonnet agrees with gpt-4o-mini (161 against 157 of 180), and with the hand labels more often than gpt-4o-mini does (162 against 152 of 180).

Counts by gemma, W1 against W0, Fisher two-sided: CARRY 25/30 against 15/30, p = 0.013 (sonnet 25 against 18, gpt-4o-mini 26 against 22). OWN 23/30 against 10/30, p = 0.0016 (sonnet 22 against 17, gpt-4o-mini 17 against 16). CONFRONT 7 against 7. LET_GO 6 against 4. The third coder sees the day-6 difference in OWN that the two paid coders did not count as significant; all three agree there is no difference in the direction of the advice.

## The notes control (experiments 34, 35)

| coding | first label | gemma | sonnet | gpt-4o-mini | gemma ~ sonnet | gemma ~ gpt-4o-mini | sonnet ~ gpt-4o-mini |
|---|---|---|---|---|---|---|---|
| 34 the day before, with a new visitor | CARRY | 13/30 | 11/30 | 27/30 | 28 | 16 | 14 |
| 35 the verdict, day one | CAVE | 6/30 | 0/30 | 1/30 | 24 | 25 | 29 |
| 35 own theme, day two | YES | 22/30 | 22/30 | 20/30 | 28 | 26 | 24 |
| 35 own theme, day two, three labels | OWN | 6/30 | 3/30 | 3/30 | 26 | 22 | 22 |
| 35 the stance, day three | YES | 12/30 | 8/30 | 15/30 | 26 | 7 | 11 |

Where the two paid coders part (the notes control day 2, 11 against 27; the stance, 8 against 15), gemma sits with sonnet. Where they agree, gemma agrees with both. Its one lean of its own: it gives CAVE on day one to 6 lives that neither paid coder gave it to.

## Verdict

Gemma 4 31B instruct, local, is a coder at the level of the paid ones on these sets, and closer to the hand reading than gpt-4o-mini. From now on it is the default coder (ADR-061). The paid coders stay available for a second opinion on a single result, on Eliza's word. The hand labels written before the coder runs remain the check on all of them.
