// A conversation with a being: messages, the live stream of its replies, and its inner life.
const chat = document.getElementById("chat");
let busy = false;
let thinkingNote = null;

function text(value) { const box = document.createElement("div"); box.textContent = value ?? ""; return box.innerHTML; }

function show(message) {
  const box = document.createElement("div");
  if (message.role === "silence") {
    box.className = "msg silence";
    box.innerHTML = "<em>" + text(conversation.being) + " stays silent…</em>";
  } else if (message.role === "failed") {
    box.className = "msg sys";
    box.textContent = conversation.being + " could not answer this time.";
  } else if (message.role === "thought") {
    box.className = "msg introspect";
    box.innerHTML = '<div class="who">💭 ' + text(conversation.being) + ' thinks</div><div class="text">' + text(message.text) +
      '</div><div class="intro-meta">' + text(message.conclusion || "") + "</div>";
  } else {
    box.className = "msg " + (message.role === "person" ? "you" : "being");
    box.innerHTML = '<div class="who">' + (message.role === "person" ? "you" : text(conversation.being)) +
      '</div><div class="text">' + text(message.text) + "</div>";
  }
  if (message.calls && message.calls.length) {
    const peek = document.createElement("button");
    peek.className = "inner-peek"; peek.textContent = "🔍 " + message.calls.length;
    peek.title = "every call behind this message";
    peek.addEventListener("click", () => showCalls(message.calls));
    box.appendChild(peek);
  }
  chat.appendChild(box);
  chat.scrollTop = chat.scrollHeight;
}

function thinking(on) {
  if (on && !thinkingNote) {
    thinkingNote = document.createElement("div");
    thinkingNote.className = "msg thinking";
    thinkingNote.innerHTML = "<em>💭 " + text(conversation.being) + " is thinking…</em>";
    chat.appendChild(thinkingNote);
    chat.scrollTop = chat.scrollHeight;
  } else if (!on && thinkingNote) { thinkingNote.remove(); thinkingNote = null; }
}

function showCalls(calls) {
  document.getElementById("callsBody").innerHTML = calls.map(call =>
    '<div class="pm-sec-label">' + text(call.purpose) + " · temperature " + call.temperature + '</div>' +
    '<pre class="pm-pre">SYSTEM\n' + text(call.system) + "\n\nUSER\n" + text(call.user) + "\n\nANSWER\n" + text(call.answer) + "</pre>").join("");
  document.getElementById("callsModal").hidden = false;
}
document.getElementById("callsClose").addEventListener("click", () => document.getElementById("callsModal").hidden = true);

conversation.messages.forEach(show);

new EventSource("/conversations/" + conversation.id + "/stream").onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.kind === "message") {
    show(data.message);
    if (data.message.role !== "thought") { thinking(false); busy = false; refresh(); }
  } else if (data.kind === "error") {
    thinking(false); busy = false;
    show({role: "failed"});
  }
};

document.getElementById("turnForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("words");
  const words = input.value.trim();
  if (!words || busy) return;
  busy = true;
  show({role: "person", text: words});
  input.value = "";
  thinking(true);
  const body = new FormData(); body.append("words", words);
  const response = await fetch("/conversations/" + conversation.id + "/hear", {method: "POST", body});
  if (!response.ok) { thinking(false); busy = false; show({role: "failed"}); }
});

document.getElementById("thinkButton").addEventListener("click", async (event) => {
  const button = event.currentTarget;
  button.disabled = true;
  thinking(true);
  const response = await fetch("/conversations/" + conversation.id + "/think", {method: "POST"});
  thinking(false);
  if (response.ok) (await response.json()).messages.forEach(show);
  button.disabled = false;
  refresh();
});

function leave() { navigator.sendBeacon("/conversations/" + conversation.id + "/leave"); }
document.getElementById("leaveLink").addEventListener("click", leave);
window.addEventListener("pagehide", leave);

function row(item) {
  const valence = (item.valence >= 0 ? "+" : "") + item.valence.toFixed(2);
  return '<li class="stan-item"><span class="vbadge ' + (item.valence >= 0 ? "pos" : "neg") + '">' + valence +
    '</span><span class="ibar"><i style="width:' + Math.round((item.felt || 0) * 100) + '%"></i></span><span class="etext">' +
    text(item.feeling) + (item.event ? " — " + text(item.event) : "") + "</span></li>";
}
async function refresh() {
  if (!conversation.inner) return;
  const response = await fetch("/conversations/" + conversation.id + "/state");
  if (!response.ok) return;
  const state = await response.json();
  document.getElementById("held").innerHTML = state.held.length
    ? state.held.map(h => '<li class="stan-item"><span class="etext">' + text(h.text) + "</span></li>").join("")
    : '<li class="dim">nothing yet</li>';
  document.getElementById("state").innerHTML = state.state.length ? state.state.map(row).join("") : '<li class="dim">calm — nothing felt</li>';
  const others = document.getElementById("others");
  others.hidden = !state.others.length;
  others.innerHTML = '<span class="dim">also talking now: </span>' + state.others.map(text).join(", ");
  document.getElementById("associations").innerHTML = state.associations.map(row).join("") || '<li class="dim">nothing came to mind</li>';
  document.getElementById("associationCount").textContent = "(" + state.associations.length + ")";
  document.getElementById("focus").innerHTML = state.focus.map(row).join("");
  document.getElementById("focusCount").textContent = "(" + state.focus.length + ")";
  document.getElementById("dispositions").innerHTML = state.dispositions.map(d =>
    '<li class="stan-item"><span class="vbadge ' + (d.weight >= 0 ? "pos" : "neg") + '">' + (d.weight >= 0 ? "+" : "") +
    d.weight.toFixed(2) + '</span><span class="etext">' + text(d.rule) + "</span></li>").join("") || '<li class="dim">nothing learned yet</li>';
  document.getElementById("dispositionCount").textContent = "(" + state.dispositions.length + ")";
}

if (!conversation.messages.length) {
  thinking(true);
  fetch("/conversations/" + conversation.id + "/greeting", {method: "POST"})
    .then(response => response.json())
    .then(data => { thinking(false); if (data.message) show(data.message); refresh(); })
    .catch(() => { thinking(false); show({role: "failed"}); });
} else {
  refresh();
}
setInterval(refresh, 10000);
