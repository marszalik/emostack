# EmoStack

EmoStack is an affective-cognitive layer over a frozen large language model. It builds a *being*
that lives in its own present: it feels what happens to it, remembers it under those feelings,
thinks about itself in its quiet moments, learns how to meet a kind of situation, and answers from
all of that. The language model is only the processor. It holds nothing between calls and is never
fine-tuned. Everything the being is lives in this layer.

The words *feels*, *thinks* and *learns* name what the layer does, and the paper measures them as
acts. Like the paper, this project does not claim that there is something it is like to be a being
built this way; on that, the traces are the only evidence there is.

This repository holds the working engine with its prompts, a terminal client, a web application,
and the research panel used to run and measure the lives of beings.

The design and the experiments are described in the paper:

> Eliza Marszalik. *What Do Electric Sheep Dream Of? A Being That Is in Its Own Present:
> Artificial Consciousness by Construction, over a Frozen Language Model.* 2026.
> [doi:10.5281/zenodo.22936968](https://doi.org/10.5281/zenodo.22936968)

## The idea in one page

The being has four kinds of **record**:

- an **emo-thought**, which is a felt interpretation of what happened: the feeling in words, the
  conclusion drawn, how pleasant it was and how strong;
- its **episodes**, which are the events under that feeling, kept as they happened and retold in
  the third person;
- a **cognitive construct**, which is what the being thought about itself in reflection: a thought,
  a belief, a decision, a goal or a dream;
- a **disposition**, which is a learned rule of the form *when this happens → this is what I do*.

A fixed **temperament** bends every new feeling.

Records are in view through **containers**. The durable ones are the **hippocampus**, which holds
everything lived, and the **accessibility slot**, which holds three of the being's own constructs.
The momentary ones make up the being's *now*:

- **here and now**, with the **senses**;
- the **associations** the words brought to mind;
- the **state**, which is what it feels;
- the **focus**, which is this conversation;
- the **conversation summary**;
- the **applicable dispositions**.

**Processes** move records between containers:

- **recall**, **appraisal** and **encoding** run in every turn;
- **introspection** runs in reflection;
- **disposition learning** runs when a person leaves;
- **fading**, **consolidation** and **forgetting** run over time and in sleep.

Each call to the language model sees some containers and not others. Those separations are the
design. The appraisal that forms the memory, for example, does not see the mood.

## Layout

```
emostack/      the engine, organised by the concepts above (one class per file)
  core/        machinery with no psychology in it: settings, SQLite, the LLM and embedding clients,
               prompt templates, time
  being/ trigger/ action/ emoThought/ episode/ construct/ disposition/ senses/
  hippocampus/ containers/ laws/
               the elements
  processes/   one package per psychological act, each with its context and its prompt template
  runtime/     when things happen: a turn, a reflection, a conversation, the clock
apps/cli/      talk to a being in the terminal
apps/web-emostack/
               the web application: bring your own model, talk to your beings
research/      the research panel (a web app) and the scenarios of the paper's lives
tests/         the same tree as the code
```

`architecture.md` is the code's constitution: how it is organised and named, and what goes where.

## Requirements

- Python 3.12. The engine uses only the standard library. It uses numpy for faster recall when
  numpy is installed.
- An LLM model behind an OpenAI-compatible chat completions endpoint. The paper's beings ran on
  `claude-haiku-4-5` through Anthropic's OpenAI-compatible endpoint.
- An embedding model behind an OpenAI-compatible `/embeddings` endpoint. The paper used
  `nomic-embed-text-v1.5`, served locally by llama.cpp.
- For the research panel: the packages in `requirements.txt`.

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Configuration

Copy `config.example.json` to `config.json` and fill it in:

```json
{
  "databasePath": "data/emostack.db",
  "processor": {"baseUrl": "https://api.anthropic.com/v1", "apiKey": "…", "model": "claude-haiku-4-5",
                "jsonMode": "jsonSchema"},
  "embedder":  {"baseUrl": "http://127.0.0.1:8897/v1", "apiKey": "", "model": "nomic-embed-text-v1.5"}
}
```

`jsonMode` says how the backend accepts a request for JSON:

- `jsonObject` for most OpenAI-compatible servers;
- `jsonSchema` for backends that take a strict schema;
- `none` for backends that take neither.

Every parameter of the model can be overridden under `"parameters"`. The defaults are the values of
the paper's measured configuration. See `emostack/core/config.py`. `config.json` is ignored by git.

## Talking to a being

```
python3 apps/cli/talk.py --config config.json --being Maya --person Eliza
```

The being is created on first use. The client understands these commands:

- `/leave` ends the conversation, so that the being has its quiet and may learn a disposition;
- `/wait 24` lets 24 hours pass;
- `/tick` runs the clock once, which brings reflection after silence and sleep after a long one;
- `/quit` exits.

## The web application

```
cp apps/web-emostack/config.example.json apps/web-emostack/config.json   # then fill it in
.venv/bin/python apps/web-emostack/app.py --port 8093                    # http://127.0.0.1:8093
```

By default the application serves one person, the owner of the installation, with no sign-in
(`"identity": "local"`). To open it to several people, choose how they are known:

- `"identity": "header"`: a reverse proxy signs people in and passes each person's email in a header
  (`identityHeader`, `X-Auth-Email` by default). The proxy must overwrite that header on every request.
- `"identity": "cookie"`: a sign-in of your own, added as a domain in `apps/web-emostack/domains/`,
  sets the signed cookie of `domains/auth/sessionCookie.py`. The secret is in `COOKIE_SECRET`. The
  application includes every domain that has a `router.py`.

A person's level decides what they can do:

- a guest talks to their own beings;
- a friend also sees the being's inner life: what it holds in mind, what it feels, what came to
  mind and what it has learned;
- an administrator sees every call behind every message and talks on the server's model.

Administrators are named in the settings. The others are given a role on the *people* page.

With `requireUserModel`, everyone but an administrator brings their own model under *my model*.
They choose a provider (Anthropic, OpenAI, Google, or any OpenAI-compatible endpoint) and paste a
key. The advanced settings can give a single kind of call its own model, for example a stronger
model for the reply or a cheaper one for the association filter.

Every person has a store of their own, so that nothing they do touches anyone else's beings and
every cost goes on their own key. A person may take their own copy of a being that has lived. The
server offers these from `snapshots/` in its data folder.

For beings to reflect in the quiet, sleep and forget, run the clock from cron once a minute:

```
* * * * *  cd /path/to/emostack && python3 apps/web-emostack/tick.py
```

## Using the engine from code

```python
from emostack.core.config import config
from emostack.runtime.engine import engine

mind = engine(config.fromFile("config.json"))
conversation, arrival = mind.open("Maya", "Eliza")    # the being may greet
outcome = mind.hear(conversation, "Did you ever have a pet?")
print(outcome.words)                                   # what the being said; empty for silence
mind.leave(conversation)                               # its quiet, then disposition learning
mind.tick()                                            # call periodically: reflection, sleep, forgetting
```

`engine` also accepts your own `processor`, `embedder` and `time` (a `timeSource`). The tests use this to run
the whole engine on a scripted model and a fixed clock.

## Prompts

Every prompt is a `.prompt` template in the package of the process that uses it. The context class
of that process fills it. Nothing a call sends is written anywhere else. Reading the templates and
the context classes shows the full content of every call. The processor records every call in full:
the prompt as sent and the answer as received.

## The research panel

```
.venv/bin/python research/panel.py        # http://127.0.0.1:8090
```

The panel keeps its own database in `data/panel/`. It also keeps a separate memory store for every
life it runs.

1. **Models.** Add the being's LLM model, the visitors' model, an embedder, and optionally a judge or
   coder model. Give a key as a path to a file outside the repository, not as text.
2. **Scenarios.** A scenario is a life. It says:
   - what the being is given at birth;
   - which visitors come, one conversation a day;
   - how many hours pass between conversations;
   - what the night does;
   - the criteria judges score;
   - the blind codings.

   Import the paper's scenarios from `research/scenarios/`:
   - `woundAndStrangers.json`: a loss mocked, then strangers;
   - `selfInquirySceptic.json`: a sceptic who says the being does not think, a stranger, then the
     sceptic again.
3. **Experiments.** An experiment runs a scenario in several arms, each repeated:
   - arm A is the being;
   - arm B is the being with engine parameters changed, which gives an ablation, e.g.
     `{"slotSize": 0}`;
   - arm C is the control: the same LLM model without the engine, told only the being's name.

   Every life is kept turn by turn, with every call to every model.
4. **Blind coding** measures as the paper did. One call per coding goes over the being's replies of
   the coded day from every finished run, in random order, with the arm hidden. The panel counts
   each label per arm and compares the arms with Fisher's exact test.
5. **Judges** score each criterion on a 1–5 scale. They see the arms of one repeat together, as
   series A, B, C. The panel compares the arms with Cliff's delta, the Mann–Whitney test and a
   paired permutation test, with the run as the unit.

To replicate the paper's lives, import the two scenarios and run each as an experiment with arms A
and C and ten repeats. Then code the finished runs with the scenario's codings. The paper reports
what its lives gave and how they were read. A replication is expected to agree within the error of
ten lives, not word for word.

The paper's lives ran on the research version of this engine, before its code was organised for
release. The model, the prompts and the parameters are the same. In three places this release does
what the research code did, where the paper's text describes it differently: a recalled memory does
not take the new event as its own, a thought in the middle of a turn is given the exchange as its
previous thought and is not told that it paused a conversation, and a choice to keep thinking
carries no direction to the next step.

This release was checked by running the paper's lives again on it: ten lives of each scenario, coded
by two LLM coders from the scenarios' criteria. The results agree with the paper's within the error
of ten lives. These lives, their codings and every call they made are published at
https://emostack.com/article/logs-replication-v1-0-wound and
https://emostack.com/article/logs-replication-v1-0-selfinquiry.

## Where the paper is in the code

| paper | code |
| ----- | ---- |
| §4.1–4.3 the being, records, senses, trigger, action | `being/`, `emoThought/`, `episode/`, `construct/`, `disposition/`, `senses/`, `trigger/`, `action/` |
| §4.4 containers | `hippocampus/`, `containers/` |
| §4.6 processes | `processes/`, `runtime/turn.py`, `runtime/reflection.py`, `runtime/clock.py` |
| §4.7 contexts, Fig. 4.4 | the `…Context.py` class and `.prompt` template in each package of `processes/` |
| §5.1 the unit of memory | `emoThought/EmoThought.py`, `episode/Episode.py` |
| §5.2 recall | `processes/recall/` |
| §5.3 state, focus, conversation summary | `containers/State.py`, `containers/Focus.py`, `processes/summarising/` |
| §5.4 what the LLM model sees | `processes/responding/reply.prompt`, `processes/responding/ReplyContext.py` |
| §5.5 the turn and the appraisal | `runtime/turn.py`, `processes/appraisal/` |
| §5.6 persistence and re-consolidation | `processes/encoding/`, `processes/reconsolidation/`, `laws/` |
| §5.7 introspection | `processes/introspection/`, `runtime/reflection.py` |
| §5.8 sleep | `processes/sleep/`, `laws/forgettingThreshold.py`, `runtime/clock.py` |
| §5.9 learned dispositions | `processes/dispositionLearning/`, `processes/dispositionSelection/` |
| §5.10 the accessibility slot, recall by kind | `containers/AccessibilitySlot.py`, `runtime/turn.py` |
| §5.11 parameters | `emostack/core/config.py` |
| §6.1 the chatbot arm | `research/domains/lives/serviceRunControl.py`, `control.prompt` |
| §6.2 the wound life | `research/scenarios/woundAndStrangers.json` |
| §6.2 the self-inquiry life | `research/scenarios/selfInquirySceptic.json` |
| §6.3 blind coders, Fisher's test | the scenarios' `codings`; `research/domains/experiments/serviceCodeBlind.py`, `coding.prompt`, `serviceFisherTest.py` |

The frozen tests of §7 replay single turns on the stores of completed lives. The panel keeps the
store of every life it runs, so that such a replay can be made. The frozen-test scripts themselves
are not part of this release.

## Tests

```
python3 tests/runTests.py
```

The tests run the engine on a scripted LLM model and a word-hashing embedder, so they cost nothing.
The panel's tests need the packages in `requirements.txt`.

## License

EmoStack is source-available under the [PolyForm Noncommercial License 1.0.0](LICENSE.md). You may
read, run, copy, change and share it for any noncommercial purpose: research, study, teaching,
personal use, and use by noncommercial and public research organisations. That includes replicating
and extending the paper's experiments and publishing the results. Commercial use is not licensed.
For a commercial license, write to the author.

This is not an open-source license in the sense of the Open Source Initiative, because it does not
allow commercial use.

## Author

Eliza Marszalik.
