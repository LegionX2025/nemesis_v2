export class InvestigationSession implements DurableObject {
  state: DurableObjectState;
  sessions: Set<WebSocket>;

  constructor(state: DurableObjectState, env: any) {
    this.state = state;
    this.sessions = new Set();
    
    // Resume existing websockets from hibernation
    this.state.getWebSockets().forEach((ws) => {
      this.sessions.add(ws);
    });
  }

  async fetch(request: Request) {
    const url = new URL(request.url);

    // Python API pushes broadcast messages here
    if (request.method === 'POST' && url.pathname === '/internal/broadcast') {
      const payload = await request.text();
      this.broadcast(payload);
      return new Response('Broadcast successful', { status: 200 });
    }

    // Handle WebSocket upgrade from browser client
    if (request.headers.get("Upgrade") === "websocket") {
      const pair = new WebSocketPair();
      const [client, server] = Object.values(pair);

      this.state.acceptWebSocket(server);
      this.sessions.add(server);

      // Send connection acknowledgement
      server.send(JSON.stringify({ type: 'LOG', message: 'Connected to Cloudflare Durable Object.' }));

      return new Response(null, {
        status: 101,
        webSocket: client,
      });
    }

    return new Response("Not found", { status: 404 });
  }

  webSocketMessage(ws: WebSocket, message: ArrayBuffer | string) {
    console.log('Received message from frontend:', message);
  }

  webSocketClose(ws: WebSocket, code: number, reason: string, wasClean: boolean) {
    this.sessions.delete(ws);
  }

  webSocketError(ws: WebSocket, error: any) {
    this.sessions.delete(ws);
  }

  broadcast(msg: string) {
    for (let ws of this.sessions) {
      try {
        ws.send(msg);
      } catch (e) {
        this.sessions.delete(ws);
      }
    }
  }
}
