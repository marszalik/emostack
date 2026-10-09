// The public room: who is talking with the being, the log everyone sees, the seat (a queue, the turn,
// or a letter while the being sleeps), and the being's inner life beside it.
const chat = document.getElementById("chat");
const seat = document.getElementById("seat");
const statusBox = document.getElementById("status");
let status = null;
let shownAt = new Set();
let lastLogKey = "";
let sending = false;

function text(value) { const box = document.createElement("div"); box.textContent = value ?? ""; return box.innerHTML; }
function when(at) { return new Date(at * 1000).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"}); }

function line(message) {
  const box = document.createElement("div");
  const who = message.who || "";
  if (message.role === "silence") {
    box.className = "msg silence";
    box.innerHTML = "<em>" + text(room.being) + " stays silent…</em>";
  } else if (message.role === "failed") {
    box.className = "msg sys";
    box.textContent = room.being + " could not answer this time.";
  } else if (message.role === "thought") {
    box.className = "msg introspect";
    box.innerHTML = '<div class="who">💭 ' + text(room.being) + ' thinks</div><div class="text">' + text(message.text) + "</div>";
  } else if (message.role === "arrival" || message.role === "departure") {
    box.className = "msg sys";
    box.textContent = who + (message.role === "arrival" ? " comes in" : " leaves") + " · " + when(message.at);
  } else if (message.role === "person") {
    box.className = "msg you";
    box.innerHTML = '<div class="who">' + text(who) + (message.letter ? " <small>(a letter left in the night)</small>" : "") +
      ' <small class="dim">' + when(message.at) + '</small></div><div class="text">' + text(message.text) + "</div>";
  } else {
    box.className = "msg being";
    box.innerHTML = '<div class="who">' + text(room.being) + ' <small class="dim">' + when(message.at) + "</small></div><div class="text">" + text(message.text) + "</div>";
  }
  if (message.role === "person" || message.role === "being") {
    const report = document.createElement("button");
    report.className = "report-link"; report.textContent = "report"; report.title = "this should not be here";
    report.addEventListener("click", async () => {
      const note = prompt("What is wrong with this message? (optional)") ;
      if (note === null) return;
      const body = new FormData(); body.append("about", (who || room.being) + ": " + (message.text || "")); body.append("note", note);
      await fetch("/public/report", {method: "POST", body});
      report.textContent = "reported"; report.disabled = true;
    });
    box.appendChild(report);
  }
  return box;
}

function renderLog(log) {
  const key = log.map(m => m.at + m.role).join("|");
  if (key === lastLogKey) return;
  lastLogKey = key;
  const atBottom = chat.scrollHeight - chat.scrollTop - chat.clientHeight < 60;
  chat.innerHTML = "";
  if (!log.length) {
    const box = document.createElement("div"); box.className = "msg sys";
    box.textContent = "Nothing has happened yet. " + room.being + " is waiting for its first visitor.";
    chat.appendChild(box);
  }
  log.forEach(message => chat.appendChild(line(message)));
  if (atBottom || true) chat.scrollTop = chat.scrollHeight;
}

function renderStatus(s, about) {
  let html = "";
  if (!s.awake) {
    const why = s.reason === "night" ? "It is night. " + room.being + " sleeps until " + s.until + "."
      : s.reason === "rest" ? room.being + " has been put to sleep for a while."
      : room.being + " is asleep: the computer it lives on is off or busy. It wakes when the computer comes back.";
    html = '<span class="badge asleep">😴 asleep</span> ' + text(why) + " You can leave it a letter; it answers when it wakes.";
  } else if (s.speaker) {
    html = '<span class="badge awake">🟢 awake</span> talking with <b>' + text(s.speaker) + "</b>" + (s.mail ? " (a letter from the night)" : "") +
      (s.waiting ? " · " + s.waiting + " waiting" : "");
  } else {
    html = '<span class="badge awake">🟢 awake</span> nobody is talking with ' + text(room.being) + " right now.";
  }
  if (about && about.records !== undefined) html += ' <span class="dim small">· ' + about.records + " records in memory</span>";
  statusBox.innerHTML = html;
}

function renderSeat(s) {
  const was = seat.dataset.mode;
  let mode;
  if (!s.awake) mode = "letter";
  else if (s.me === "speaker") mode = "turn";
  else if (s.me === "queue") mode = "queue";
  else if (s.visitsLeft <= 0) mode = "done";
  else mode = "join";
  if (mode === was) { updateSeat(s); return; }
  seat.dataset.mode = mode;
  if (mode === "join") {
    seat.innerHTML = '<form id="joinForm" class="input-row"><input id="joinName" name="name" autocomplete="off" maxlength="24" placeholder="your name" required>' +
      '<button type="submit">' + (s.speaker ? "wait for a turn" : "talk to " + text(room.being)) + "</button></form>" +
      '<div class="seat-note dim small">A visit is up to ' + s.turnsPerVisit + " messages; " + s.visitsLeft + " visit" + (s.visitsLeft === 1 ? "" : "s") + " left today.</div>";
    document.getElementById("joinForm").addEventListener("submit", async (event) => {
      event.preventDefault();
      const body = new FormData(event.target);
      const response = await fetch("/public/queue", {method: "POST", body});
      if (!response.ok) { alert((await response.json()).detail); return; }
      try { localStorage.setItem("roomName", body.get("name")); } catch (e) {}
      refresh();
    });
    try { const saved = localStorage.getItem("roomName"); if (saved) document.getElementById("joinName").value = saved; } catch (e) {}
  } else if (mode === "queue") {
    seat.innerHTML = '<div class="seat-note">You are <b>number ' + s.position + '</b> in the queue. Keep this page open; your turn comes when the visitor before you leaves.</div>' +
      '<div class="input-row"><button type="button" id="leaveQueue" class="ghost">leave the queue</button></div>';
    document.getElementById("leaveQueue").addEventListener("click", async () => { await fetch("/public/leave", {method: "POST"}); refresh(); });
  } else if (mode === "turn") {
    seat.innerHTML = '<form id="turnForm" class="input-row"><input id="words" name="words" autocomplete="off" maxlength="' + s.maxWords + '" placeholder="write something…" required>' +
      '<button type="submit">send</button><button type="button" id="leaveSeat" class="ghost">leave</button></form>' +
      '<div class="seat-note dim small" id="turnNote"></div>';
    document.getElementById("turnForm").addEventListener("submit", async (event) => {
      event.preventDefault();
      const input = document.getElementById("words");
      const words = input.value.trim();
      if (!words || sending) return;
      sending = true;
      const body = new FormData(); body.append("words", words);
      const response = await fetch("/public/say", {method: "POST", body});
      sending = false;
      if (!response.ok) { const detail = (await response.json()).detail; document.getElementById("turnNote").textContent = detail; return; }
      input.value = "";
      refresh();
    });
    document.getElementById("leaveSeat").addEventListener("click", async () => { await fetch("/public/leave", {method: "POST"}); refresh(); });
    document.getElementById("words").focus();
  } else if (mode === "done") {
    seat.innerHTML = '<div class="seat-note dim">That is all for today; ' + text(room.being) + " meets you again tomorrow. You can still watch.</div>";
  } else if (mode === "letter") {
    const mine = (s.letters || []);
    let letters = mine.map(l => '<div class="letter"><div class="who">you wrote' + (l.deliveredAt ? "" : " (not yet read)") + '</div><div class="text">' + text(l.words) + "</div>" +
      (l.deliveredAt ? '<div class="who">' + text(room.being) + ' answered</div><div class="text">' + (l.reply ? text(l.reply) : "<em>…with silence</em>") + "</div>" : "") + "</div>").join("");
    seat.innerHTML = letters + (s.lettersLeft > 0
      ? '<form id="mailForm" class="mail-form"><input name="name" autocomplete="off" maxlength="24" placeholder="your name" required>' +
        '<textarea name="words" maxlength="400" rows="3" placeholder="a letter for ' + text(room.being) + ' to read when it wakes…" required></textarea>' +
        '<button type="submit">leave the letter</button></form>'
      : '<div class="seat-note dim small">Your letter waits for the morning. Come back after ' + (s.until || "it wakes") + ".</div>");
    const form = document.getElementById("mailForm");
    if (form) {
      try { const saved = localStorage.getItem("roomName"); if (saved) form.name.value = saved; } catch (e) {}
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const body = new FormData(form);
        const response = await fetch("/public/mail", {method: "POST", body});
        if (!response.ok) { alert((await response.json()).detail); return; }
        try { localStorage.setItem("roomName", body.get("name")); } catch (e) {}
        refresh();
      });
    }
  }
  updateSeat(s);
}

