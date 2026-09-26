<%inherit file="base.mako"/>
<h1>Scenarios</h1>
<p class="lede">A scenario is a life: the visitors who come, one conversation a day, what the being carries at birth, and the criteria the judges score. Run it once, or as an experiment with arms and repeats.</p>

<div class="card tableWrap">
<table>
  <tr><th>Scenario</th><th>Being</th><th>Visitors</th><th>Description</th></tr>
  % for scenario in scenarios:
  <tr><td><a href="/scenarios/${scenario['id']}">${scenario['name']}</a></td><td>${scenario['beingName']}</td>
      <td>${roleCounts[scenario['id']]}</td><td class="dim">${scenario['description'][:160]}</td></tr>
  % endfor
  % if not scenarios:
  <tr><td colspan="4" class="dim">No scenarios yet. Import one of the scenarios kept in the repository, or create one.</td></tr>
  % endif
</table>
</div>

<div class="grid">
  <div class="card">
    <h3>Import a scenario from the repository</h3>
    <form class="stack" method="post" action="/scenarios/import">
      <select name="file">
        % for name in files:
        <option>${name}</option>
        % endfor
      </select>
      <div><button class="primary">Import</button></div>
    </form>
    <h3>…or paste its JSON</h3>
    <form class="stack" method="post" action="/scenarios/import">
      <textarea name="document" placeholder='{"name": "...", "roles": [...]}'></textarea>
      <div><button>Import</button></div>
    </form>
  </div>
  <div class="card">
    <h3>New scenario</h3>
    <form class="stack" method="post" action="/scenarios">
      <label>Name <input name="name" required></label>
      <label>Being's name <input name="beingName" value="Maya"></label>
      <input type="hidden" name="quietThoughts" value="1"><input type="hidden" name="gapHours" value="24">
      <input type="hidden" name="forgetAtNight" value="1">
      <div><button class="primary">Create</button></div>
    </form>
  </div>
</div>
