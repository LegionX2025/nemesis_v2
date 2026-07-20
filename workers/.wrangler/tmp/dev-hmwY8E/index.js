var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// .wrangler/tmp/bundle-AOQi8x/checked-fetch.js
var urls = /* @__PURE__ */ new Set();
function checkURL(request, init) {
  const url = request instanceof URL ? request : new URL(
    (typeof request === "string" ? new Request(request, init) : request).url
  );
  if (url.port && url.port !== "443" && url.protocol === "https:") {
    if (!urls.has(url.toString())) {
      urls.add(url.toString());
      console.warn(
        `WARNING: known issue with \`fetch()\` requests to custom HTTPS ports in published Workers:
 - ${url.toString()} - the custom port will be ignored when the Worker is published using the \`wrangler deploy\` command.
`
      );
    }
  }
}
__name(checkURL, "checkURL");
globalThis.fetch = new Proxy(globalThis.fetch, {
  apply(target, thisArg, argArray) {
    const [request, init] = argArray;
    checkURL(request, init);
    return Reflect.apply(target, thisArg, argArray);
  }
});

// .wrangler/tmp/bundle-AOQi8x/strip-cf-connecting-ip-header.js
function stripCfConnectingIPHeader(input, init) {
  const request = new Request(input, init);
  request.headers.delete("CF-Connecting-IP");
  return request;
}
__name(stripCfConnectingIPHeader, "stripCfConnectingIPHeader");
globalThis.fetch = new Proxy(globalThis.fetch, {
  apply(target, thisArg, argArray) {
    return Reflect.apply(target, thisArg, [
      stripCfConnectingIPHeader.apply(null, argArray)
    ]);
  }
});

// src/InvestigationSession.ts
var InvestigationSession = class {
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
__name(InvestigationSession, "InvestigationSession");

// src/index.ts
var corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization"
};
var src_default = {
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

// node_modules/wrangler/templates/middleware/middleware-ensure-req-body-drained.ts
var drainBody = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } finally {
    try {
      if (request.body !== null && !request.bodyUsed) {
        const reader = request.body.getReader();
        while (!(await reader.read()).done) {
        }
      }
    } catch (e) {
      console.error("Failed to drain the unused request body.", e);
    }
  }
}, "drainBody");
var middleware_ensure_req_body_drained_default = drainBody;

// node_modules/wrangler/templates/middleware/middleware-miniflare3-json-error.ts
function reduceError(e) {
  return {
    name: e?.name,
    message: e?.message ?? String(e),
    stack: e?.stack,
    cause: e?.cause === void 0 ? void 0 : reduceError(e.cause)
  };
}
__name(reduceError, "reduceError");
var jsonError = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } catch (e) {
    const error = reduceError(e);
    return Response.json(error, {
      status: 500,
      headers: { "MF-Experimental-Error-Stack": "true" }
    });
  }
}, "jsonError");
var middleware_miniflare3_json_error_default = jsonError;

// .wrangler/tmp/bundle-AOQi8x/middleware-insertion-facade.js
var __INTERNAL_WRANGLER_MIDDLEWARE__ = [
  middleware_ensure_req_body_drained_default,
  middleware_miniflare3_json_error_default
];
var middleware_insertion_facade_default = src_default;

// node_modules/wrangler/templates/middleware/common.ts
var __facade_middleware__ = [];
function __facade_register__(...args) {
  __facade_middleware__.push(...args.flat());
}
__name(__facade_register__, "__facade_register__");
function __facade_invokeChain__(request, env, ctx, dispatch, middlewareChain) {
  const [head, ...tail] = middlewareChain;
  const middlewareCtx = {
    dispatch,
    next(newRequest, newEnv) {
      return __facade_invokeChain__(newRequest, newEnv, ctx, dispatch, tail);
    }
  };
  return head(request, env, ctx, middlewareCtx);
}
__name(__facade_invokeChain__, "__facade_invokeChain__");
function __facade_invoke__(request, env, ctx, dispatch, finalMiddleware) {
  return __facade_invokeChain__(request, env, ctx, dispatch, [
    ...__facade_middleware__,
    finalMiddleware
  ]);
}
__name(__facade_invoke__, "__facade_invoke__");

// .wrangler/tmp/bundle-AOQi8x/middleware-loader.entry.ts
var __Facade_ScheduledController__ = class {
  constructor(scheduledTime, cron, noRetry) {
    this.scheduledTime = scheduledTime;
    this.cron = cron;
    this.#noRetry = noRetry;
  }
  #noRetry;
  noRetry() {
    if (!(this instanceof __Facade_ScheduledController__)) {
      throw new TypeError("Illegal invocation");
    }
    this.#noRetry();
  }
};
__name(__Facade_ScheduledController__, "__Facade_ScheduledController__");
function wrapExportedHandler(worker) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return worker;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  const fetchDispatcher = /* @__PURE__ */ __name(function(request, env, ctx) {
    if (worker.fetch === void 0) {
      throw new Error("Handler does not export a fetch() function.");
    }
    return worker.fetch(request, env, ctx);
  }, "fetchDispatcher");
  return {
    ...worker,
    fetch(request, env, ctx) {
      const dispatcher = /* @__PURE__ */ __name(function(type, init) {
        if (type === "scheduled" && worker.scheduled !== void 0) {
          const controller = new __Facade_ScheduledController__(
            Date.now(),
            init.cron ?? "",
            () => {
            }
          );
          return worker.scheduled(controller, env, ctx);
        }
      }, "dispatcher");
      return __facade_invoke__(request, env, ctx, dispatcher, fetchDispatcher);
    }
  };
}
__name(wrapExportedHandler, "wrapExportedHandler");
function wrapWorkerEntrypoint(klass) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return klass;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  return class extends klass {
    #fetchDispatcher = (request, env, ctx) => {
      this.env = env;
      this.ctx = ctx;
      if (super.fetch === void 0) {
        throw new Error("Entrypoint class does not define a fetch() function.");
      }
      return super.fetch(request);
    };
    #dispatcher = (type, init) => {
      if (type === "scheduled" && super.scheduled !== void 0) {
        const controller = new __Facade_ScheduledController__(
          Date.now(),
          init.cron ?? "",
          () => {
          }
        );
        return super.scheduled(controller);
      }
    };
    fetch(request) {
      return __facade_invoke__(
        request,
        this.env,
        this.ctx,
        this.#dispatcher,
        this.#fetchDispatcher
      );
    }
  };
}
__name(wrapWorkerEntrypoint, "wrapWorkerEntrypoint");
var WRAPPED_ENTRY;
if (typeof middleware_insertion_facade_default === "object") {
  WRAPPED_ENTRY = wrapExportedHandler(middleware_insertion_facade_default);
} else if (typeof middleware_insertion_facade_default === "function") {
  WRAPPED_ENTRY = wrapWorkerEntrypoint(middleware_insertion_facade_default);
}
var middleware_loader_entry_default = WRAPPED_ENTRY;
export {
  InvestigationSession,
  __INTERNAL_WRANGLER_MIDDLEWARE__,
  middleware_loader_entry_default as default
};
//# sourceMappingURL=index.js.map
