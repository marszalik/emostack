<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#14171c">
<meta name="color-scheme" content="dark">
<title>EmoStack</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/core/app.css">
</head>
<body>
<header>
  <span class="brand"><a href="https://emostack.com" class="brand-logo" title="emostack.com"><img src="/static/core/logo.png" alt="EmoStack"></a><a href="/" class="brand-name">EmoStack</a></span>
  <nav>
    <a href="/" class="${'active' if section == 'home' else ''}">sheep</a>
    % if user:
    <a href="/me/model" class="${'active' if section == 'myModel' else ''}">my model</a>
    % endif
    % if level >= 3:
    <a href="/people" class="${'active' if section == 'people' else ''}">people</a>
    % endif
    <a href="https://emostack.com/code">code</a>
  </nav>
  <div class="auth-box">
    % if user and identity != 'local':
      % if user.get('picture'):
      <img class="auth-avatar" src="${user['picture'] | h}" alt="" referrerpolicy="no-referrer">
      % endif
      <span class="auth-email">${user['email'] | h}</span>
      % if signOutUrl:
      <a class="ghost" href="${signOutUrl}">sign out</a>
      % endif
    % elif not user and signInPath:
      <a class="ghost gbtn" href="${signInPath}">sign in</a>
    % endif
  </div>
</header>
<main>
${next.body()}
</main>
<footer>
  <small><a href="https://emostack.com">emostack.com</a> · <a href="https://emostack.com/article">the paper and its materials</a> · a research instrument, not a product</small>
</footer>
</body>
</html>
