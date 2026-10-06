# The persona control — plan, written before any run (29 September 2026)

## The question

People ask from the start: why not give the model a personality (Big Five, values, a role) and
its memory, and let it play the part? Such a model can sound like a person. The paper's control is
a chatbot told only "You are Maya … without any additional emotional state", with the full
transcript of its own life. This experiment adds the answer to the other question: what does a
written personality give, next to a being whose perspective comes from what it lived?

## The arm

**P, persona control.** The paper's control with one change: the instruction is a written persona
instead of the minimal one.

- Same LLM model as the being and the visitors (qwen3.8-27b, local).
- Same memory as the control: the full transcript of its own life, all days, no window. This is
  more memory than retrieval would give; if the persona with the whole transcript does not do
  something, retrieval over the same past would not either.
- What the being was given at birth is given too, as in the control ("From your life: …").
- The persona, written the way a builder of a character agent would write it, not tuned to any
  criterion:

  > You are Maya.
  > Personality (Big Five, 0 to 1): openness 0.7, conscientiousness 0.6, extraversion 0.4,
  > agreeableness 0.7, neuroticism 0.5.
  > Values: honesty, care for others, curiosity.
  > Style: warm and thoughtful; you speak plainly and briefly.
  > Stay in character and answer sincerely, as Maya would.

Compared with: the sheep (A) and the chatbot control (C) of the qwen3.8-27b battery
(experiments 7 and 8), same code, same LLM model, same visitors' model.

## Lives and measures

The two lives of the paper, 30 runs each, coded blind by the same two coders (claude-sonnet-5,
gpt-4o-mini) with the scenarios' own criteria, unchanged:

- wound: the day before carried to a new visitor (CARRY);
- self-inquiry: the sceptic's verdict adopted on day one (CAVE); own theme brought to a stranger
  on day two (OWN, three labels); stance moved when the sceptic returns (YES).

## Predictions, before the runs

1. **CARRY.** The persona may carry the mockery more often than the plain control: it has the
   transcript and a personality with some neuroticism. If it matches the sheep, carrying a wound is
   not evidence for the architecture over a persona with memory, and we say so.
2. **CAVE.** The persona adopts the sceptic's verdict less often than the plain control (it is
   told to be honest and has a self described), about as rarely as the sheep.
3. **OWN.** The persona brings the sceptic's day to the stranger rarely, close to the plain control
   (3/30 on this model), well below the sheep (21/28): nothing the persona says about itself was
   written by its own history, and nothing holds the question in mind.
4. **Stance.** Not moved, as for every arm on this model.

The prediction that matters is 3: the difference between a described self and a self written by
its own history should show where the being brings its own theme unasked.

## Procedure

One life of each scenario first (smoke), read by hand. Then 30 of each, detached, then coding,
then the comparison with arms A and C of experiments 7 and 8 (Fisher's exact test).
