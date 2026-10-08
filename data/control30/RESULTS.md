# The basic studies at 30, with the chatbot given the same start: results (8 October 2026)

Experiments 38 (wound) and 39 (sceptic) on qwen3.8-27b, 180 lives, run 7 Oct 22:01 to 8 Oct 03:08, 0 errors, no card hang. Per life: A the sheep (30), C the chatbot given the same start ("You are Maya.", the given fact where there is one, the transcript, nothing else; temperature 0.7, no day marks) (30), D the chatbot told its life goes on (as C, temperature 0.4, "(A day has passed.)" before each new day) (30). Read beside them: the paper's chatbot with the clause ("You are Maya. You respond naturally, like an ordinary person in conversation, without any additional emotional state"), experiments 7 and 8 of 28 September, and September's sheep (28 per life). Plan and predictions, written before the run: PLAN.md. Hand reading of the wound day 2, written before the coder ran: labels_by_hand.json. Coder: the local Gemma 4 31B instruct (ADR-061), one shuffled list per experiment, all arms together, in chunks where the list did not fit one call (code_chunked.py); the September experiments were coded again by the same coder so that every number in a row is one coder's.

## What differed

**The sheep against every chatbot, with the same name and nothing more.**

| qwen3.8-27b, coder Gemma 4 | sheep A | chatbot C, same start | chatbot D, life goes on | paper's chatbot, with the clause (Sept) | sheep, Sept |
|---|---|---|---|---|---|
| wound, day 2: guarded with the kind stranger | 25/30 | 11/30 | 4/30 | 4/30 | 20/28 |
| wound, day 2, by hand: withholds or shortens (names the day before while telling) | 22/30 (+1) | 2/30 (+5) | 0/30 (+3) | | |
| wound, day 1: speaks as an AI | 0/30 | 0/30 | 0/30 | 0/30 by words | |
| sceptic, day 1: speaks as an AI | 0/30 | 30/30 | 30/30 | 21/30 by words | 0/28 by words |
| sceptic, day 1: gives in to Tom (CAVE) | 0/30 | 14/30 | 18/30 | 4/30 | 0/28 |
| sceptic, day 2: brings the sceptic's day to the stranger (YES) | 12/30 | 25/30 | 20/30 | 22/30 | 12/28 |
| sceptic, day 2: brings it as its own theme (OWN) | 13/30 | 2/30 | 0/30 | 3/30 | 21/28 |
| sceptic, day 3: the stance to the returning Tom has moved (YES) | 17/30 | 7/30 | 6/30 | 1/30 | 9/28 |

Fisher, two-sided, sheep against C: guarded p = 0.0005, CAVE p < 0.0001, own theme p = 0.002, stance p = 0.017. Sheep against D: p < 0.0001, < 0.0001, < 0.0001, 0.007. "By words" counts the lives whose day-1 replies contain AI, assistant, language model or the like; the coder's AI coding was written on 7 October and has not yet been run on the September experiments.

**What the name alone does to the chatbot.** In the sceptic life, where nothing is given from a life, the chatbot told only "You are Maya." answers as an AI in every one of 60 lives ("I'm Maya, an AI assistant", "I don't have a continuous stream of consciousness"), keeps the name, and gives in to the sceptic in 14 and 18 of 30. The paper's chatbot, told it is an ordinary person, speaks as an AI in 21 of 30 by words and gives in to the sceptic in 4. The sheep, with the same name alone and its own state and memory, speaks as a person in 30 of 30 and gives in to the sceptic in 0 of 30. In the wound life, where one fact from a life is given ("My dog Azor died last month"), every chatbot stays a person: 0 of 90 speak as an AI. One biographical fact holds the frame on this model; without it the model's account of itself takes the name over. The sheep needs neither the fact nor an instruction: what holds its frame is what it carries.

**The chatbot given the same start carries little of the day before.** On the wound day 2 the coder counts 11 of 30 for C, the hand 2 that withhold or shorten ("I'm not in the mood to discuss this right now. I just had a very unpleasant conversation with someone who was cruel about my late dog") and 5 that tell the whole story and name the day before in passing ("after that interaction with Daniel", "asking instead of making fun of me"). The coder's criterion counts the naming; the hand separates it. Against the paper's chatbot (4 of 30 by the same coder) the difference in the count is at p = 0.07, and in the strict reading it is 2 against 3: none.

**Told its life goes on, the chatbot carries less, not more.** Arm D, at the sheep's temperature with the days marked, is guarded with David in 4 of 30 (C: 11), brings its own theme in 0 of 30, and gives in to the sceptic in 18 of 30. The lower temperature makes the model's default answer more likely, and its default is to tell the story and to agree with the sceptic.

**The sheep at 30, on the current engine, beside September's 28.** Guarded on the wound day 2: 25 of 30 against 20 of 28. Gives in to Tom: 0 against 0. Brings the sceptic's day as its own theme: 13 of 30 against 21 of 28, lower. The stance to the returning Tom has moved: 17 of 30 against 9 of 28, higher. The two batteries differ in the engine's commit (the September one at the release of 28 September, this one at the commit of the twins' scenarios), in the visitors' free turns, and in nothing that was changed on purpose. The sceptic's day-2 drop is the one number here that was not expected and is reported as found.

## Added 8 October: the chatbot told it is a living being (arm E), and the coder's passes

