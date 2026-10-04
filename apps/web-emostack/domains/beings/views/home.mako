<%inherit file="base.mako"/>
<section class="hero">
% if level >= 3:
  <h1>Choose a sheep</h1>
  <p class="lede">Each has its own temperament. The same words meet a different state and a different history.</p>
% else:
  <h1>Talk to a sheep</h1>
  <p class="lede">A sheep is a being over a frozen language model: it feels what happens to it, writes about itself in the quiet, and learns how it meets people. It starts from nothing and becomes someone over days, not minutes. What it says comes from its own records, never from a script.</p>
  <p class="lede">Three things to know. <b>Your key, your cost:</b> every call the sheep makes runs on the model and key you set under <a href="/me/model">my model</a>; nothing is billed to this server. <b>Your sheep are yours:</b> nobody else can talk to them or see them. <b>It is kept:</b> what you say and what the sheep feels is kept in your own store on this server, so that you and the sheep can return to it; it is not read by anyone else and not used for anything else. This is a research instrument, not a product or a companion.</p>
  <p class="lede">Two ways in. <b>A sheep that has lived</b> gives you your own copy of a being with a history, so that the first conversation already meets someone. <b>A new sheep</b> starts from an empty memory; introduce yourself, say something that matters, and come back tomorrow.</p>
% endif
</section>

% if anonymous:
<div class="signin-overlay" id="signinOverlay" role="dialog" aria-modal="true" aria-labelledby="signinTitle">
  <div class="signin-card">
    <h2 id="signinTitle">Free. Sign in only so that your sheep stays yours.</h2>
    <p>The site learns your e-mail and nothing else; you talk on your own model key, and nothing is billed here. You will see what the sheep says and, beside it, what it feels, what came to its mind and what it has learned.</p>
    <a class="signin-google" href="${signInPath or '/'}">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
      </svg>
      Continue with Google
    </a>
    <p class="dim small">A research instrument, not a product. <a href="https://emostack.com/article/paper-full-text">The paper</a> says how it is built.</p>
  </div>
</div>
% endif

% if needsModel:
<section class="notice-box">
  <p><b>Before you start a conversation, set your model.</b> The sheep talk on your own API key
     (Anthropic, OpenAI, Google or another OpenAI-compatible endpoint); nothing is billed to this server.</p>
  <p><a class="gbtn" href="/me/model">set my model →</a></p>
</section>
% endif

% if snapshots:
<h2 class="section-title">Sheep that have lived — take your own copy</h2>
<div class="being-grid">
% for snapshot in snapshots:
  <div class="being-card">
    <header class="card-header"><h2>${snapshot['name'] | h}</h2></header>
    <div class="tagline">${snapshot.get('tagline', '') | h}</div>
    <p class="dim small">${snapshot.get('description', '') | h}</p>
    <div class="card-actions"><button class="cta copy-button" data-slug="${snapshot['slug'] | h}">Take a copy of ${snapshot['name'] | h}</button></div>
  </div>
% endfor
</div>
% if not anonymous:
<h2 class="section-title">Your sheep</h2>
% endif
% endif

<div class="being-grid">
% for being in beings:
  <div class="being-card" data-being-id="${being['id']}">
    <header class="card-header">
      <h2>${being['name'] | h}</h2>
      <span class="emo-count" title="${being['records']} records">📓 ${being['records']}</span>
      <button class="awake-badge ${'is-awake' if being['awake'] else 'is-asleep'}" data-being-id="${being['id']}"
              data-awake="${'1' if being['awake'] else '0'}" title="wake / put to sleep">${'🟢 awake' if being['awake'] else '😴 asleep'}</button>
    </header>
    <div class="card-mood">
      % if being['mood']:
      <span class="vbadge ${'pos' if being['mood']['valence'] >= 0 else 'neg'}">${'{:+.2f}'.format(being['mood']['valence'])}</span>
      <span class="ibar"><i style="width:${int(being['mood']['intensity'] * 100)}%"></i></span>
      <span class="mood-text">${being['mood']['feeling'] | h}</span>
      % else:
      <span class="dim mood-text">calm — nothing felt</span>
      % endif
    </div>
    <div class="active-row dim">Talking now: ${', '.join(being['talking']) or 'nobody'}</div>
    <div class="enter-inline" hidden><input class="enter-name" placeholder="your name" autocomplete="off"></div>
    <div class="card-actions">
      <button class="cta start-button" data-being-id="${being['id']}">Talk</button>
      <a class="ghost icon-btn" href="/beings/${being['id']}" title="what it holds">📓</a>
      <button class="ghost icon-btn delete-button" data-being-id="${being['id']}" title="delete this sheep and its memory">🗑</button>
    </div>
  </div>
