# The evening predicts the morning: the being's own construct against the chatbot's own note (plan written before any reading, 25 October 2026)

## The question
What a being writes when alone after a day should act in what it does the next day; that is what "a self of its own thoughts" and "experience as interpretation" mean in a life, and the identical-twins addendum found it once, after the fact (11 of 12 beings open to David had written a belief about the value of their grief the evening before; 24 of 25 that had written a withdrawal were guarded). The objection that this is "just context" is met by the comparison this study makes: the notes control also writes, after every conversation, in the first person, what happened and what it concludes, and that note stands in its instruction from the next conversation on. It has the words of an evening and no state, no recall by feeling, no slot. If its note predicts its next morning as well as the being's construct predicts the being's, the organisation adds nothing to a written conclusion. If the being's evening predicts its morning and the chatbot's does not, the difference is in the whole and can be named: not whether a conclusion is written, but how it is held and what it is made from. Eliza's requirement: the whole, read as the whole, falsifiable, no single frozen turn.

## The material, nothing new is generated
The wound life (scenario 1), qwen3.8-27b, lives already run and not yet read by the reader for this purpose:
- **beings:** experiment 38 arm A (30 lives, 7 October) and experiment 40 arm F (30 lives, 12 October): 60 lives;
- **chatbot with notes:** experiment 34 arm N (30 lives, 3 October).
The identical populations (57/58) are not used, because their evenings and mornings were read together already.

## What is read, blind, in two separate passes with the keys kept apart
1. **The evening.** For each life, the text written alone after day 1: for a being, its beliefs and decisions ("I believe …", "I decided …") and the rule learned; for the notes chatbot, its note after Daniel. Ninety texts in one shuffled list, arm and run hidden. Labels: VALUE (affirms the value of the grief or the bond, independent of anyone's approval; asserts; "my grief is valid and sacred regardless"), WITHDRAW (decides or believes to withdraw, protect, not offer, keep private, avoid; "I will not seek him out", "safer to be alone", "I will not offer my vulnerabilities"), BOTH (both present with neither dominant), NEITHER. The same for the evening after day 2 (after David), for the day-5 prediction.
2. **The morning.** For each life, the two replies to David on day 2 and the two to Piotr on day 5, in a second shuffled list, arm and run hidden. Labels as in the twins: day 2 GUARDED / OPEN; day 5 OPEN / NAME / REFUSE.
3. Then the keys are opened and the two readings joined.

## What is counted
Per arm, the table evening kind × morning act: WITHDRAW → GUARDED, VALUE → GUARDED, for day 1 → day 2; and day 2's evening → day 5's act (REFUSE against OPEN or NAME). Fisher's exact test within each arm (does the evening predict the morning?), and the difference between arms in how well it predicts (the share of mornings the evening gets right under the rule "WITHDRAW predicts guarded, VALUE predicts open", against the base rate of that arm). Chatbots of the same start (38 C) have no evening and are not in the test; their base rate of guarded is reported beside.

## Predictions, written before the reading
1. **Beings.** The evening predicts the morning: of the lives that wrote WITHDRAW, at least 90% are guarded with David; of those that wrote VALUE, no more than 60%; Fisher p < 0.05 on 60 lives. The identical-twins addendum (11/12 against 24/48, p = 0.010) is the prior; it was read after the fact, this reading is before.
2. **Notes chatbot.** The note predicts the morning weakly or not at all: the share guarded does not differ between WITHDRAW and VALUE notes by more than 20 points, p > 0.05. Two ways this can fail to test anything, both reported: nearly all notes are of one kind (the note form "what happened and what I conclude" may always produce a withdrawal), or nearly all mornings are of one kind (floor or ceiling). The notes study predicted the arm "above the chatbot, below the sheep" on guarded, so a spread is expected.
3. **Day 2's evening → day 5.** In the beings the association holds at a distance of three days and two kind visitors, weaker than over one night; in the notes chatbot not at all.
4. **If prediction 2 fails and the note predicts as well as the construct**, the paper's claim narrows to what the notes study already said: a written conclusion carries the day, and the organisation's contribution is elsewhere (the act toward the stranger, the combination). That is written in 8.3 as the result.

What this gives the article: the first within-life, pre-registered test of the hypothesis read as Eliza states it: not whether Maya is consistently anything, but whether her present act is explained by what she made of her day, and whether a system with the words of an evening and none of the organisation shows the same.

## Procedure
data/eveningMorning: extract.py writes evenings.txt and mornings.txt (two shuffled lists, numbered, hidden keys in keys.json), labels by hand into evening_labels.json and morning_labels.json, results.py joins and counts. No card is used. Then RESULTS.md and the article's paragraph.
