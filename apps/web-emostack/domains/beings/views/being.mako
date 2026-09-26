<%inherit file="base.mako"/>
<%
  import datetime
  when = lambda ts: datetime.datetime.fromtimestamp(ts).strftime('%d %b %Y %H:%M')
%>
<section class="hero"><h1>${being.name | h}</h1>
<p class="lede">What ${being.name | h} holds: every record with the events under it, the thoughts it holds in mind, and what it has learned about meeting people.</p></section>

<h2 class="section-title">Accessibility slot</h2>
% if held:
<ul class="stan-list">
  % for statement in held:
  <li class="stan-item"><span class="etext">${statement | h}</span></li>
  % endfor
</ul>
% else:
<p class="dim">Nothing yet — a thought enters when the being writes it in reflection or brings it back to mind.</p>
% endif

<h2 class="section-title">Dispositions</h2>
% if dispositions:
<ul class="stan-list">
  % for disposition in dispositions:
  <li class="stan-item"><span class="vbadge ${'pos' if disposition['weight'] >= 0 else 'neg'}">${'{:+.2f}'.format(disposition['weight'])}</span>
    <span class="etext">${disposition['rule'] | h}</span><span class="dim">×${disposition['count']}</span></li>
  % endfor
</ul>
% else:
<p class="dim">Nothing yet — a conversation rarely teaches a rule.</p>
% endif

<h2 class="section-title">Hippocampus</h2>
% for record in records:
<div class="memory-record">
  <div><span class="vbadge ${'pos' if record['valence'] >= 0 else 'neg'}">${'{:+.2f}'.format(record['valence'])}</span>
    <span class="ibar"><i style="width:${int(record['intensity'] * 100)}%"></i></span>
    <span class="dim">${when(record['happenedAt'])} · ${record['kind']}${' · ' + record['person'] if record['person'] else ''}</span></div>
  % if record['text']:
  <div class="memory-text">${record['text'] | h}</div>
  % endif
  <div class="memory-feeling">${record['feeling'] | h}</div>
  % if record['conclusion']:
  <div class="dim">${record['conclusion'] | h}</div>
  % endif
  % for event in record['events']:
  <div class="memory-event">◦ ${event | h}</div>
  % endfor
</div>
% endfor
