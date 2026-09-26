# EmoStack 3 — code architecture

## Main rule

**The code is organised by the concepts of the ontology, not by technical layers.**

Everything about one concept lives together: its class, its types, its storage, its tests.
A reader who knows the concepts finds each of them in the code by its name.

There are no global directories such as `services/`, `models/`, `utils/`, `templates/`, `prompts/`.

## Naming

1. **An identity class is written with a capital letter, and so is its file.**
   An identity class is a thing of the ontology: an element, a record, a container, a type, a context.
   `class Being` lives in `Being.py`. `class Belief` lives in `Belief.py`.
2. **A service class is written in camelCase starting with a small letter, and so is its file.**
   A service class does something: a process, a repository, a factory, a loader, a runner.
   `associationFilter.py`, `hippocampusRepository.py`, `actionFactory.py`.
3. **No underscores inside names.** Not in files, directories, classes, methods or variables.
   Multi-word names are camelCase: `dispositionLearning/`, `feltAt()`, `beingId`.
   The one exception: a private method or attribute starts with a single underscore: `_buildContext()`.
4. **Methods and variables are camelCase,** starting with a small letter: `isActive()`, `execute(turn)`.
5. **Names follow the ontology,** in English, without abbreviations.

## Rules

1. **One file = one class.**
2. **One package = one concept** of the ontology, together with its typology.
3. **A type that changes behaviour is a subclass.** Trigger kinds, action kinds and construct types are subclasses.
4. **A type that is only a label is an enum in its own file.** Examples: `Origin`, `Rendering`, `SlotPlace`.
5. **One process = one package.** The process, the context it shows to the LLM model and its prompt template sit together.
   This is the same idea as router + service + view in one web domain.
6. **One operation = one class.** No large `service.py`, no class that runs the turn, builds contexts and stores records at once.
7. **Dependencies go one way:** `runtime → processes → elements → core`.
   An element never imports a process. A process never imports the runtime.
8. **Comments explain what the code does now.** History belongs to git and the changelog.

## Repository and prompts

- **EmoStack 3 is public code in its own git repository.**
- **The repository holds the working engine with its prompts.** The prompts are the ones the engine runs with, not simplified or sample versions.
- **Each prompt is a template file (`.prompt`) in the package of the process that uses it.** The process's context class fills it.
- **Nothing a call sends is written outside a template.** Reading the templates and the context classes shows the full content of every call.

## Directory structure

