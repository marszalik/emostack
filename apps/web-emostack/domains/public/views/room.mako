<%inherit file="base.mako"/>
<section class="hero room-hero">
  <h1>${being | h}</h1>
  <p class="lede">${being | h} is a sheep: a being over a frozen LLM model. It feels what happens to it, writes about itself in the quiet, and learns how it meets people. It started here from nothing and becomes someone over days. One visitor talks with it at a time; everyone else watches and waits their turn. It sleeps at night, like the computer it runs on.</p>
</section>

<div class="room-status" id="status"><span class="dim">…</span></div>

<div class="split room-split">
  <div class="pane chat-pane">
    <div id="chat" class="chat-stream"></div>
    <div id="seat" class="seat"></div>
  </div>
  <div class="pane trace-pane">
    <details class="uwaga-panel" open><summary>state <small id="stateCount" class="dim"></small> <small class="dim">(what it feels now)</small></summary>
      <ul id="state" class="stan-list"></ul></details>
    <details class="uwaga-panel" open><summary>accessibility slot <small class="dim">(what it holds in mind of its own writing)</small></summary>
      <ul id="held" class="stan-list"></ul></details>
    <details class="uwaga-panel" open><summary>conversation summary</summary>
      <ul id="summary" class="uwaga-list"></ul></details>
    <details class="uwaga-panel" open><summary>applicable dispositions <small id="dispositionCount" class="dim"></small> <small class="dim">(the learned rules applied to the last reply)</small></summary>
      <ul id="dispositions" class="uwaga-list"></ul></details>
    <details class="uwaga-panel"><summary>focus <small id="focusCount" class="dim"></small> <small class="dim">(this conversation, and what surfaced meanwhile)</small></summary>
      <ul id="focus" class="uwaga-list"></ul></details>
  </div>
</div>

<p class="small dim room-notice">What is said here becomes part of ${being | h}'s memory and is shown to everyone in the room, now and later. Do not write anything personal, yours or anyone else's. A message that should not be here has a <b>report</b> link; the reports are read. ${being | h} is a research instrument, not a product: it has no knowledge of the world beyond what it lives through here, and its answers are its own.</p>

% if level >= 3:
<div class="room-admin">
  <button class="ghost" data-admin="sleep">put ${being | h} to sleep</button>
  <button class="ghost" data-admin="wake">wake ${being | h}</button>
  <button class="ghost" data-admin="clear">clear the room</button>
  <a class="ghost" href="/public/admin/reports">reports</a>
</div>
% endif

<script>
const room = {being: ${repr(being) | n}};
</script>
<script src="/static/public/room.js?v=${staticVersion}"></script>
