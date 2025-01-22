"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const ws_1 = require("ws");
const rooms = {}; // Armazena conexões por sala
const wss = new ws_1.WebSocketServer({ port: 3000 });
wss.on("connection", (socket, req) => {
    var _a;
    const roomName = ((_a = req.url) === null || _a === void 0 ? void 0 : _a.replace("/", "")) || "default"; // Nome da sala (ex: /sala1 -> sala1)
    // Cria a sala se não existir
    if (!rooms[roomName]) {
        rooms[roomName] = new Set();
    }
    // Adiciona o cliente à sala
    rooms[roomName].add(socket);
    console.log(`Cliente conectado na sala: ${roomName}`);
    // Recebe e repassa mensagens
    socket.on("message", (message) => {
        console.log(`Mensagem na ${roomName}: ${message}`);
        rooms[roomName].forEach(client => {
            if (client.readyState === ws_1.WebSocket.OPEN) {
                client.send(message.toString());
            }
        });
    });
    // Remove o cliente ao desconectar
    socket.on("close", () => {
        rooms[roomName].delete(socket);
        console.log(`Cliente desconectado da sala: ${roomName}`);
    });
});
console.log("Servidor WebSocket rodando na porta 3000.");
