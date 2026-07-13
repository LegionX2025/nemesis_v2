import { Router } from 'itty-router';
export { InvestigationSession } from './InvestigationSession';

export interface Env {
  INVESTIGATION_SESSION: DurableObjectNamespace;
  TRACE_QUEUE: Queue;
  NEMESIS_METADATA_CACHE: KVNamespace;
  PYTHON_API_URL?: string;
  VERCEL_API_URL?: string;
}

const router = Router();

// Handle CORS for browser
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

router.options('*', () => new Response(null, { headers: corsHeaders }));

// WebSocket connection endpoint for Tracer
router.get('/api/ws/trace', (request: Request, env: Env) => {
  const upgradeHeader = request.headers.get('Upgrade');
  if (!upgradeHeader || upgradeHeader !== 'websocket') {
    return new Response('Expected Upgrade: websocket', { status: 426 });
  }

  // Bind to a global session for the tracer dashboard
  const id = env.INVESTIGATION_SESSION.idFromName('global-live-feed');
  const stub = env.INVESTIGATION_SESSION.get(id);

  return stub.fetch(request);
});

// Webhook endpoint for Python API to broadcast to all connected WebSockets
router.post('/internal/broadcast', async (request: Request, env: Env) => {
  const id = env.INVESTIGATION_SESSION.idFromName('global-live-feed');
  const stub = env.INVESTIGATION_SESSION.get(id);
  
  return stub.fetch(request);
});

// Endpoint to start a new trace (enqueues to Cloudflare Queues)
router.post('/api/trace/start', async (request: Request, env: Env) => {
  try {
    const body = await request.json();
    
    // Add to Cloudflare Queue for background processing by the Python AI Router
    if (env.TRACE_QUEUE) {
      await env.TRACE_QUEUE.send(body);
    } else {
      console.warn("TRACE_QUEUE binding missing, bypassing queue.");
      // Fallback: If Queue is not bound, we could forward directly to Python API
      // await fetch(`${env.PYTHON_API_URL}/api/trace`, { method: 'POST', body: JSON.stringify(body) });
    }

    return new Response(JSON.stringify({ status: 'queued', message: 'Trace initiated' }), {
      headers: { 'Content-Type': 'application/json', ...corsHeaders }
    });
  } catch (err: any) {
    return new Response(JSON.stringify({ error: err.message }), { status: 400, headers: corsHeaders });
  }
});

// Main Fetch Handler
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    return router.handle(request, env, ctx).catch((err: Error) => {
      console.error(err);
      return new Response('Internal Server Error', { status: 500, headers: corsHeaders });
    });
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