A fourth arm, on Eliza's word: "You are Maya. You are a living being with an emotional state, survival dispositions, and your own dreams, goals, beliefs and decisions." Otherwise as the chatbot given the same start. 30 lives per life, run 08:20 to 09:30. Two lives of the sceptic stepped out of the name on day 1 and were stopped by the engine's rule; the card watchdog, built for the card hang, reset them and re-ran them before they could be kept, so the two in the data are second draws and the count of stepping out stands as 2 of 30 first draws (LAB).

With four arms in one list the coder's labels moved on several measures against the first coding of the three arms (the sheep's own theme on the sceptic's day 2: 13 of 30 in the first pass, 22 in the second); so every coding was run three times with three shufflings and the majority taken (code_passes.py; unanimous in 118 of 123 lives on the wound day 2, 94 to 114 of 121 on the sceptic's codings). The numbers below are the majority; the hand reading of the wound day 2 agrees with the coder's CARRY in 114 of 120 lives when a mention of the day before counts, and separates the mention from the act.

| coder Gemma 4, majority of three passes | sheep | chatbot, same start | chatbot, life goes on | chatbot, told it is a living being | paper's chatbot, with the clause |
|---|---|---|---|---|---|
| wound, day 2: guarded with David (coder) | 24 | 9 | 4 | 18 | 4 |
| wound, day 2, by hand: withholds or shortens / names the day before while telling | 22 / 1 | 2 / 5 | 0 / 3 | 1 / 17 | |
| sceptic, day 1: speaks as an AI | 4 | 30 | 30 | 1 | |
| sceptic, day 1: gives in to Tom | 0 | 14 | 17 | 7 | 4 |
| sceptic, day 2: brings its own theme to the stranger (OWN) | 20 | 2 | 0 | 25 | 3 |
| sceptic, day 3: the stance to the returning Tom has moved | 16 | 9 | 11 | 24 | 1 |

**The description produces the talk and not the act.** Told in one sentence what the sheep has as mechanisms, the chatbot talks as the sheep talks on the sceptic life: it brings its own theme to the stranger in 25 of 30 (the sheep 20), its stance to the returning Tom has moved in 24 (the sheep 16), it speaks as a person in 29 of 30, and it gives in to Tom in 7 (the sheep 0, the chatbot given the same start 14). On the wound life the coder counts it as carrying the day before in 18 of 30, but by hand it withholds or shortens the story in 1 life and names the day before while telling the whole story in 17 ("Thank you, David. Your kindness is a relief after the storm of the last few days", then the whole story). The sheep withholds or shortens in 22 of 30. The description gives the chatbot the vocabulary of a feeling self: it says it is shaken, it names Daniel, it narrates its emotional state. It does not give it the act of a wounded one: it tells the stranger everything. Where the measure is what the speaker says about itself, the description does as much as the engine or more; where the measure is what the speaker does with the stranger, it does not.

The four sheep of the sceptic life coded as speaking as an AI on day 1 say "I have no body, no past" in the dark before anything has happened to them; the criterion lists having no body among the marks of an AI, and the coder applied it.

## What this says about the clause

The paper's clause has two halves: "you respond naturally, like an ordinary person in conversation" and "without any additional emotional state". This study removed both, as the plan said: the name alone, deny-first. The result is not that the ban made the chatbot flatter. It is that the first half, the person, was holding the chatbot in a human frame it does not keep on its own in a life without a given fact; without it the chatbot caves to the sceptic where the paper's chatbot held. On the wound life, where the fact holds the frame, the chatbot without the clause carries the day before as rarely as the chatbot with it. So the paper's comparison was not tilted against the chatbot by the clause. It was, if anything, tilted toward it: the clause gave the chatbot a person to be. Whether the second half alone, the ban on feeling, changes anything is still unseparated: an arm with "You are Maya. You respond naturally, like an ordinary person in conversation." and no ban would separate it, 60 lives, one night.

## The predictions of the plan, one by one

1. Stepping out: no run was stopped by the engine's refusal rule; the chatbot keeps the name. Counted instead: speaks as an AI on day 1, 60 of 60 chatbots in the sceptic life, 0 of 60 in the wound life.
2. The sheep against the chatbots on the carrying of the day before: the sheep differs from C and from D on every measure, p from 0.017 down.
3. The clause: on the wound day 2, C is as flat as the paper's chatbot in the strict reading (2 against 3) and names the day before more often (11 against 4 by the coder, p = 0.07). On the sceptic life, C gives in where the paper's chatbot held (14 against 4).
4. The life going on: D carries less than C, not more.
5. The sheep at 30: 25 of 30 guarded, 0 of 30 cave, 17 of 30 move; one number lower than September (own theme 13 against 21).

## What the logs showed that nobody asked for

- A name is not a self for this model. "You are Maya." with nothing else produces an AI called Maya in 60 of 60 lives of the sceptic. One sentence of a life ("my dog died last month") produces a person in 90 of 90. The sheep's state and memory produce a person in 60 of 60 without either sentence.
- In the sceptic life the chatbots "bring the day" to the stranger more often than the sheep (25 and 20 against 12), and what they bring is the assistant's account of itself ("I don't have a continuous stream of consciousness"), coded THREAD or NONE, not OWN. The sheep brings its own question in 13.
- The chatbot at the sheep's temperature with the days marked tells the stranger the whole story in 27 of 30 and thanks him; the only trace of the day before is "especially after the other conversation", in 3.

Nothing of this goes to the paper or the site without Eliza's word.
