export { InvestigationSession } from './InvestigationSession';

export interface Env {
  INVESTIGATION_SESSION: DurableObjectNamespace;
  TRACE_QUEUE: Queue;
  NEMESIS_METADATA_CACHE: KVNamespace;
  PYTHON_API_URL?: string;
  VERCEL_API_URL?: string;
}

// Handle CORS for browser
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

// Main Fetch Handler
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    try {
      if (request.method === 'OPTIONS') {
        return new Response(null, { headers: corsHeaders });
      }

      const url = new URL(request.url);

      if (request.method === 'GET' && url.pathname === '/api/health') {
        return new Response(JSON.stringify({ status: 'ok', version: 'v1.0' }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }

      if (request.method === 'GET' && url.pathname === '/api/ws/trace') {
        const upgradeHeader = request.headers.get('Upgrade');
        if (!upgradeHeader || upgradeHeader !== 'websocket') {
          return new Response('Expected Upgrade: websocket', { status: 426, headers: corsHeaders });
        }

        const id = env.INVESTIGATION_SESSION.idFromName('global-live-feed');
        const stub = env.INVESTIGATION_SESSION.get(id);
        return stub.fetch(request);
      }

      if (request.method === 'POST' && url.pathname === '/internal/broadcast') {
        const id = env.INVESTIGATION_SESSION.idFromName('global-live-feed');
        const stub = env.INVESTIGATION_SESSION.get(id);
        return stub.fetch(request);
      }

      if (request.method === 'POST' && (url.pathname === '/api/trace/start' || url.pathname === '/api/start_trace')) {
        const body = await request.json();
        
        if (env.TRACE_QUEUE) {
          await env.TRACE_QUEUE.send(body);
        } else {
          console.warn("TRACE_QUEUE binding missing, bypassing queue.");
        }

        return new Response(JSON.stringify({ status: 'queued', message: 'Trace initiated' }), {
          headers: { 'Content-Type': 'application/json', ...corsHeaders }
        });
      }

      // Proxy all other /api/ requests to the Python backend
      if (url.pathname.startsWith('/api/')) {
        const targetUrl = new URL(url.pathname + url.search, env.PYTHON_API_URL || 'https://projectnemesis.onrender.com');
        try {
          const proxyReq = new Request(targetUrl.toString(), {
            method: request.method,
            headers: request.headers,
            body: request.method !== 'GET' && request.method !== 'HEAD' ? request.body : null,
          });
          
          const response = await fetch(proxyReq);
          const newHeaders = new Headers(response.headers);
          newHeaders.set('Access-Control-Allow-Origin', '*');
          
          return new Response(response.body, {
            status: response.status,
            statusText: response.statusText,
            headers: newHeaders
          });
        } catch (err: any) {
          return new Response(JSON.stringify({ error: 'Proxy failed', details: err.message }), { 
            status: 502, 
            headers: { 'Content-Type': 'application/json', ...corsHeaders } 
          });
        }
      }

      return new Response('Not Found', { status: 404, headers: corsHeaders });
    } catch (err: any) {
      console.error(err);
      return new Response(`Internal Server Error: ${err.message}\n${err.stack}`, { status: 500, headers: corsHeaders });
    }
  },

  async queue(batch: MessageBatch<any>, env: Env): Promise<void> {
    const primaryWebhook = env.PYTHON_API_URL || 'https://projectnemesis.onrender.com/api/trace/webhook';
    const fallbackWebhook = env.VERCEL_API_URL; // e.g. https://nemesis-vercel.vercel.app/api/trace/webhook

    for (const msg of batch.messages) {
      try {
        let response = await fetch(primaryWebhook, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(msg.body)
        });

        // AUTO-SWITCH: If primary fails and Vercel fallback is configured
        if (!response.ok && fallbackWebhook) {
          console.warn(`Primary backend (${primaryWebhook}) failed with status ${response.status}. Auto-switching to Vercel fallback...`);
          response = await fetch(fallbackWebhook, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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
