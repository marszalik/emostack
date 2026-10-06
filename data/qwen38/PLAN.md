# The paper's two lives on qwen3.8-27b, on EmoStack 3 — written before the runs (28 IX 2026)

Replaces the night pool on the old research engine (emoNew/experiments/qwen38_2026-09-27), stopped
because that engine sends no conversation to disposition learning and Qwen then learns nothing.

- Panel experiments 7 (wound, scenario 1) and 8 (self-inquiry, scenario 2): arm A sheep, arm C
  control, 30 repeats each, exactly as the replication on v1.0 except the LLM model:
  qwen3.8-27b (model 5) for the being and every visitor; embeddings local (model 2).
- First four runs (one sheep and one control of each scenario) are a check before the rest:
  the sheep must learn dispositions, replies must make sense. If not, stop and report.
- Then up to 16 lives at once. If the parallel run breaks, fewer, down to one at a time.
- Coding: the panel's blind coding (claude-sonnet-5 and gpt-4o-mini, the scenarios' criteria),
  Fisher's exact test. Nothing is published without Eliza's decision.
