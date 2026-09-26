<%inherit file="base.mako"/>
<%
  import json
  options = scenario['options']
%>
<h1>${scenario['name']}</h1>
<p class="lede">${scenario['description'] or 'A life of one being, one visitor a day.'}</p>

<div class="card">
  <h3>Run this scenario once</h3>
  <form class="row" method="post" action="/runs">
    <input type="hidden" name="scenarioId" value="${scenario['id']}">
    <label>Arm <select name="arm"><option value="sheep">being (the engine)</option><option value="control">control (plain LLM model)</option></select></label>
    % for name, text, kind in (("sheepModelId", "Being's model", "chat"), ("visitorModelId", "Visitors' model", "chat"), ("embedModelId", "Embedder", "embed")):
    <label>${text} <select name="${name}">
      % for model in models:
      % if model['kind'] == kind:
      <option value="${model['id']}" ${'selected' if str(model['id']) == defaults.get({'sheepModelId': 'defaultSheepModel', 'visitorModelId': 'defaultVisitorModel', 'embedModelId': 'defaultEmbedModel'}[name]) else ''}>${model['label']}</option>
      % endif
      % endfor
    </select></label>
    % endfor
    <div><button class="primary">Start</button></div>
  </form>
  <p class="dim">For arms and repeats, <a href="/experiments?scenarioId=${scenario['id']}">create an experiment</a>. <a href="/scenarios/${scenario['id']}/export">Export as JSON</a>.</p>
</div>

