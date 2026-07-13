interface Env {
  BACKEND: Fetcher;
}

export const onRequest: PagesFunction<Env> = async (context) => {
  const request = context.request;

  try {
    // Route API requests natively through the Cloudflare Edge to the Python Worker
    // WebSocket upgrades are automatically handled by Service Bindings
    const response = await context.env.BACKEND.fetch(request);

    // Inject Enterprise Proxy Headers
    const responseHeaders = new Headers(response.headers);
    responseHeaders.set("X-Nemesis-Edge-Proxy", "Active");

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
    
  } catch (err) {
    return new Response(JSON.stringify({ error: "Edge Proxy Error", details: err.message }), {
      status: 502,
      headers: { "Content-Type": "application/json" }
    });
  }
};
