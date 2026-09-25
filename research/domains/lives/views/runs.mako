<%inherit file="base.mako"/>
<h1>Runs</h1>
<p class="lede">Every life the panel has run, newest first. A run belongs to an experiment or stands alone.</p>
<div class="card tableWrap"><table>
  <tr><th>Run</th><th>Scenario</th><th>Arm</th><th>Experiment</th><th>Status</th></tr>
  % for run in runs:
  <tr><td><a href="/runs/${run['id']}">#${run['id']}</a></td>
      <td>${scenarios.get(run['scenarioId'], {}).get('name', '(deleted)')}</td>
      <td>${run['armLabel'] + ' · ' if run['armLabel'] else ''}${run['arm']}${' · repeat %d' % (run['iteration'] + 1) if run['experimentId'] else ''}</td>
      <td>${'<a href="/experiments/%d">#%d</a>' % (run['experimentId'], run['experimentId']) if run['experimentId'] else ''}</td>
      <td><span class="pill ${run['status']}">${run['status']}</span></td></tr>
  % endfor
</table></div>
