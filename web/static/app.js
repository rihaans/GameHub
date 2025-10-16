let ws;
let playerId;

function log(msg) {
  const el = document.getElementById("log");
  el.textContent = msg + "\n" + el.textContent;
}

document.getElementById("connectBtn").onclick = () => {
  const name = document.getElementById("playerName").value || "Player1";
  ws = new WebSocket(
    `ws://${location.host}/ws?name=${encodeURIComponent(name)}`
  );
  ws.onopen = () => log("WebSocket connected");
  ws.onmessage = (ev) => {
    const data = JSON.parse(ev.data);
    log("RECV: " + JSON.stringify(data));
    if (data.type === "welcome") {
      playerId = data.player_id;
      log("Assigned player id: " + playerId);
    }
  };
  ws.onclose = () => log("WebSocket closed");
};

document.getElementById("createBtn").onclick = () => {
  const gameType = document.getElementById("gameType").value;
  ws.send(JSON.stringify({ type: "create", game_type: gameType }));
};

document.getElementById("joinBtn").onclick = () => {
  const room = document.getElementById("roomId").value;
  ws.send(JSON.stringify({ type: "join", room_id: room }));
};

document.getElementById("readyBtn").onclick = () => {
  ws.send(JSON.stringify({ type: "ready", ready: true }));
};

document.getElementById("sendActionBtn").onclick = () => {
  const action = document.getElementById("actionName").value;
  let data = {};
  try {
    data = JSON.parse(document.getElementById("actionData").value || "{}");
  } catch (e) {
    alert("Invalid JSON");
    return;
  }
  ws.send(JSON.stringify({ type: "action", action: action, data: data }));
};
