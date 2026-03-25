const $ = (id) => document.getElementById(id);

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

$("loadLogs").onclick = async () => {
  const res = await fetch('/api/logs?limit=20');
  const data = await res.json();
  $("logs").textContent = JSON.stringify(data, null, 2);
};
