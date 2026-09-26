// Shared helpers of the panel: live streams and small form actions.
function followStream(url, onEvent) {
  const source = new EventSource(url);
  source.onmessage = (message) => onEvent(JSON.parse(message.data));
  return source;
}

function postAndReload(url, confirmText) {
  if (confirmText && !confirm(confirmText)) return;
  fetch(url, {method: "POST"}).then(() => location.reload());
}

function escapeHtml(text) {
  return String(text ?? "").replace(/[&<>"]/g, (c) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
}
