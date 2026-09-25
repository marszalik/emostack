<%inherit file="base.mako"/>
<%
  import datetime
  when = lambda ts: datetime.datetime.fromtimestamp(ts).strftime('%d %b %Y %H:%M')
  levels = {0: 'no access', 1: 'guest', 2: 'friend', 3: 'administrator'}
%>
<section class="hero"><h1>People</h1>
<p class="lede">Who may come in. A guest talks to their own sheep; a friend also sees the being's inner life; an administrator sees everything and talks on the server's model.</p></section>
<table class="plain">
  <tr><th>email</th><th>level</th><th></th></tr>
  % for email in administrators:
  <tr><td>${email | h}</td><td>administrator (from the settings)</td><td></td></tr>
  % endfor
  % for person in people:
  <tr><td>${person['email'] | h}</td><td>${{1: 'guest', 2: 'friend', 3: 'administrator'}[person['level']]}</td>
      <td><form method="post" action="/people/delete"><input type="hidden" name="email" value="${person['email'] | h}"><button class="ghost">remove</button></form></td></tr>
  % endfor
</table>
<h2 class="section-title">Everyone who has signed in</h2>
<p class="dim">A person's store is made on their first visit. Most recently active first.</p>
<table class="plain">
  <tr><th>email</th><th>level</th><th>first visit</th><th>last activity</th><th>sheep</th><th>own model</th></tr>
  % for person in everyone:
  <tr><td>${person['email'] | h}</td><td>${levels.get(person['level'], person['level'])}</td>
      <td>${when(person['firstVisit'])}</td><td>${when(person['lastActivity'])}</td>
      <td>${person['beings']}</td><td>${'yes' if person['ownModel'] else 'no'}</td></tr>
  % endfor
  % if not everyone:
  <tr><td colspan="6" class="dim">Nobody but the administrators yet.</td></tr>
  % endif
</table>

<h2 class="section-title">Give a role</h2>
<form method="post" action="/people" class="inline-form">
  <input name="email" placeholder="email" required>
  <select name="level"><option value="1">guest</option><option value="2">friend</option><option value="3">administrator</option></select>
  <button>save</button>
</form>
