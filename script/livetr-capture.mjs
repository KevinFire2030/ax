import fs from "node:fs";
import path from "node:path";

const roomCode = process.argv[2] ?? "180342";
const lang = process.argv[3] ?? "ko";
const outDir = path.resolve(process.argv[4] ?? "livetr-captures");

const baseUrl = "https://ai-realtime.flit.to";
const apiPath = "/v1/ai/broadcasting";
const wsUrl = `wss://ai-realtime.flit.to${apiPath}/chat/realtime/${roomCode}`;

fs.mkdirSync(outDir, { recursive: true });

const stamp = new Date().toISOString().replace(/[:.]/g, "-");
const rawPath = path.join(outDir, `${roomCode}-${stamp}.jsonl`);
const mdPath = path.join(outDir, `${roomCode}-${stamp}.md`);
const latestPath = path.join(outDir, `${roomCode}-latest.md`);

const chats = new Map();
const pendingTranslation = new Set();
let ws;
let roomInfo;
let closedByUser = false;
let reconnectDelayMs = 1000;
let pingTimer;

function msToIso(ms) {
  if (!Number.isFinite(Number(ms))) return "";
  return new Date(Number(ms)).toISOString();
}

function cleanText(value) {
  return String(value ?? "").replace(/\s+/g, " ").trim();
}

function upsertChat(chat) {
  if (!chat?.chat_id) return;
  const previous = chats.get(chat.chat_id) ?? {};
  chats.set(chat.chat_id, { ...previous, ...chat });
}

function lineFor(chat) {
  const original = cleanText(chat.text_for_tr || chat.text);
  const translated = cleanText(chat.content);
  const time = msToIso(chat.timestamp);
  const src = chat.src_lang_code ?? "";
  const dst = chat.dst_lang_code ?? lang;

  if (translated && translated !== original) {
    return `- ${time} [${src}->${dst}] ${translated}\n  Original: ${original}`;
  }
  return `- ${time} [${src}] ${original}`;
}

function writeSnapshot() {
  const rows = [...chats.values()]
    .filter((chat) => cleanText(chat.text_for_tr || chat.text || chat.content))
    .sort((a, b) => Number(a.timestamp ?? 0) - Number(b.timestamp ?? 0));

  const header = [
    `# LiveTR ${roomCode}`,
    "",
    `- Title: ${roomInfo?.chat_room_title ?? ""}`,
    `- Saved at: ${new Date().toISOString()}`,
    `- Language: ${lang}`,
    `- Messages: ${rows.length}`,
    "",
  ].join("\n");

  const body = rows.map(lineFor).join("\n\n");
  fs.writeFileSync(mdPath, `${header}${body}\n`, "utf8");
  fs.copyFileSync(mdPath, latestPath);
}

function logEvent(event) {
  fs.appendFileSync(rawPath, `${JSON.stringify({ received_at: new Date().toISOString(), event })}\n`, "utf8");
}

function requestTranslation(chat) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  if (!chat?.chat_id || pendingTranslation.has(chat.chat_id)) return;
  const source = cleanText(chat.text_for_tr || chat.text);
  if (!source || chat.src_lang_code === lang || cleanText(chat.content)) return;

  pendingTranslation.add(chat.chat_id);
  ws.send(JSON.stringify({
    task_type: "translation",
    data: {
      chat_room_id: chat.chat_room_id ?? roomInfo?.chat_room_id,
      chat_id: chat.chat_id,
      timestamp: chat.timestamp,
      text: source,
      src_lang_code: chat.src_lang_code,
      dst_lang_code: lang,
    },
  }));
}

function requestMissingTranslations() {
  for (const chat of chats.values()) requestTranslation(chat);
}

function handleChatList(data) {
  for (const chat of data.chat_list ?? []) {
    if (!chat) continue;
    if (data.list_type === "translation") pendingTranslation.delete(chat.chat_id);
    upsertChat(chat);
  }
  requestMissingTranslations();
  writeSnapshot();
}

async function main() {
  const response = await fetch(`${baseUrl}${apiPath}/chat/chat-rooms/check/interaction-keys/${roomCode}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ token: null }),
  });

  if (!response.ok) {
    throw new Error(`Room info failed: ${response.status} ${await response.text()}`);
  }

  roomInfo = await response.json();
  connect();
}

function connect() {
  const url = roomInfo.auth_token ? `${wsUrl}?auth_token=${roomInfo.auth_token}` : wsUrl;

  ws = new WebSocket(url);
  ws.addEventListener("open", () => {
    reconnectDelayMs = 1000;
    console.log(`capturing ${roomCode} -> ${mdPath}`);
    clearInterval(pingTimer);
    pingTimer = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send("ping");
    }, 50000);
    pingTimer.unref?.();
  });

  ws.addEventListener("message", (event) => {
    if (event.data === "pong") return;
    const parsed = JSON.parse(event.data);
    logEvent(parsed);
    if (parsed?.data?.chat_list) handleChatList(parsed.data);
  });

  ws.addEventListener("close", () => {
    clearInterval(pingTimer);
    writeSnapshot();
    console.log(`closed ${roomCode}`);
    if (!closedByUser) {
      const delay = reconnectDelayMs;
      reconnectDelayMs = Math.min(reconnectDelayMs * 2, 30000);
      setTimeout(connect, delay);
    }
  });

  ws.addEventListener("error", (event) => {
    console.error("websocket error", event.message ?? event);
  });
}

process.on("SIGINT", () => {
  closedByUser = true;
  ws?.close();
  process.exit(0);
});

process.on("SIGTERM", () => {
  closedByUser = true;
  ws?.close();
  process.exit(0);
});

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