% endfor
  <div class="being-card create-card">
    <h2>+ a new sheep</h2>
    <div class="tagline">starts from an empty memory${'' if level >= 3 else ' (up to %d sheep per person)' % most}</div>
    <form id="createForm">
      <label><span>name</span><input name="name" required placeholder="e.g. Maya"></label>
      % if level >= 3:
      <label><span>valence bias</span><input type="number" name="valenceBias" min="-1" max="1" step="0.05" value="0"></label>
      <label><span>intensity amplification</span><input type="number" name="intensityAmplification" min="0.1" max="3" step="0.05" value="1"></label>
      <label><span>avoidance weight</span><input type="number" name="avoidanceWeight" min="1" max="5" step="0.1" value="2"></label>
      % endif
      <button type="submit">create</button>
    </form>
  </div>
</div>

<script>
let starting = false;
async function start(beingId, name) {
  if (starting) return;
  starting = true;
  const body = new FormData(); body.append('beingId', beingId); body.append('name', name);
  const response = await fetch('/conversations', {method: 'POST', body});
  if (response.status === 409) { window.location = '/me/model?reason=needed'; return; }
  if (!response.ok) { alert(await response.text()); starting = false; return; }
  window.location = '/conversations/' + (await response.json()).id;
}
document.querySelectorAll('.start-button').forEach(button => {
  const card = button.closest('.being-card');
  const inline = card.querySelector('.enter-inline');
  const input = card.querySelector('.enter-name');
  button.addEventListener('click', () => {
    if (inline.hidden) { inline.hidden = false; input.focus(); button.textContent = 'Enter →'; return; }
    if (input.value.trim()) start(button.dataset.beingId, input.value.trim()); else input.focus();
  });
  input.addEventListener('keydown', e => { if (e.key === 'Enter' && input.value.trim()) start(button.dataset.beingId, input.value.trim()); });
});
document.querySelectorAll('.awake-badge').forEach(badge => badge.addEventListener('click', async () => {
  const response = await fetch('/beings/' + badge.dataset.beingId + '/awake/' + (badge.dataset.awake === '1' ? 0 : 1), {method: 'POST'});
  if (!response.ok) return;
  const awake = (await response.json()).awake;
  badge.dataset.awake = awake ? '1' : '0';
  badge.className = 'awake-badge ' + (awake ? 'is-awake' : 'is-asleep');
  badge.textContent = awake ? '🟢 awake' : '😴 asleep';
}));
document.querySelectorAll('.delete-button').forEach(button => button.addEventListener('click', async () => {
  if (!confirm('Delete this sheep and everything it remembers?')) return;
  const response = await fetch('/beings/' + button.dataset.beingId + '/delete', {method: 'POST'});
  if (!response.ok) { alert(await response.text()); return; }
  location.reload();
}));
const anonymous = ${'true' if anonymous else 'false'};
const signInPath = ${repr(signInPath or '/') | n};
function askToSignIn() {
  const panel = document.getElementById('signinOverlay');
  if (panel) { panel.classList.add('is-nudged'); setTimeout(() => panel.classList.remove('is-nudged'), 900); }
  else window.location = signInPath;
}
document.querySelectorAll('.copy-button').forEach(button => button.addEventListener('click', async () => {
  if (anonymous) { askToSignIn(); return; }
  button.disabled = true;
  const response = await fetch('/beings/copy/' + button.dataset.slug, {method: 'POST'});
  if (!response.ok) { alert(await response.text()); button.disabled = false; return; }
  location.reload();
}));
document.getElementById('createForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  if (anonymous) { askToSignIn(); return; }
  const response = await fetch('/beings', {method: 'POST', body: new FormData(event.target)});
  if (!response.ok) { alert(await response.text()); return; }
  location.reload();
});
if (!anonymous) setInterval(async () => {
  const response = await fetch('/beings');
  if (!response.ok) return;
  for (const being of await response.json()) {
    const card = document.querySelector('.being-card[data-being-id="' + being.id + '"]');
    if (card) card.querySelector('.active-row').textContent = 'Talking now: ' + (being.talking.join(', ') || 'nobody');
  }
}, 8000);
</script>
