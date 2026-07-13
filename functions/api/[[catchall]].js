export async function onRequest(context) {
    // context.request is the incoming Request object
    // context.env is the environment variables (bindings)
    
    const request = context.request;
    const url = new URL(request.url);
    
    // The target URL (Cloudflare Tunnel backend) should be configured in Pages env variables
    const TUNNEL_URL = context.env.TUNNEL_URL || 'http://127.0.0.1:8000';
    
    // If TUNNEL_URL is local for some reason, we might want to fail gracefully in prod
    if (TUNNEL_URL === 'http://127.0.0.1:8000' && !url.hostname.includes('localhost') && !url.hostname.includes('127.0.0.1')) {
        // Fallback for demonstration if the user forgets to set TUNNEL_URL in prod
        // In reality, this would just fail to fetch a local IP from Cloudflare edge.
    }

    // Construct the destination URL
    const destinationUrl = new URL(url.pathname + url.search, TUNNEL_URL);

    // Create a new request based on the original, modifying the URL
    const proxyRequest = new Request(destinationUrl.toString(), new Request(request));

    // Optional: Inject extra headers here if needed for authorization to the backend
    // proxyRequest.headers.set('X-Nemesis-Client', 'Pages-Worker');

    // Handle WebSocket Upgrades
    if (request.headers.get("Upgrade") === "websocket") {
        return fetch(proxyRequest);
    }

    try {
        const response = await fetch(proxyRequest);
        
        // Return a new response to allow CORS modification if necessary
        const newResponse = new Response(response.body, response);
        newResponse.headers.set('Access-Control-Allow-Origin', '*');
        
        return newResponse;
    } catch (err) {
        return new Response(JSON.stringify({ error: "Backend Tunnel unreachable", details: err.message }), {
            status: 502,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}
