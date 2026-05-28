async function fetchModels() {
  const res = await fetch('/api/models');
  const data = await res.json();
  const modelName = data.best || data;
  const span = document.getElementById('model');
  if (span) span.textContent = modelName;
}

function addMessage(role, text) {
  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = 'message ' + role;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function sendMessage(message) {
  addMessage('user', message);
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  const data = await res.json();
  if (data.error) {
    addMessage('assistant', 'Error: ' + data.error);
  } else {
    addMessage('assistant', data.reply);
  }
}

window.addEventListener('load', async () => {
  await fetchModels();
  document.getElementById('form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('input');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    await sendMessage(text);
  });
});