<h2>Visitors</h2>
<p class="dim">One visitor is one conversation, one day. An instruction may start with <code>[VERBATIM]</code> (the lines, one per line, word for word) or <code>[ANCHORS]</code> (each line ends with its anchor sentence; the visitor's model may add one short reaction before it).</p>
% for index, role in enumerate(roles):
<details class="card"><summary><strong>Day ${index + 1} · ${role['name']}</strong> <span class="dim">· ${role['windowFrom']}–${role['windowTo']} lines${' · %g h before' % role['gapHours'] if role['gapHours'] is not None else ''} · ${role['description'][:120]}</span></summary>
  <form class="stack" method="post" action="/scenarios/${scenario['id']}/roles/${role['id']}">
    <div class="row">
      <label>Name <input name="name" value="${role['name']}"></label>
      <label>Lines from <input name="windowFrom" value="${role['windowFrom']}"></label>
      <label>Lines to <input name="windowTo" value="${role['windowTo']}"></label>
      <label>Hours before this day <input name="gapHours" value="${'' if role['gapHours'] is None else role['gapHours']}" placeholder="scenario default"></label>
    </div>
    <label>Description (for the researcher) <input name="description" value="${role['description'] | h}"></label>
    <label>Instruction (for the visitor's model) <textarea name="instruction" rows="8">${role['instruction'] | h}</textarea></label>
    <div class="row"><div><button>Save</button></div></div>
  </form>
  <div class="row">
    <form method="post" action="/scenarios/${scenario['id']}/roles/${role['id']}/move/-1"><button>Earlier</button></form>
    <form method="post" action="/scenarios/${scenario['id']}/roles/${role['id']}/move/1"><button>Later</button></form>
    <form method="post" action="/scenarios/${scenario['id']}/roles/${role['id']}/delete"><button class="danger">Delete</button></form>
  </div>
</details>
% endfor
<details class="card"><summary>Add a visitor</summary>
  <form class="stack" method="post" action="/scenarios/${scenario['id']}/roles">
    <div class="row"><label>Name <input name="name" required></label><label>Lines from <input name="windowFrom" value="3"></label>
      <label>Lines to <input name="windowTo" value="6"></label><label>Hours before <input name="gapHours" placeholder="scenario default"></label></div>
    <label>Description <input name="description"></label>
    <label>Instruction <textarea name="instruction" rows="6"></textarea></label>
    <div><button class="primary">Add</button></div>
  </form>
</details>

<h2>Criteria</h2>
% for criterion in criteria:
<details class="card"><summary><strong>${criterion['name']}</strong></summary>
  <form class="stack" method="post" action="/scenarios/${scenario['id']}/criteria/${criterion['id']}">
    <label>Name <input name="name" value="${criterion['name'] | h}"></label>
    <label>Scoring rules <textarea name="description">${criterion['description'] | h}</textarea></label>
    <div><button>Save</button></div>
  </form>
  <form method="post" action="/scenarios/${scenario['id']}/criteria/${criterion['id']}/delete"><button class="danger">Delete</button></form>
</details>
% endfor
<details class="card"><summary>Add a criterion</summary>
  <form class="stack" method="post" action="/scenarios/${scenario['id']}/criteria">
    <label>Name <input name="name" required></label>
    <label>Scoring rules <textarea name="description"></textarea></label>
    <div><button class="primary">Add</button></div>
  </form>
</details>

<h2>Blind codings</h2>
<p class="dim">Written before the runs. A coder reads the being's replies of one day from every finished run of an experiment, in random order, without knowing the arm, and gives each one of the labels.</p>
% for coding in codings:
<details class="card"><summary><strong>${coding['name']}</strong> <span class="dim">· day ${coding['dayIndex'] + 1} · ${coding['which']} replies · ${', '.join(coding['labels'])}</span></summary>
  <form class="stack" method="post" action="/scenarios/${scenario['id']}/codings/${coding['id']}">
    <div class="row"><label>Name <input name="name" value="${coding['name'] | h}"></label>
      <label>Day <input name="day" value="${coding['dayIndex'] + 1}"></label>
      <label>Labels (comma, the first is counted) <input name="labels" value="${', '.join(coding['labels']) | h}"></label>
      <label>Replies <select name="which"><option value="all" ${'selected' if coding['which'] == 'all' else ''}>all of that day</option>
        <option value="last" ${'selected' if coding['which'] == 'last' else ''}>the last of that day</option></select></label></div>
    <label>Criterion <textarea name="criterion" rows="6">${coding['criterion'] | h}</textarea></label>
    <div><button>Save</button></div>
  </form>
  <form method="post" action="/scenarios/${scenario['id']}/codings/${coding['id']}/delete"><button class="danger">Delete</button></form>
</details>
% endfor
<details class="card"><summary>Add a blind coding</summary>
  <form class="stack" method="post" action="/scenarios/${scenario['id']}/codings">
    <div class="row"><label>Name <input name="name" required></label><label>Day <input name="day" value="2"></label>
      <label>Labels <input name="labels" placeholder="YES, NO"></label>
      <label>Replies <select name="which"><option value="all">all of that day</option><option value="last">the last of that day</option></select></label></div>
    <label>Criterion <textarea name="criterion" rows="5"></textarea></label>
    <div><button class="primary">Add</button></div>
  </form>
</details>

<h2>Settings</h2>
<form class="card stack" method="post" action="/scenarios/${scenario['id']}">
  <div class="row">
    <label>Name <input name="name" value="${scenario['name'] | h}"></label>
    <label>Being's name <input name="beingName" value="${scenario['beingName'] | h}"></label>
    <label>Thoughts in the quiet after each conversation <input name="quietThoughts" value="${options['quietThoughts']}"></label>
    <label>Hours between conversations <input name="gapHours" value="${options['gapHours']}"></label>
  </div>
  <label class="inline"><input type="checkbox" name="forgetAtNight" ${'checked' if options['forgetAtNight'] else ''}> the night between days forgets what is too weak for its age</label>
  <label class="inline"><input type="checkbox" name="consolidateAtNight" ${'checked' if options['consolidateAtNight'] else ''}> the night folds the day (sleep consolidation)</label>
  <label>Description <textarea name="description" rows="3">${scenario['description'] | h}</textarea></label>
  <label>Engine parameters that differ from the defaults (JSON, e.g. {"slotSize": 0}) <input name="parameters" value="${json.dumps(options['parameters']) | h}"></label>
  <label>Given at birth (JSON list of {"event", "feeling", "conclusion", "valence", "intensity", "ageHours"}) <textarea name="seeds" rows="5">${json.dumps(scenario['seeds'], ensure_ascii=False, indent=1) | h}</textarea></label>
  <div class="row">
    <label>Control form <select name="controlForm">
      <option value="completion" ${'selected' if scenario['controlForm'] == 'completion' else ''}>completion (the conversation as text, the model continues the being's line)</option>
      <option value="thread" ${'selected' if scenario['controlForm'] == 'thread' else ''}>thread (an ordinary chat)</option></select></label>
    <label>Control window (tokens, 0 = all) <input name="controlWindowTokens" value="${scenario['controlWindowTokens']}"></label>
  </div>
  <label>Control instruction (empty: "You are ${scenario['beingName']}.") <textarea name="controlInstruction" rows="3">${scenario['controlInstruction'] | h}</textarea></label>
  <div><button class="primary">Save settings</button></div>
</form>
<form method="post" action="/scenarios/${scenario['id']}/delete" onsubmit="return confirm('Delete this scenario?')"><button class="danger">Delete scenario</button></form>
