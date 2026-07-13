// Cloudflare Pages Proxy to API Gateway
// This function catches all /api/* requests on the Pages frontend and pipes them
// securely over Cloudflare's internal network to the 'nemesis-api' Worker.

export async function onRequest(context) {
    const { request, env } = context;
    
    // We expect env.BACKEND to be bound to the 'nemesis-api' worker in wrangler.toml
    if (!env.BACKEND) {
        return new Response(JSON.stringify({ 
            error: "Service Binding Error", 
            message: "The BACKEND binding to the nemesis-api worker is missing." 
        }), { status: 500, headers: { "Content-Type": "application/json" } });
    }

    try {
        // Forward the exact request to the worker
        return await env.BACKEND.fetch(request);
    } catch (err) {
        return new Response(JSON.stringify({ 
            error: "Gateway Timeout", 
            message: "Failed to communicate with the nemesis-api gateway." 
        }), { status: 502, headers: { "Content-Type": "application/json" } });
    }
}
