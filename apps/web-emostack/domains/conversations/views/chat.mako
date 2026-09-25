<%inherit file="base.mako"/>
<%
  import json
  inner = level >= 2
%>
<section class="session-bar">
  <div><strong>${live.beingName | h}</strong> <span class="dim">↔</span> <strong>${live.person | h}</strong>
    <button type="button" id="thinkButton" class="being-btn intro-btn" title="the sheep stops to think, whatever you write">💭 think</button></div>
  <a href="/" class="ghost" id="leaveLink">← leave</a>
</section>

<div class="${'split' if inner else ''}">
  <div class="pane chat-pane">
    <div id="chat" class="chat-stream"></div>
    <form id="turnForm" class="input-row">
      <input id="words" name="words" autocomplete="off" placeholder="write something…" required>
      <button type="submit">send</button>
    </form>
  </div>
  % if inner:
  <div class="pane trace-pane">
    <div class="state-panel"><h3>held in mind <small class="dim">(its own thoughts, apart from what it feels)</small></h3>
      <ul id="held" class="stan-list"><li class="dim">…</li></ul></div>
    <div class="state-panel"><h3>state <small class="dim">(what it feels now)</small></h3>
      <div id="others" class="stan-active" hidden></div>
      <ul id="state" class="stan-list"><li class="dim">…</li></ul></div>
    <details class="uwaga-panel" open><summary>came to mind <small id="associationCount" class="dim"></small></summary>
      <ul id="associations" class="uwaga-list"></ul></details>
    <details class="uwaga-panel"><summary>focus <small id="focusCount" class="dim"></small></summary>
      <ul id="focus" class="uwaga-list"></ul></details>
    <details class="uwaga-panel"><summary>learned <small id="dispositionCount" class="dim"></small></summary>
      <ul id="dispositions" class="uwaga-list"></ul></details>
  </div>
  % endif
</div>

<div id="callsModal" class="prompt-modal" hidden>
  <div class="pm-backdrop"></div>
  <div class="pm-panel"><div class="pm-head"><span class="pm-title">the calls behind this message</span>
    <button type="button" class="pm-close" id="callsClose">×</button></div>
    <div id="callsBody" class="pm-body"></div></div>
</div>

<script>
const conversation = ${json.dumps({"id": live.id, "being": live.beingName, "messages": live.messages, "inner": inner}) | n};
</script>
<script src="/static/conversations/chat.js"></script>
