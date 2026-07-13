export default {
    async fetch(request, env, ctx) {
        const url = new URL(request.url);
        
        // Define our Backend Targets
        // NOTE: These are placeholders. The actual deployment domains should be set in Cloudflare Secrets/Env Vars
        // e.g. env.PRIMARY_BACKEND = "nemesis-backend.onrender.com"
        const primaryHost = env.PRIMARY_BACKEND || "nemesis-backend.onrender.com";
        const secondaryHost = env.SECONDARY_BACKEND || "nemesis-api.vercel.app";

        // Route: API and WebSockets
        if (url.pathname.startsWith("/api")) {
            const isWebSocket = request.headers.get("Upgrade") === "websocket";

            // 1. WebSocket Handling (Must go to Render as Vercel Serverless drops WS connections)
            if (isWebSocket) {
                const targetUrl = new URL(request.url);
                targetUrl.hostname = primaryHost;
                targetUrl.protocol = "https:"; // fetch requires https, CF handles the WS upgrade
                
                try {
                    return await fetch(targetUrl.toString(), request);
                } catch (err) {
                    return new Response("Primary WebSocket Backend Offline", { status: 502 });
                }
            }

            // 2. Standard HTTP API Handling (With Fallback)
            const primaryUrl = new URL(request.url);
            primaryUrl.hostname = primaryHost;
            primaryUrl.protocol = "https:";
            
            try {
                const response = await fetch(primaryUrl.toString(), request);
                // If primary returns a 5xx Server Error, trigger fallback
                if (response.status >= 500) {
                    throw new Error("Primary backend returned 5xx error");
                }
                return response;
            } catch (err) {
                // Fallback to Secondary (Vercel)
                const secondaryUrl = new URL(request.url);
                secondaryUrl.hostname = secondaryHost;
                secondaryUrl.protocol = "https:";
                
                try {
                    return await fetch(secondaryUrl.toString(), request);
                } catch (fallbackErr) {
                    return new Response(JSON.stringify({
                        error: "CRITICAL SYSTEM FAILURE",
                        details: "Both Primary and Secondary backends are offline."
                    }), {
                        status: 503,
                        headers: { "Content-Type": "application/json" }
                    });
                }
            }
        }

        // If the route doesn't match API, return 404
        return new Response("Not Found. This worker only routes /api traffic.", { status: 404 });
    }
};