function updateSeat(s) {
  const note = document.getElementById("turnNote");
  if (note && s.me === "speaker") {
    note.textContent = (s.busy ? room.being + " is answering… " : "") + s.turnsLeft + " message" + (s.turnsLeft === 1 ? "" : "s") +
      " left in this visit; it ends after " + Math.round(s.idleSeconds / 60) + " minutes of silence.";
    const button = document.querySelector("#turnForm button[type=submit]");
    if (button) button.disabled = !!s.busy;
  }
  if (s.me === "queue") {
    const b = seat.querySelector(".seat-note b");
    if (b) b.textContent = "number " + s.position;
  }
}

function row(item, tag = "") {
  const valence = (item.valence >= 0 ? "+" : "") + item.valence.toFixed(2);
  return '<li class="stan-item"><span class="vbadge ' + (item.valence >= 0 ? "pos" : "neg") + '">' + valence +
    '</span><span class="ibar"><i style="width:' + Math.round((item.felt || 0) * 100) + '%"></i></span><span class="etext">' + text(item.feeling) +
    (item.event ? " — " + text(item.event) : "") + (item.conclusion ? " → " + text(item.conclusion) : "") + "</span>" +
    (tag ? '<span class="eago dim">' + text(tag) + "</span>" : "") + "</li>";
}

