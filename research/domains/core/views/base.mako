<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title} · EmoStack research panel</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;1,500&family=Inter:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/core/core.css">
<%block name="head"/>
</head>
<body>
<header>
  <a class="brand" href="/"><img src="/static/core/logo.png" alt=""><span>EmoStack · research</span></a>
  <nav>
    <a href="/" class="${'active' if section == 'scenarios' else ''}">Scenarios</a>
    <a href="/experiments" class="${'active' if section == 'experiments' else ''}">Experiments</a>
    <a href="/runs" class="${'active' if section == 'runs' else ''}">Runs</a>
    <a href="/judges" class="${'active' if section == 'judges' else ''}">Judges</a>
    <a href="/models" class="${'active' if section == 'models' else ''}">Models</a>
  </nav>
</header>
<main>
${next.body()}
</main>
<script src="/static/core/core.js"></script>
<%block name="scripts"/>
</body>
</html>
