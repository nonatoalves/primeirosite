import { WebSocketServer, WebSocket } from "ws";

interface Rooms {
    [key: string]: Set<WebSocket>;
}

const rooms: Rooms = {}; // Armazena conexões por sala

const wss = new WebSocketServer({ port: 3000 });

wss.on("connection", (socket, req) => {
    const roomName = req.url?.replace("/", "") || "default"; // Nome da sala (ex: /sala1 -> sala1)

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
            if (client.readyState === WebSocket.OPEN) {
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
