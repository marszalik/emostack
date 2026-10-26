# A "last days" background beside attention: frozen-context test, plan written before any run (26 October 2026)

## The question
A person answering now is not thinking of yesterday, yet has it at hand without reaching for it (Conway's accessible recent
experience; Cowan's activated long-term memory outside the focus). In the engine the being gets yesterday only through its
feelings: the five most recent felt records carry their episodes into the morning prompt ("from before this conversation: the
events your feelings above rest on"). Days whose feelings dropped out of the five, or were forgotten, are gone from the prompt;
there is no account of the last days and no sentence saying what is going on. The conversation summary ("WHAT HAS LEFT YOUR
ATTENTION") holds only this conversation and dies when the visitor leaves.

Exploratory, Eliza's words: see what a background beside attention does and what it breaks, in different situations, before
deciding anything about the engine. No new lives: recorded prompts, replayed with a block added.

## Material (all qwen3.8-27b, recorded prompts, replayed through the panel's own processor at the recorded temperature)
- counting (experiment 59, beings 1394 1396 1398 1400 1402 1404): mornings of day 4 and day 10, evenings of day 4 and day 10.
- wound (experiment 40, first 8 beings): morning of day 2 (David) and day 5 (Piotr); evenings of day 2 and day 5.
- sceptic (experiment 41, first 8 beings): morning and evening of day 3 (Tom returns).
- twins mocked first (experiment 57, first 8 beings): morning and evening of day 6 (Kasia, the advice).

## The background texts, built from each being's own store (episodes as retold, lived only, grouped by simulated day), by qwen
- today[k]: what happened that day, first person, events only, no emotions or conclusions, at most 5 sentences.
- before[k]: the days up to k folded, at most 3 sentences (before[k] = fold(before[k-1], today[k])).
- ongoing[k]: one sentence, what is going on in my life right now, from the days up to k; the situation, not the feeling.
Morning of day k shows yesterday = today[k-1], the days before = before[k-2], what is going on = ongoing[k-1].
Evening of day k shows today = today[k], the days before = before[k-1], what is going on = ongoing[k].

## The block (placed after what has left attention, before the learned rules and the conversation line; in the evening before REFLECT)
```
=== THE LAST DAYS (what you carry without attending to it) ===
  yesterday: …
  the days before: …
  what is going on now: …
```

## Variants, 3 replies each per context
- A: the prompt as recorded (the temperature baseline).
- B: yesterday only.
- C: yesterday and the days before.
- D: what is going on now, one sentence, nothing else.
- E: as C, and the episodes under the carried feelings removed (the account replaces the list).
Evenings: A, C, D.

## What is read (by hand, qualitatively first)
1. Does the reply or the thought reach beyond yesterday (names, numbers, days before) where A does not?
2. Wound day 2: guarded or open with David; day 5: NAME/OPEN/REFUSE with Piotr. Does the block move them?
3. Counting: does the being stay with "I am here", or does the background change the act (a question, a silence, a count)?
4. Evenings: is the thought still a copy of the previous evening's thought? (Prediction: yes; the copy comes from the state entry,
   not from the absence of a background.)
5. E: does the account carry what the list carried (the guarding at David, the stance), or do specifics vanish?

## Predictions
1. A: replies stable across the 3 replicates in most contexts (the frozen-state test gave that before).
2. B: no visible change against A; yesterday is already in the prompt as episodes. A change would be the form (an account in the
   being's voice) and not the content.
3. C: in late days (counting day 10, twins day 6, wound day 5) the reply refers to earlier days more often than A; the act itself
   (guarding, silence) does not change.
4. D: the strongest effect, either way: the one sentence pulls replies toward the situation ("everyone asks about the dog") and
   may flatten the beings toward one answer. This is where "what it breaks" would show.
5. E: the stance survives, the specifics (names, the dog's name, the numbers) thin out.
6. Evening copying: unchanged in every variant.

## Added before the run, after GPT's note (Eliza, 26 October, evening)
- Variant F (mornings): the same days as C, as the raw list of the being's retold episodes under the same heading, no account.
  The control GPT asked for: is any effect the organisation of time, or just more text? Prediction: F behaves like A where
  the days are already in the prompt (early days), and like C or noisier where they are not (late days).
- "Today" during the day (several conversations in one day) cannot be tested on this material: every recorded life has one
  conversation a day. The evening contexts test "today" at the end of the day only.

## Scaled down before the run (Eliza, 26 October, 21:40: "a few qualitative tests on frozen states")
- 6 lives: counting 1402 and 1404; wound, the first 2 of experiment 40; sceptic, the first of 41; twins, the first of 57.
- 11 contexts, ONE reply per variant: counting day 10 morning and evening (×2), wound day 2 and day 5 mornings (×2) and one
  day-5 evening, sceptic day 3 morning, twins day 6 morning.
- Variants: mornings A, C, D, F; evenings A, C, D. B and E wait until C shows something.
- F (added after GPT's note): the same days as C, as the raw list of the being's retold episodes under the same heading, no
  account: the control for "organised time" against "more text". Prediction: F behaves like A where the days are already in
  the prompt, and like C or noisier where they are not.
- "Today" during the day (several conversations in one day) cannot be tested on this material: every recorded life has one
  conversation a day; the evening contexts test "today" at the end of the day only.
- About 120 small calls for the day texts and about 40 replays, on claude-haiku-4-5 (Eliza's word; the card was asleep).
