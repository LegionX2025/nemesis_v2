export default {
    async fetch(request, env, ctx) {
        const url = new URL(request.url);
        
        // Define our Backend Targets
        // NOTE: These are placeholders. The actual deployment domains should be set in Cloudflare Secrets/Env Vars
        // e.g. env.PRIMARY_BACKEND = "nemesis-backend.onrender.com"
        const primaryHost = env.PRIMARY_BACKEND || "nemesis-backend.onrender.com";
        const secondaryHost = env.SECONDARY_BACKEND || "nemesis-api.vercel.app";

        // Route: API and Socket.IO
        if (url.pathname.startsWith("/api") || url.pathname.startsWith("/socket.io")) {
            const primaryUrl = new URL(request.url);
            primaryUrl.hostname = env.PRIMARY_BACKEND || "127.0.0.1";
            primaryUrl.port = env.PRIMARY_PORT || "8000";
            primaryUrl.protocol = "http:";
            
            try {
                return await fetch(primaryUrl.toString(), request);
            } catch (err) {
                return new Response(JSON.stringify({
                    error: "CRITICAL SYSTEM FAILURE",
                    details: "Primary backend offline."
                }), {
                    status: 503,
                    headers: { "Content-Type": "application/json" }
                });
            }
        }

        // If the route doesn't match API, return 404
        return new Response("Not Found. This worker only routes /api traffic.", { status: 404 });
    }
};
