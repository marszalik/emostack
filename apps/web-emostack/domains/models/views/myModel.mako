<%inherit file="base.mako"/>
<%
  import json
  current = saved or {}
  currentProvider = current.get('provider', 'anthropic')
  routes = current.get('routes', {})
%>
<section class="hero">
  <h1>My model</h1>
  <p class="lede">The sheep you talk to think on your own key. Choose a provider, paste the key, save.
     The key stays on this server, readable only by the application, and is sent nowhere except to that provider.</p>
</section>

% if reason == 'needed':
<section class="notice-box"><p><b>To start a conversation, set your model first.</b></p></section>
% endif

<form id="modelForm" class="me-model">
  <fieldset>
    <label>provider
      <select name="provider" id="provider" data-scope="">
      % for provider in providers:
        <option value="${provider['name']}" ${'selected' if provider['name'] == currentProvider else ''}>${provider['label']}</option>
      % endfor
      </select>
    </label>
    <label>API key
      <input name="apiKey" type="password" autocomplete="off"
             placeholder="${'saved: ' + current['keyMasked'] + ' — leave empty to keep it' if current else 'paste your key'}">
    </label>
    <label>model <small class="dim">(a cheap one is enough)</small>
      <input name="model" id="model" list="models" value="${current.get('model', '') | h}" autocomplete="off">
      <datalist id="models"></datalist>
    </label>
    <label class="customOnly" ${'hidden' if currentProvider != 'custom' else ''}>endpoint address (OpenAI-compatible)
      <input name="baseUrl" value="${current.get('baseUrl', '') if currentProvider == 'custom' else '' | h}" placeholder="https://…/v1">
    </label>
    <label class="customOnly" ${'hidden' if currentProvider != 'custom' else ''}>the endpoint's embedding model <small class="dim">(for the being's memory; keep it once chosen)</small>
      <input name="embedModel" value="${current.get('embedModel', '') | h}" placeholder="text-embedding-3-small">
    </label>
    <label class="customOnly" ${'hidden' if currentProvider != 'custom' else ''}>the JSON format the endpoint expects
      <select name="jsonMode">
        <option value="jsonObject" ${'selected' if current.get('jsonMode') == 'jsonObject' else ''}>jsonObject (OpenAI, LiteLLM, Gemini)</option>
        <option value="jsonSchema" ${'selected' if current.get('jsonMode') == 'jsonSchema' else ''}>jsonSchema (Anthropic)</option>
        <option value="none" ${'selected' if current.get('jsonMode') == 'none' else ''}>none (LM Studio and the like)</option>
      </select>
    </label>
  </fieldset>

  <details class="advanced" ${'open' if routes else ''}>
    <summary>advanced — another model for a single kind of call</summary>
    <p class="dim small">Every call the being makes has a kind. Leave a kind on "the model above", or give it another model:
      for example a stronger one for the reply, or a cheaper one for the association filter. A key may be left empty
      when the provider is the same as above.</p>
    % for purpose in purposes:
    <% route = routes.get(purpose.name, {}) %>
    <div class="route-row">
      <span class="route-label">${purpose.label}</span>
      <select name="route.${purpose.name}.provider" class="routeProvider">
        <option value="">the model above</option>
        % for provider in providers:
        <option value="${provider['name']}" ${'selected' if route.get('provider') == provider['name'] else ''}>${provider['label']}</option>
        % endfor
      </select>
      <input name="route.${purpose.name}.model" placeholder="model" value="${route.get('model', '') | h}">
      <input name="route.${purpose.name}.apiKey" type="password" placeholder="${'(kept)' if route else 'key, if another provider'}">
      <input name="route.${purpose.name}.baseUrl" placeholder="endpoint, for other" value="${route.get('baseUrl', '') if route.get('provider') == 'custom' else '' | h}">
    </div>
    % endfor
  </details>

  <div class="actions">
    <button type="submit">save</button>
    <button type="button" id="testButton" class="ghost">test the connection</button>
    % if current:
    <button type="button" id="deleteButton" class="ghost">delete my settings</button>
    % endif
    <span id="status" class="dim"></span>
  </div>
</form>

<section class="dim small" style="margin-top:24px">
  <p>Where to get a key: Anthropic — console.anthropic.com → API keys; OpenAI — platform.openai.com → API keys;
     Google — aistudio.google.com → Get API key. A turn of conversation reads several thousand tokens in a few calls,
     so a cheap model is enough. The sheep's memory vectors are made on your key where the provider serves embeddings
     (OpenAI, Google); for Anthropic, which has none, on this server's own small model.</p>
</section>

<script>
const providers = ${json.dumps({p['name']: p for p in providers}) | n};
const providerSelect = document.getElementById('provider');
function syncProvider() {
  const provider = providers[providerSelect.value] || {models: []};
  document.getElementById('models').innerHTML = provider.models.map(m => '<option value="' + m + '"></option>').join('');
  document.querySelectorAll('.customOnly').forEach(el => el.hidden = providerSelect.value !== 'custom');
  const model = document.getElementById('model');
  if (!model.value && provider.models.length) model.value = provider.models[0];
}
providerSelect.addEventListener('change', () => { document.getElementById('model').value = ''; syncProvider(); });
syncProvider();

async function send(path) {
  const status = document.getElementById('status');
  status.textContent = '…';
  const response = await fetch(path, {method: 'POST', body: new FormData(document.getElementById('modelForm'))});
  return response.json().catch(() => ({ok: false, error: 'HTTP ' + response.status}));
}
document.getElementById('testButton').addEventListener('click', async () => {
  const answer = await send('/me/model/test');
  document.getElementById('status').textContent = answer.ok ? '✓ works — ' + answer.message : '✗ ' + (answer.message || answer.error);
});
document.getElementById('modelForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  const answer = await send('/me/model');
  if (answer.ok) { window.location = '/'; return; }
  document.getElementById('status').textContent = '✗ ' + (answer.error || 'error');
});
const deleteButton = document.getElementById('deleteButton');
if (deleteButton) deleteButton.addEventListener('click', async () => {
  if (!confirm('Delete the saved key and model?')) return;
  await fetch('/me/model/delete', {method: 'POST'});
  window.location = '/me/model';
});
</script>
