// A conversation with a being: messages, the live stream of its replies, and its inner life.
const chat = document.getElementById("chat");
let busy = false;
let over = false;
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

// An entry opens in full on a click and stays open across refreshes.
const expanded = new Set();
document.querySelector(".trace-pane")?.addEventListener("click", (event) => {
  const entry = event.target.closest(".etext[data-key]");
  if (!entry) return;
  entry.classList.toggle("expanded");
  if (entry.classList.contains("expanded")) expanded.add(entry.dataset.key); else expanded.delete(entry.dataset.key);
});

function entryText(key, html) {
  return '<span class="etext' + (expanded.has(key) ? " expanded" : "") + '" data-key="' +
    text(key).replace(/"/g, "&quot;") + '">' + html + "</span>";
}

function row(item, tag = "") {
  const valence = (item.valence >= 0 ? "+" : "") + item.valence.toFixed(2);
  return '<li class="stan-item"><span class="vbadge ' + (item.valence >= 0 ? "pos" : "neg") + '">' + valence +
    '</span><span class="ibar"><i style="width:' + Math.round((item.felt || 0) * 100) + '%"></i></span>' + entryText(item.at + "|" + item.feeling, text(item.feeling) +
    (item.event ? " — " + text(item.event) : "") + (item.conclusion ? " → " + text(item.conclusion) : "")) +
    (tag ? '<span class="eago dim">' + text(tag) + "</span>" : "") + "</li>";
}
async function refresh() {
  if (!conversation.inner) return;
  const response = await fetch("/conversations/" + conversation.id + "/state");
  if (response.status === 404 && !over) {
    over = true;
    show({role: "failed"});
    chat.lastChild.textContent = "This conversation is over. Go back and start a new one.";
  }
  if (!response.ok) return;
  const state = await response.json();
  const here = [["when", new Date(state.now * 1000).toLocaleString()], ["talking with", state.person],
    ["also present", state.others.join(", ") || "nobody"]];
  document.getElementById("hereAndNow").innerHTML = here.map(([name, value]) =>
    '<li class="stan-item"><span class="eago dim">' + name + "</span>" + entryText("here|" + name, text(value)) + "</li>").join("") +
    '<li class="stan-item"><span class="eago dim">senses</span><span class="etext expanded">' +
    (state.senses.length ? state.senses.map(text).join("<br>") : '<span class="dim">after the first reply</span>') + "</span></li>";
  document.getElementById("state").innerHTML = state.state.length ? state.state.map(item => row(item, item.evoked ? "association" : "")).join("") : '<li class="dim">calm — nothing felt</li>';
  document.getElementById("stateCount").textContent = "(" + state.state.length + ")";
  document.getElementById("focus").innerHTML = state.focus.map(item => row(item, item.evoked ? "association" : "")).join("") || '<li class="dim">nothing yet</li>';
  document.getElementById("focusCount").textContent = "(" + state.focus.length + ")";
  document.getElementById("summary").innerHTML = state.summary
    ? '<li class="stan-item">' + entryText("summary", text(state.summary)) + "</li>" : '<li class="dim">not yet — it is written as the conversation grows</li>';
  document.getElementById("held").innerHTML = state.held.length
    ? state.held.map(h => '<li class="stan-item">' + entryText(h.text, text(h.text)) + "</li>").join("")
    : '<li class="dim">nothing yet</li>';
  document.getElementById("dispositions").innerHTML = state.dispositions.map(d =>
    '<li class="stan-item"><span class="vbadge ' + (d.weight >= 0 ? "pos" : "neg") + '">' + (d.weight >= 0 ? "+" : "") +
    d.weight.toFixed(2) + '</span>' + entryText(d.rule, text(d.rule)) + "</li>").join("") || '<li class="dim">none applied to the last reply</li>';
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
