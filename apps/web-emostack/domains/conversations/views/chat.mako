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
    <details class="uwaga-panel" open><summary>here and now <small class="dim">(the situation of this moment)</small></summary>
      <ul id="hereAndNow" class="uwaga-list"></ul></details>
    <details class="uwaga-panel" open><summary>state <small id="stateCount" class="dim"></small> <small class="dim">(what it feels now)</small></summary>
      <ul id="state" class="stan-list"></ul></details>
    <details class="uwaga-panel" open><summary>accessibility slot <small class="dim">(what it holds in mind of its own writing)</small></summary>
      <ul id="held" class="stan-list"></ul></details>
    <details class="uwaga-panel" open><summary>conversation summary</summary>
      <ul id="summary" class="uwaga-list"></ul></details>
    <details class="uwaga-panel" open><summary>applicable dispositions <small id="dispositionCount" class="dim"></small> <small class="dim">(the learned rules applied to the last reply)</small></summary>
      <ul id="dispositions" class="uwaga-list"></ul></details>
    <details class="uwaga-panel" open><summary>focus <small id="focusCount" class="dim"></small> <small class="dim">(this conversation, and what surfaced meanwhile)</small></summary>
      <ul id="focus" class="uwaga-list"></ul></details>
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
