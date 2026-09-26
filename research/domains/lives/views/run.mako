<%inherit file="base.mako"/>
<%
  import json
  labels = {"visitor": None, "sheep": run['settings'].get('scenario', {}).get('beingName', 'being'), "thought": "thought", "event": "", "seed": "given at birth"}
%>
<h1>Run #${run['id']}</h1>
<p class="lede">${run['arm']}${' · arm ' + run['armLabel'] if run['armLabel'] else ''} · <span class="pill ${run['status']}" id="status">${run['status']}</span>
% if run['experimentId']:
 · <a href="/experiments/${run['experimentId']}">experiment #${run['experimentId']}</a>
% endif
</p>
<div class="row">
  % if run['status'] in ('running', 'queued'):
  <div><button onclick="postAndReload('/runs/${run['id']}/stop')">Stop</button></div>
  % else:
  <form method="post" action="/runs/${run['id']}/delete" onsubmit="return confirm('Delete this run?')"><button class="danger">Delete</button></form>
  % endif
</div>
% if run['error']:
<pre class="card mono bad">${run['error'] | h}</pre>
% endif

<div class="card transcript" id="transcript">
% for turn in turns:
  <div class="turn ${turn['speaker']}">
    <div class="who">day ${turn['dayIndex'] + 1} · ${turn['person'] if turn['speaker'] == 'visitor' else (labels.get(turn['speaker']) or turn['speaker'])}
      % if turn['valence'] is not None:
      · <span class="mono">${'%+.2f' % turn['valence']} / ${'%.2f' % (turn['intensity'] or 0)}</span> ${turn['feeling'][:120] | h}
      % endif
    </div>
    <div class="text">${turn['text'] | h}</div>
    % for call in turn['calls']:
    <details class="call"><summary>${call.get('purpose') or 'call'} · temperature ${call.get('temperature')}</summary>
      <pre><b>SYSTEM</b>
${call.get('system', '') | h}

<b>USER</b>
${call.get('user', '') | h}

<b>ANSWER</b>
${call.get('answer', '') | h}</pre>
    </details>
    % endfor
  </div>
% endfor
</div>

<%block name="scripts">
% if run['status'] in ('running', 'queued'):
<script>
const seen = ${len(turns)};
let count = 0;
followStream("/runs/${run['id']}/stream", (event) => {
  if (event.kind === "turn") {
    count += 1;
    if (count <= seen) return;
    const box = document.createElement("div");
    box.className = "turn " + event.speaker;
    box.innerHTML = '<div class="who">day ' + (event.day + 1) + ' · ' + escapeHtml(event.speaker === "visitor" ? event.person : event.speaker) +
      '</div><div class="text">' + escapeHtml(event.text) + '</div>';
    document.getElementById("transcript").appendChild(box);
  } else if (event.kind === "done" || event.kind === "error") {
    setTimeout(() => location.reload(), 800);
  }
});
</script>
% endif
</%block>
