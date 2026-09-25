<%inherit file="base.mako"/>
<h1>Judges</h1>
<p class="lede">A judge scores each criterion of a scenario on a 1–5 scale. It sees the runs of one repeat together, as series A, B, C, and is never told which is the engine and which the control.</p>
<%def name="judgeForm(judge, action, submit)">
<form class="stack" method="post" action="${action}">
  <div class="row">
    <label>Name <input name="name" value="${judge.get('name', '') | h}"></label>
    <label>Model <select name="modelId">
      % for model in models:
      <option value="${model['id']}" ${'selected' if model['id'] == judge.get('modelId') else ''}>${model['label']}</option>
      % endfor
    </select></label>
    <label>Scores <select name="granularity">
      <option value="turn" ${'selected' if judge.get('granularity') != 'session' else ''}>each turn of the being</option>
      <option value="session" ${'selected' if judge.get('granularity') == 'session' else ''}>each whole conversation</option></select></label>
  </div>
  <label>Instruction <textarea name="instruction">${judge.get('instruction', '') | h}</textarea></label>
  <div><button class="primary">${submit}</button></div>
</form>
</%def>
% for judge in judges:
<details class="card"><summary><strong>${judge['name']}</strong> <span class="dim">· ${judge['granularity']}</span></summary>
  ${judgeForm(judge, "/judges/%d" % judge['id'], "Save")}
  <form method="post" action="/judges/${judge['id']}/delete"><button class="danger">Delete</button></form>
</details>
% endfor
<div class="card"><h3>Add a judge</h3>${judgeForm({}, "/judges", "Add")}</div>
