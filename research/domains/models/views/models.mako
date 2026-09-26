<%inherit file="base.mako"/>
<h1>Models</h1>
<p class="lede">The LLM models and embedders the panel runs with. Keep a key in a file outside the repository and give its path; the panel stores the path, not the key.</p>

<%def name="modelForm(model, action, submit)">
<form class="stack" method="post" action="${action}">
  <div class="row">
    <label>Label <input name="label" value="${model.get('label', '')}"></label>
    <label>Kind <select name="kind">
      <option value="chat" ${'selected' if model.get('kind') != 'embed' else ''}>chat</option>
      <option value="embed" ${'selected' if model.get('kind') == 'embed' else ''}>embed</option></select></label>
    <label>Model <input name="model" value="${model.get('model', '')}" required></label>
  </div>
  <div class="row">
    <label>Base URL <input name="baseUrl" value="${model.get('baseUrl', '')}" required></label>
    <label>Key file <input name="apiKeyFile" value="${model.get('apiKeyFile', '')}" placeholder="path/to/key.txt"></label>
    <label>Key <input name="apiKey" type="password" placeholder="${'(kept)' if model.get('apiKey') else ''}"></label>
  </div>
  <div class="row">
    <label>JSON mode <select name="jsonMode">
      % for mode in ("jsonObject", "jsonSchema", "none"):
      <option ${'selected' if model.get('jsonMode', 'jsonObject') == mode else ''}>${mode}</option>
      % endfor
    </select></label>
    <label>Max tokens <input name="maxTokens" value="${model.get('maxTokens', 2048)}"></label>
    <label>Max tokens field <input name="maxTokensParam" value="${model.get('maxTokensParam', 'max_tokens')}"></label>
    <label>Timeout (s) <input name="timeoutSeconds" value="${model.get('timeoutSeconds', 240)}"></label>
  </div>
  <label class="inline"><input type="checkbox" name="supportsTemperature" ${'checked' if model.get('supportsTemperature', 1) else ''}> accepts a temperature</label>
  <label>Extra request fields (JSON) <input name="extraBody" value="${model.get('extraBody', '') | h}"></label>
  <div><button class="primary">${submit}</button></div>
</form>
</%def>

<div class="card">
  <h3>Defaults</h3>
  <form class="row" method="post" action="/defaults">
    % for name, text in (("defaultSheepModel", "Being"), ("defaultVisitorModel", "Visitors"), ("defaultEmbedModel", "Embedder")):
    <label>${text} <select name="${name}"><option value=""></option>
      % for model in models:
      <option value="${model['id']}" ${'selected' if str(model['id']) == defaults[name] else ''}>${model['label']}</option>
      % endfor
    </select></label>
    % endfor
    <div><button>Save defaults</button></div>
  </form>
</div>

% for model in models:
<details class="card"><summary><strong>${model['label']}</strong> <span class="dim">· ${model['kind']} · ${model['model']}</span></summary>
  ${modelForm(model, "/models/%d" % model['id'], "Save")}
  <form method="post" action="/models/${model['id']}/delete"><button class="danger">Delete</button></form>
</details>
% endfor

<div class="card"><h3>Add a model</h3>${modelForm({}, "/models", "Add")}</div>
