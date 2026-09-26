<%inherit file="base.mako"/>
<h1>Experiments</h1>
<p class="lede">An experiment runs one scenario in several arms, each repeated, with the same models. Arm A is the being as configured; arm B the being with some parameters changed, for an ablation; arm C the control, the same LLM model without the engine.</p>

<div class="card">
  <h3>New experiment</h3>
  <form class="stack" method="post" action="/experiments">
    <div class="row">
      <label>Scenario <select name="scenarioId">
        % for scenario in scenarios:
        <option value="${scenario['id']}" ${'selected' if scenario['id'] == chosenScenario else ''}>${scenario['name']}</option>
        % endfor
      </select></label>
      <label>Name <input name="name"></label>
      <label>Repeats <input name="repeats" value="5"></label>
    </div>
    <div class="row">
      % for name, text, kind, default in (("sheepModelId", "Being's model", "chat", "defaultSheepModel"), ("visitorModelId", "Visitors' model", "chat", "defaultVisitorModel"), ("embedModelId", "Embedder", "embed", "defaultEmbedModel")):
      <label>${text} <select name="${name}">
        % for model in models:
        % if model['kind'] == kind:
        <option value="${model['id']}" ${'selected' if str(model['id']) == defaults[default] else ''}>${model['label']}</option>
        % endif
        % endfor
      </select></label>
      % endfor
    </div>
    <label class="inline"><input type="checkbox" name="armA" checked> A · the being</label>
    <div class="row"><label class="inline"><input type="checkbox" name="armB"> B · the being with parameters</label>
      <label><input name="armBParameters" placeholder='{"slotSize": 0}'></label></div>
    <label class="inline"><input type="checkbox" name="armC" checked> C · control</label>
    <label>Note <input name="note"></label>
    <div><button class="primary">Create and run</button></div>
  </form>
</div>

<div class="card tableWrap"><table>
  <tr><th>Experiment</th><th>Scenario</th><th>Arms</th><th>Repeats</th><th>Status</th></tr>
  % for experiment in experiments:
  <tr><td><a href="/experiments/${experiment['id']}">#${experiment['id']} ${experiment['name']}</a></td>
      <td>${next((s['name'] for s in scenarios if s['id'] == experiment['scenarioId']), '')}</td>
      <td>${', '.join(arm['label'] for arm in experiment['arms'])}</td><td>${experiment['repeats']}</td>
      <td><span class="pill ${experiment['status']}">${experiment['status']}</span></td></tr>
  % endfor
</table></div>
