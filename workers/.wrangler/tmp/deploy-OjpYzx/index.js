var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// src/InvestigationSession.ts
var InvestigationSession = class {
  static {
    __name(this, "InvestigationSession");
  }
  state;
  sessions;
  constructor(state, env) {
    this.state = state;
    this.sessions = /* @__PURE__ */ new Set();
    this.state.getWebSockets().forEach((ws) => {
      this.sessions.add(ws);
    });
  }
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method === "POST" && url.pathname === "/internal/broadcast") {
      const payload = await request.text();
      this.broadcast(payload);
      return new Response("Broadcast successful", { status: 200 });
    }
    if (request.headers.get("Upgrade") === "websocket") {
      const pair = new WebSocketPair();
      const [client, server] = Object.values(pair);
      this.state.acceptWebSocket(server);
      this.sessions.add(server);
      server.send(JSON.stringify({ type: "LOG", message: "Connected to Cloudflare Durable Object." }));
      return new Response(null, {
        status: 101,
        webSocket: client
      });
    }
    return new Response("Not found", { status: 404 });
  }
  webSocketMessage(ws, message) {
    console.log("Received message from frontend:", message);
  }
  webSocketClose(ws, code, reason, wasClean) {
    this.sessions.delete(ws);
  }
  webSocketError(ws, error) {
    this.sessions.delete(ws);
  }
  broadcast(msg) {
    for (let ws of this.sessions) {
      try {
        ws.send(msg);
      } catch (e) {
        this.sessions.delete(ws);
      }
    }
  }
};

// src/index.ts
var corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization"
};
var index_default = {
  async fetch(request, env, ctx) {
    try {
      if (request.method === "OPTIONS") {
        return new Response(null, { headers: corsHeaders });
      }
      const url = new URL(request.url);
      if (request.method === "GET" && url.pathname === "/api/health") {
        return new Response(JSON.stringify({ status: "ok", version: "v1.0" }), {
          headers: { "Content-Type": "application/json", ...corsHeaders }
        });
      }
      if (request.method === "GET" && url.pathname === "/api/ws/trace") {
        const upgradeHeader = request.headers.get("Upgrade");
        if (!upgradeHeader || upgradeHeader !== "websocket") {
          return new Response("Expected Upgrade: websocket", { status: 426, headers: corsHeaders });
        }
        const id = env.INVESTIGATION_SESSION.idFromName("global-live-feed");
        const stub = env.INVESTIGATION_SESSION.get(id);
        return stub.fetch(request);
      }
      if (request.method === "POST" && url.pathname === "/internal/broadcast") {
        const id = env.INVESTIGATION_SESSION.idFromName("global-live-feed");
        const stub = env.INVESTIGATION_SESSION.get(id);
        return stub.fetch(request);
      }
      if (request.method === "POST" && (url.pathname === "/api/trace/start" || url.pathname === "/api/start_trace")) {
        const body = await request.json();
        if (env.TRACE_QUEUE) {
          await env.TRACE_QUEUE.send(body);
        } else {
          console.warn("TRACE_QUEUE binding missing, bypassing queue.");
        }
        return new Response(JSON.stringify({ status: "queued", message: "Trace initiated" }), {
          headers: { "Content-Type": "application/json", ...corsHeaders }
        });
      }
      return new Response("Not Found", { status: 404, headers: corsHeaders });
    } catch (err) {
      console.error(err);
      return new Response(`Internal Server Error: ${err.message}
${err.stack}`, { status: 500, headers: corsHeaders });
    }
  },
  async queue(batch, env) {
    const primaryWebhook = env.PYTHON_API_URL || "https://projectnemesis.onrender.com/api/trace/webhook";
    const fallbackWebhook = env.VERCEL_API_URL;
    for (const msg of batch.messages) {
      try {
        let response = await fetch(primaryWebhook, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(msg.body)
        });
        if (!response.ok && fallbackWebhook) {
          console.warn(`Primary backend (${primaryWebhook}) failed with status ${response.status}. Auto-switching to Vercel fallback...`);
          response = await fetch(fallbackWebhook, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(msg.body)
          });
        }
        if (response.ok) {
          msg.ack();
        } else {
          throw new Error(`Both backends failed to process trace request.`);
        }
      } catch (err) {
        console.error("Failed to forward queue msg:", err);
        msg.retry();
      }
    }
  }
};
export {
  InvestigationSession,
  index_default as default
};
//# sourceMappingURL=index.js.map