function renderInner(state) {
  if (!state) {
    document.getElementById("state").innerHTML = '<li class="dim">nothing yet</li>';
    return;
  }
  document.getElementById("state").innerHTML = state.state.length ? state.state.map(item => row(item, item.evoked ? "association" : "")).join("") : '<li class="dim">calm — nothing felt</li>';
  document.getElementById("stateCount").textContent = "(" + state.state.length + ")";
  document.getElementById("focus").innerHTML = state.focus.map(item => row(item, item.evoked ? "association" : "")).join("") || '<li class="dim">nothing now</li>';
  document.getElementById("focusCount").textContent = "(" + state.focus.length + ")";
  document.getElementById("summary").innerHTML = state.summary
    ? '<li class="stan-item"><span class="etext">' + text(state.summary) + "</span></li>" : '<li class="dim">no conversation now</li>';
  document.getElementById("held").innerHTML = state.held.length
    ? state.held.map(h => '<li class="stan-item"><span class="etext">' + text(h.text) + "</span></li>").join("")
    : '<li class="dim">nothing yet</li>';
  document.getElementById("dispositions").innerHTML = state.dispositions.map(d =>
    '<li class="stan-item"><span class="vbadge ' + (d.weight >= 0 ? "pos" : "neg") + '">' + (d.weight >= 0 ? "+" : "") +
    d.weight.toFixed(2) + '</span><span class="etext">' + text(d.rule) + "</span></li>").join("") || '<li class="dim">none applied to the last reply</li>';
  document.getElementById("dispositionCount").textContent = "(" + state.dispositions.length + ")";
}

let refreshing = false;
async function refresh() {
  if (refreshing) return;
  refreshing = true;
  try {
    const response = await fetch("/public/room");
    if (!response.ok) return;
    const data = await response.json();
    status = data.status;
    renderStatus(data.status, data.about);
    renderSeat(data.status);
    renderLog(data.log);
    renderInner(data.inner);
  } catch (e) {
  } finally {
    refreshing = false;
  }
}

function listen() {
  const source = new EventSource("/public/stream");
  source.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.kind === "message") {
      if (!shownAt.has(data.message.at)) { chat.appendChild(line(data.message)); chat.scrollTop = chat.scrollHeight; shownAt.add(data.message.at); }
      setTimeout(refresh, 300);
    } else if (data.kind === "room" || data.kind === "error") {
      setTimeout(refresh, 300);
    }
  };
  source.onerror = () => { source.close(); setTimeout(listen, 5000); };
}

document.querySelectorAll("[data-admin]").forEach(button => button.addEventListener("click", async () => {
  const response = await fetch("/public/admin/" + button.dataset.admin, {method: "POST"});
  if (!response.ok) alert(await response.text());
  refresh();
}));

refresh();
listen();
setInterval(refresh, 5000);
