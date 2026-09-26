<%inherit file="base.mako"/>
<%
  import json
  byRepeat = {}
  for run in runs:
      byRepeat.setdefault(run['iteration'], {})[run['armLabel']] = run
%>
<h1>Experiment #${experiment['id']} ${experiment['name']}</h1>
<p class="lede">${scenario['name']} · <span class="pill ${experiment['status']}">${experiment['status']}</span> · ${experiment['note']}</p>
<div class="row">
  % if experiment['status'] in ('running', 'queued'):
  <div><button onclick="postAndReload('/experiments/${experiment['id']}/stop', 'Stop the experiment?')">Stop</button></div>
  % else:
  <form method="post" action="/experiments/${experiment['id']}/delete" onsubmit="return confirm('Delete the experiment and its runs?')"><button class="danger">Delete</button></form>
  % endif
</div>

<h2>Arms</h2>
<div class="card tableWrap"><table>
  <tr><th>Arm</th><th>What</th></tr>
  % for arm in experiment['arms']:
  <tr><td>${arm['label']}</td><td>${arm['arm']}${' · ' + json.dumps(arm['parameters']) if arm['parameters'] else ''}</td></tr>
  % endfor
</table></div>

<h2>Runs</h2>
<div class="card tableWrap"><table>
  <tr><th>Repeat</th>
  % for arm in experiment['arms']:
    <th>${arm['label']}</th>
  % endfor
  </tr>
  % for repeat in sorted(byRepeat):
  <tr><td>${repeat + 1}</td>
    % for arm in experiment['arms']:
    <% run = byRepeat[repeat].get(arm['label']) %>
    <td>${'<a href="/runs/%d">#%d</a> <span class="pill %s">%s</span>' % (run['id'], run['id'], run['status'], run['status']) if run else ''}</td>
    % endfor
  </tr>
  % endfor
</table></div>

<h2>Blind coding</h2>
% if codings:
<form class="card stack" method="post" action="/experiments/${experiment['id']}/code">
  <div class="row">
    % for coding in codings:
    <label class="inline"><input type="checkbox" name="codingId" value="${coding['id']}" checked> ${coding['name']}</label>
    % endfor
  </div>
  <div class="row"><label>Coder <select name="coderModelId">
    % for model in coders:
    <option value="${model['id']}">${model['label']}</option>
    % endfor
  </select></label><div><button class="primary">Code the finished runs</button></div></div>
</form>
% else:
<p class="dim">The scenario has no blind codings.</p>
% endif
% for result in codingResults:
<div class="card">
  <h3>${result['coding']} <span class="dim">· ${result['coder']} · counted: ${result['counted']}</span></h3>
  <p class="mono">${' · '.join('%s: %s' % (arm, ', '.join('%s %d' % (label, n) for label, n in sorted(labels.items()))) for arm, labels in sorted(result['arms'].items()))}</p>
  % for pair in result['pairs']:
  <p>${pair['a']} ${pair['countA']} vs ${pair['b']} ${pair['countB']} · Fisher p = ${'%.4f' % pair['p'] if pair['p'] is not None else '—'}</p>
  % endfor
</div>
% endfor

<h2>Judging</h2>
<form class="card row" method="post" action="/experiments/${experiment['id']}/judge">
  % for judge in judges:
  <label class="inline"><input type="checkbox" name="judgeId" value="${judge['id']}"> ${judge['name']}</label>
  % endfor
  <div><button class="primary">Judge the finished runs</button></div>
</form>

% for result in results:
<div class="card">
  <h3>${result['criterion']} <span class="dim">· ${result['judge']}</span></h3>
  <p class="mono">${' · '.join('%s: %s' % (arm, scores) for arm, scores in sorted(result['perArm'].items()))}</p>
  <div class="tableWrap"><table>
    <tr><th>Pair</th><th>Means</th><th>δ</th><th>p (Mann–Whitney)</th><th>p (paired)</th><th>Reading</th></tr>
    % for row in result['comparisons']:
    <tr><td>${row['a']} vs ${row['b']}</td><td>${row['meanA']} / ${row['meanB']}</td><td>${row['delta']}</td>
        <td>${row['pUnpaired']}</td><td>${row['pPaired']}</td><td>${row['verdict']}</td></tr>
    % endfor
  </table></div>
</div>
% endfor

<h3>Log</h3>
<div class="card log" id="log"></div>
<%block name="scripts">
<script>
followStream("/experiments/${experiment['id']}/stream", (event) => {
  const line = document.createElement("div");
  line.textContent = [event.kind, event.text || "", event.runId ? "run #" + event.runId : "", event.arm || "",
                      event.criterion || "", event.judge || ""].filter(Boolean).join(" · ");
  const log = document.getElementById("log");
  log.appendChild(line);
  log.scrollTop = log.scrollHeight;
  if (event.kind === "done" || event.kind === "runDone" || event.kind === "judgedAll" || event.kind === "codedAll") setTimeout(() => location.reload(), 1500);
});
</script>
</%block>
