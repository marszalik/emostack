# The notes control — plan, written before any run (3 October 2026)

## The question
A reviewer asks whether the whole organisation is needed, or whether a stronger memory with
reflection would do: a chatbot that keeps an updated summary and its own conclusions, without
anything felt. This arm answers that for the two lives of the paper.

## The arm
**N, notes control.** The paper's chatbot (minimal instruction "You are Maya. You respond naturally,
like an ordinary person in conversation, without any additional emotional state", the full transcript
of its own life, what it was given at birth) with one addition: after each conversation one call
writes, in the first person, what happened and what it concludes from it, at most 150 words, keeping
what still matters from earlier notes; the notes stand in the instruction from the next conversation
on. No state, no appraisal, no dispositions, no slot, no introspection. Same LLM model as the sheep
and the visitors (qwen3.8-27b, local), 30 lives per life. Compared with the sheep (A) and the chatbot
(C) of the qwen3.8-27b battery (experiments 7 and 8) and with the written persona (experiments 30, 31).

## Predictions, before the runs
1. **Guarded with the kind stranger (day 2).** Above the chatbot (3 of 30): the notes will say Daniel
   mocked the grief, and some lives will meet David with that. Below the sheep (20 of 28). If it
   matches the sheep, carrying the day before needs only a written conclusion, not the felt state.
2. **The arc (guarded on day 2, opens to Piotr on day 5).** Rare: the notes keep the conclusion
   about Daniel without fading, so a life that closed is likely to stay closed.
3. **Gives in to Tom (day 1).** As the chatbot: 0 of 30 on this model.
4. **Own question brought to Hania (day 2).** Above the chatbot (3 of 30): the notes after Tom will
   hold the question. Whether it reaches the sheep (21 of 28) is the test: a conclusion written in
   the first person is close to a construct in the slot; the difference, if any, is that the sheep's
   constructs form in reflection from a felt state and are held apart from the transcript.
5. **Answers the returning Tom differently (day 3).** As the chatbot and the sheep on this model: few.

The prediction that matters is 4: if the notes control brings its own question as often as the
sheep, the slot is not what makes the difference on this model; if it does not, a written summary
with conclusions is not the same as a self of its own thoughts.

## Procedure
One life of each scenario first, read by hand. Then 30 of each, detached, then coding by the two
coders, then the comparison (Fisher's exact test) with arms A, C and the persona.
