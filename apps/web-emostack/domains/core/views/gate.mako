<%inherit file="base.mako"/>
<section class="gate" style="max-width:560px;margin:48px auto;text-align:center">
% if not user:
  <h1>EmoStack</h1>
  <p>This page is for signed-in people with access.</p>
  % if signInPath:
  <p><a class="gbtn" href="${signInPath}">sign in</a></p>
  % endif
% else:
  <h1>No access</h1>
  <p>The account <b>${user['email'] | h}</b> is signed in but has no access yet. Ask the administrator for a role.</p>
  <p><a class="ghost" href="/auth/logout">sign out</a></p>
% endif
</section>
