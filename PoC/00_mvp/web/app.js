const $ = (id) => document.getElementById(id);
let examples = [];

async function loadExamples() {
  if (examples.length) return examples;
  const res = await fetch('/api/examples');
  const data = await res.json();
  examples = data.items || [];
  return examples;
}

$("run").onclick = async () => {
  const payload = {
    text: $("text").value,
    force_mode: $("mode").value
  };

  const res = await fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  $("result").textContent = JSON.stringify(data, null, 2);
};

$("randomExample").onclick = async () => {
  const list = await loadExamples();
  if (!list.length) {
    alert('예시 데이터가 없습니다.');
    return;
  }
  const picked = list[Math.floor(Math.random() * list.length)];
  $("text").value = picked.text || '';
  $("mode").value = picked.force_mode || 'auto';
};

$("loadLogs").onclick = async () => {
  const res = await fetch('/api/logs?limit=20');
  const data = await res.json();
  $("logs").textContent = JSON.stringify(data, null, 2);
};
