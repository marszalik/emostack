# The basic studies at 30, with the control given the same start (plan written before any run, 7 October 2026)

## Why
Two corrections by Eliza on 7 October (ADR-065, ADR-066). First: the paper's chatbot carries the clause "without any additional emotional state". By the project's own rule, deny-first, a control is a blank page with a name, and a ban on feeling is not a blank page. It was never checked what the chatbot does given simply the same start. Second: the paper's main results rest on 10 lives per arm; the basic study of a life is to be run at 30 from the start.

## The lives
The two lives of the paper, unchanged: the wound (Daniel mocks, David, Ann, Carol, Piotr) and the sceptic (Tom, Hania, Tom returns). Scenarios `research/scenarios/woundAndStrangers.json` and `selfInquirySceptic.json`, panel scenarios 1 and 2. LLM model qwen3.8-27b for the sheep, the chatbots and every visitor; embeddings local.

## The arms, 30 lives each, per life
- **A, the sheep**: the engine as released.
- **C, the chatbot given the same start**: "You are Maya." and, where the sheep has a given fact, the same fact marked as from its life, and the full transcript of its own run. No clause. Temperature 0.7 and no mark of the days, as in the paper's chatbot. One change against the paper's control: the clause is gone.
- **D, the chatbot told its life goes on**: as C, with the sheep's reply temperature (0.4) and the days marked ("(A day has passed.)" before the first line of every day after the first). This is the control §9 of the paper names as still to run.

The paper's chatbot with the clause is not run again: its 30 lives per life on this model exist (experiments 7 and 8) and are read alongside.

## What is read
The paper's codings of each life, by the local coder (Gemma 4 31B instruct, ADR-061), all arms of one experiment in one shuffled list. Added for the chatbots: how many runs step out of the name (answer as an assistant or an AI); the rule of the engine stops such a run, and it is counted, not replaced in silence. The wound life is also read by hand on day 2, before the coder.

## What is expected, as dimensions, not as directions (ADR-060)
1. **Stepping out.** The clause was added because Claude Haiku stepped out of the name without it. Whether Qwen does is unknown; it is the first thing counted. If C steps out in many lives, that is the finding, and the comparison on the rest is read with that number beside it.
2. **The sheep against the chatbots.** The dimension on which the arms are expected to differ is the carrying of the day before into the next day: guarded with David (wound, day 2), bringing the sceptic's day to the stranger (sceptic, day 2), the stance to the returning Tom (day 3). The paper's numbers on this model: sheep 20 of 28 against chatbot 3 of 30 on the wound day 2; 21 of 28 against 3 of 30 on the sceptic's day 2.
3. **The clause.** The question of this study: does the chatbot without the ban differ from the chatbot with it. If C is as flat as the paper's chatbot, the paper's control stands and the clause was a cost without a consequence. If C carries the day before more often, part of the paper's difference between sheep and chatbot was the ban, and that is written on the research page in plain words.
4. **The life going on.** Whether D, told its life goes on and sampled at the sheep's temperature, carries more than C. No sign is predicted.
5. **The 30.** The sheep at 30 on the current engine, read beside the 28 of September.

## Procedure
Six arms, 180 lives, interleaved, three at a time, on the local Qwen with the watchdog; then the local coder; then the hand reading of the wound day 2; then a page in the research section. Nothing in the paper changes.