```
emostack/
  core/                             # shared machinery, no psychology in it
    config.py                       # settings and runtime paths
    database.py                     # SQLite connection and schema migrations
    processor.py                    # the LLM model interface
    openAiCompatibleProcessor.py    # its implementation
    embedder.py                     # the embedding interface
    localEmbedder.py                # its implementation
    promptTemplate.py               # loads and fills a process's template
    timeSource.py                   # now(); replaced by a fixed clock in tests

  # ---- elements -------------------------------------------------------

  being/
    Being.py                        # identity, wakefulness, owner of the containers
    Wakefulness.py                  # Awake | Asleep
    Temperament.py                  # valence bias, intensity amplification; apply(emoThought)
    beingRepository.py

  trigger/                          # what reaches the being from the world
    Trigger.py                      # base: who, when, channel
    Utterance.py                    # someone speaks -> a reply
    Arrival.py                      # someone enters -> a record without a reply
    Departure.py                    # someone leaves -> the conversation closes
    Channel.py                      # Text (later Image, Sound)

  action/                           # what the being does; one subclass per kind
    Action.py                       # base: target, execute(turn)
    ActionTarget.py                 # World | Memory | Self
    Speak.py
    StaySilent.py
    SearchMemory.py
    Think.py                        # reflection before the reply
    KeepThinking.py                 # reflection only
    FormConstruct.py                # reflection only; the construct enters the slot
    DoNothing.py
    actionFactory.py                # the model's answer -> the right subclass

  emoThought/
    EmoThought.py                   # feeling, conclusion, valence, author, time, vector
    Author.py                       # Person(name) | Self
    Origin.py                       # Lived | Given
    Strength.py                     # intensity + time of refresh; feltAt(now)

  episode/
    Episode.py                      # one event under a feeling; belongs to one emo-thought
    Rendering.py                    # AsItHappened | Retold

  construct/                        # what the being wrote about itself
    CognitiveConstruct.py           # base: author Self, no episodes, never in State, protected from sleep
    Thought.py
    Belief.py
    Decision.py
    Goal.py
    Dream.py
    SlotRole.py                     # Act (Decision, Goal, Dream) | HeldByStrength (Belief, Thought)

  disposition/
    Disposition.py                  # situation -> act, weight, count; isActive()
    Situation.py                    # the part that selection matches
    dispositionRepository.py

  senses/
    Senses.py                       # the channels; the head of every context
    Hearing.py                      # words | arrival | departure | nothing
    HearingNote.py                  # structural note: a moment the being has no memory of
    EmptySense.py                   # sight, touch, smell and taste, body, place: say they carry nothing
    AttentionAndMemory.py           # counts, and this turn's searches with their results

  hippocampus/                      # everything lived
    Hippocampus.py                  # all records of one being
    hippocampusRepository.py        # SQLite

  containers/                       # one class per container
    HereAndNow.py
    Association.py                  # record + origin (Involuntary | Deliberate) + destination (State | Focus)
    Associations.py
    State.py                        # budget, ordered by felt strength
    Focus.py
    FocusEntry.py                   # ThisConversation | EvokedFromBefore
    ConversationSummary.py
    AccessibilitySlot.py            # three places, seven days
    SlotPlace.py                    # Reserved | Free
    ApplicableDispositions.py

  laws/                             # the rules of strength, in one place
    fadingLaw.py                    # negative fades 1.5x slower
    forgettingThreshold.py
    reconsolidationLaw.py           # valence moves toward what is felt now

  # ---- processes: the psychological acts of the ontology ---------------

  processes/
    recall/
      recall.py                     # similarity x strength, names, episodes
      associationFilter.py
      AssociationFilterContext.py
      associationFilter.prompt
    appraisal/
      appraisal.py                  # the isolated appraisal of what to keep
      AppraisalContext.py
      appraisal.prompt
    encoding/
      encoding.py                   # a new record, or an episode under an existing one
    reconsolidation/
      reconsolidation.py
    responding/
      responding.py
      ReplyContext.py
      reply.prompt
    introspection/
      introspection.py
      IntrospectionContext.py
      introspection.prompt
    summarising/
      summarising.py
      SummarisingContext.py
      summarising.prompt
    dispositionSelection/
      dispositionSelection.py
      DispositionSelectionContext.py
      dispositionSelection.prompt
    dispositionLearning/
      dispositionLearning.py
      DispositionLearningContext.py
      dispositionLearning.prompt
      DispositionClassificationContext.py
      dispositionClassification.prompt
    fading/
      fading.py
    sleep/
      sleep.py
      ConsolidationPlanContext.py
      consolidationPlan.prompt

  # ---- runtime: when things happen ------------------------------------

  runtime/
    Conversation.py                 # one conversation, from Arrival to Departure
    turn.py                         # the fast path of one turn
    reflection.py                   # the chain of up to three steps
    presence.py                     # parallel conversations
    clock.py                        # the slow path: silence, sleep, waking

apps/
  web/                              # the web app, organised like every other web project
    domains/
      core/                         # config, templates, views/base.mako, static/
      chat/                         # router.py, serviceSendMessage.py, views/, static/
      beings/                       # router.py, serviceCreateBeing.py, ...
      auth/
  cli/

research/                           # scenario runner, test panel, experiments
tests/                              # the same tree as emostack/
```

## What goes where

**`core/`** holds machinery that knows nothing about feelings: configuration, the database connection, the LLM model and embedding clients, template loading, the time source.
If a piece of code needs a word from the ontology, it does not belong in `core/`.

**Element packages** (`being/` … `laws/`) hold what the ontology calls elements and their typologies.
They are plain Python. They do not call the LLM model.
A repository sits in the package whose data it stores.
Only repositories use SQL.

**Process packages** hold one psychological act each.
A process that calls the LLM model keeps three things side by side:
- the process class, which decides what to do;
- the context class, which decides what the model sees;
- the prompt template, which decides how it is worded.

A context never builds text by string concatenation spread over the code. It fills its template.

**`runtime/`** decides when processes run: a turn, a reflection, a conversation, the clock.
It holds no rule of psychology itself.

**`apps/`** and **`research/`** use the engine through `runtime/`. The engine never imports them.
`apps/web` follows the general web architecture: domains, a thin `router.py`, one `service<Operation>.py` per operation, `views/` and `static/` inside the domain.

## How objects talk

- Every call to the LLM model receives a context object. Nobody sets attributes on another object before calling it.
- A process returns a result object. The runtime passes it on.
- Every call is recorded in full: the prompt as sent and the answer as received.

## Adding something

A new concept:
1. Add it to the ontology first.
2. Create its package, one class per file, named as in the ontology.
3. Put its storage in a repository inside the package.
4. Mirror the package in `tests/`.

A new process:
1. Create `processes/<name>/`.
2. Add the process class, and if it calls the LLM model, its context class and template.
3. Call it from `runtime/`, not from another process.

A new kind of action or trigger:
1. Add a subclass in `action/` or `trigger/`.
2. Register it in the factory.
No `if kind == ...` anywhere else.

## What to avoid

- one large class that runs the turn, builds contexts and stores records;
- a concept that exists only as a string field (`kind = "belief"`) or a dict;
- global `prompts/`, `services/`, `models/` or `utils.py`;
- SQL outside repositories;
- the same rule of strength written in several places;
- feature flags that no longer change anything;
- underscores inside names (a leading underscore marks only what is private);
- history in comments.
