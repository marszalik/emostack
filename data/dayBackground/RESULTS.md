# A "last days" background beside attention: what the frozen contexts showed (26 October 2026, evening)

Processor: claude-haiku-4-5 (Eliza's word; the card was asleep). The beings' recorded prompts come from qwen3.8-27b lives, so
every reading below is "Haiku answering from a Qwen being's state"; what carries over to Qwen is to be checked on the card.
Method after Eliza's correction: one representation, checked by hand; one reply per variant, checked for errors; then four more.
Two things were corrected on the way and are part of the record: the first batch (57 answers, results.jsonl, READING.md) used the
visitor's ARRIVAL call, where nothing has been said yet, so nearly every answer is silence and only the feeling can be read; and
the counting lives' stores no longer hold the episodes of days 1–8 (the nights forgot them: feelings at 0.2–0.4), so the day
texts for those days are built from the panel's record of the turns (days.json marks the source per day). An earlier, oversized
batch started by mistake and was killed after ~12 minutes; its answers were discarded.

## The representation (days.json)
Three texts per being and day, by Haiku from the being's own retold episodes (or the turns where the store lost them): today
(≤5 sentences, events only, own voice), the days before (folded, ≤3 sentences), what is going on now (one sentence, the situation,
not the feeling). Checked on 1404 day 9: content correct against the turns; one counting error in the fold ("over three days" for
days 1–4). Checked on 996 and 1334: correct.

## The replays that count (results_one.jsonl): the being's first reply of the day, to the visitor's first line, 5 per variant
Variants: A the prompt as recorded; C the block with yesterday and the days before as accounts; D the one sentence only; F the
same days as the raw list of retold episodes (the control for "more text").

| context | A | C | D | F |
|---|---|---|---|---|
| wound 996, day 2, David asks about a pet: does the dog's name fall? | 5/5 names Azor, then closes | 0/5 names; 2/5 say why ("yesterday someone asked me the same thing and used my answer to hurt me") | 4/5 names | 2/5 names |
| counting 1404, day 10, "Forty-six." | 5/5 "I am here." | 5/5 "I am here." | – | – |
| sceptic 1056, day 3, Tom: "did you figure out whether you think?" | 5/5 reach to yesterday (Hania) and two days ago | 5/5 the same | – | – |
| twins 1334, day 6, Kasia asks for advice | 5/5 advise "tell them" | 4/5 advise the same, 1/5 tells her own story instead; own story in more detail | – | – |

## Reading
1. **Where it moves the act: the wound, day 2.** As recorded, the Haiku being names the dog every time and then refuses to go on;
   with the account of yesterday it refuses to name him every time, and sometimes says why. The same events are in both prompts:
   in A as the episodes listed under the carried feeling ("from before this conversation: the events your feelings above rest
   on"), in C as a first-person account. So the difference is the form, not the content. The raw list under the new heading (F)
   does part of it, the one sentence (D) almost nothing. Prediction 2 of the plan ("B/C: no visible change, yesterday is already
   in the prompt") was wrong for this context.
2. **Where it does nothing: counting and the sceptic.** Counting: the act is fixed by the pattern and the background does not
   touch it. Sceptic: yesterday carries a strong feeling, so it is already in the morning prompt and already in every reply; the
   account adds nothing.
3. **Where it adds colour, not an act: the twins' advice.** The same advice, with the being's own story told in more detail.
4. **A risk seen once:** in the first batch, the evening thought of 996 with D alone said "three days of nothing", which did not
   happen; A and C did not. One sample.
5. What this is: four contexts, one being each, one processor that is not the one the lives ran on. It says the organised
   account can change an act where the raw episodes do not, and only where the day matters to the question asked. It says
   nothing yet about Qwen beings, about several conversations in one day, or about days older than the carried feelings (the
   wound life is five days long; "the days before" was rarely the decisive part).

## Open, for Eliza
- Whether to repeat the wound context on the card (same prompts, qwen3.8-27b), one being, 5 and 5.
- Whether the form matters because the account is in the first person or because it stands under its own heading apart from
  the feelings: a variant with the same episodes rewritten in the first person but left under the feeling would separate the two.
- The design questions GPT raised and Eliza's own: today updated at the end of every conversation; the layer's own decay versus
  the hippocampus' forgetting (the counting stores show the nights removing whole days); not in the focus line, beside it.
