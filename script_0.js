
    // ==========================================
    // DYNAMIC BACKEND ROUTING FOR CLOUDFLARE/LOCAL
    // ==========================================
    const IS_LOCAL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.hostname === "";
    window.BACKEND_URL = IS_LOCAL ? "" : "http://127.0.0.1:3001";
    
    let protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
    window.WS_URL = IS_LOCAL ? (protocol + window.location.host) : "ws://127.0.0.1:3001";
    // ==========================================

        const originalWarn = console.warn;
        console.warn = function(...args) {
            if (args[0] && typeof args[0] === 'string' && args[0].includes('cdn.tailwindcss.com should not be used in production')) return;
            originalWarn.apply(console, args);
        };
    