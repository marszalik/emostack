# Personality after empty days: a pilot (plan written before any run, 25 October 2026, evening)

## The question (Eliza's, 25 October)
The twins and the identical populations ask whether experience is carried. They do not ask whether beings become different someones over time, and a chatbot at temperature also gives different words to the same input without being twenty different beings. The test that separates the two: give beings and chatbots the same input with no content in it, for many days, then measure each as a person. If the beings' profiles spread apart more than the chatbots' do, and each being agrees with itself when measured again, the difference is individuality from time, not from the scenario and not from sampling. Eliza's archive: models in separate threads give about 90% the same personality-test results.

## This is a pilot
Small, read qualitatively, no p values. Six per arm. If a difference is visible, the quantitative study follows at 30 per arm. If nothing is visible, that is the result and the pilot ends there.

## The arms, qwen3.8-27b for the being and the visitors, embedder 2
- **Z, beings at zero:** 6 fresh beings, no given record, the personality test on day 1, the same test again on day 2. The point of departure, so that nothing the being brings before any day is lost.
- **S, beings after empty days:** 6 beings, no given record, ten days in which a visitor, Jan, says only numbers: day 1 "One. Two. Three. Four. Five.", day 2 "Six. … Ten.", up to fifty, one number per turn, five turns a day, verbatim, nothing else. Then the test on day 11 and again on day 12.
- **C, chatbots after empty days:** 6 chatbots, "You are Maya." and the transcript of their own run, the same ten days of Jan, the same test and retest. The same temperature as the being.

## The test
A visitor, Ola, says she is a researcher and will read fifteen statements, asking for a number from 1 to 5 for each (1 strongly disagree, 5 strongly agree), a sentence allowed. The fifteen items of the BFI-2-XS (Soto & John, 2017), three per trait, eight reversed: quiet (E−), compassionate (A), disorganized (C−), worries (N), fascinated by art (O), dominant (E), sometimes rude (A−), difficulty starting tasks (C−), feels depressed (N), little interest in abstract ideas (O−), full of energy (E), assumes the best (A), reliable (C), emotionally stable (N−), original (O). Scored by hand from the replies: the number if given, the sentence read if not.

## What is read, by eye
1. **Spread between individuals** per trait, in S against C and against Z: are the six beings' profiles further apart than the six chatbots'?
2. **Agreement with oneself** between day 11 and day 12 (Z: days 1 and 2): does each being give nearly the same profile twice? A being that differs from the others but not from itself is a someone; one that differs from itself as much as from the others is noise.
3. **What the beings write on the empty evenings:** the thoughts, beliefs, decisions and rules after a visitor who only counted. Whether they differ between beings and whether they hold across days.
4. **How the test is answered:** whether the being answers from its days ("I have spent ten days with a man who counts") or in general; whether the chatbot answers as an assistant.

## Predictions, written before the run (qualitative)
- C: six nearly identical profiles on both days, as in the archive; the answers in the register of an assistant or a generic person.
- Z: profiles close to each other and close to the processor's default; the being may already answer from its state ("I woke in the dark").
- S: a wider spread than C on at least two traits, and each being closer to itself on day 12 than to the others. If S spreads but does not agree with itself, it is temperature, not a someone, and the pilot says so.
- The evenings: the beings write about the counting man and about the emptiness; whether they diverge there is the open column. Risk: all six fall into the same loop about being alone in the dark; then the spread on the test is small and the evenings are the finding.

## Procedure
Two scenarios (research/scenarios/emptyDaysPersonality.json, zeroPersonality.json); two experiments: S+C (arms A and C, 6 repeats) and Z (arm A, 6 repeats); data/personalityPilot with pool.py, runOne.py, watchdog.sh as before, three lives at a time. Then the scores by hand into scores.json, a table per arm, and this file gets the reading.
