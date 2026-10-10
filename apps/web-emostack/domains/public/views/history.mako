<%inherit file="base.mako"/>
<section class="hero room-hero">
  <h1>Earlier with ${being | h}</h1>
  <p class="lede">Everything said in ${being | h}'s room, day by day: who came, what they said, what ${being | h} answered, and what it thought about afterwards. <a href="/public">Back to the room, where ${being | h} is now.</a></p>
</section>
% if not days:
<p class="dim">Nothing has happened in the room yet.</p>
% else:
<nav class="history-days">
  % for d in days:
  <a href="/public/history?day=${d['day']}" class="${'active' if d['day'] == chosen else ''}">${d['day']} <small class="dim">${d['visitors']} visitor${'' if d['visitors'] == 1 else 's'}, ${d['messages']} message${'' if d['messages'] == 1 else 's'}</small></a>
  % endfor
</nav>
<div class="chat-stream history-stream">
  % for e in entries:
    % if e['role'] in ('arrival', 'departure'):
  <div class="msg sys">${e['who'] | h} ${'comes in' if e['role'] == 'arrival' else 'leaves'} · ${e['clock']}</div>
    % elif e['role'] == 'silence':
  <div class="msg silence"><em>${being | h} stays silent…</em></div>
    % elif e['role'] == 'thought':
  <div class="msg introspect"><div class="who">💭 ${being | h} thinks · ${e['clock']}</div><div class="text">${e['text'] | h}</div></div>
    % elif e['role'] == 'person':
  <div class="msg you"><div class="who">${e['who'] | h} <small class="dim">${e['clock']}</small></div><div class="text">${e['text'] | h}</div></div>
    % elif e['role'] == 'being':
  <div class="msg being"><div class="who">${being | h} <small class="dim">${e['clock']}</small></div><div class="text">${e['text'] | h}</div></div>
    % endif
  % endfor
</div>
% endif
