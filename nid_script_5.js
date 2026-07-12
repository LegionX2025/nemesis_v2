
        (function() {
            const batch = [];
            const originalLog = console.log;
            const originalError = console.error;
            const originalWarn = console.warn;
            const originalInfo = console.info;

            function sendBatch() {
                if(batch.length === 0) return;
                const logsToSend = batch.splice(0, batch.length);
                fetch('/api/logs/frontend', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ logs: logsToSend })
                }).catch(e => { /* fail silently to avoid loop */ });
            }

            setInterval(sendBatch, 2000);

            function captureLog(level, args) {
                try {
                    const msg = args.map(a => {
                        if (a instanceof Error) return a.stack || a.message;
                        return typeof a === 'object' ? JSON.stringify(a) : String(a);
                    }).join(' ');
                    batch.push({ level, message: msg, source: 'FRONTEND', timestamp: new Date().toISOString() });
                    if(batch.length >= 20) sendBatch();
                } catch(e) {}
            }

            console.log = function(...args) { captureLog('info', args); originalLog.apply(console, args); };
            console.error = function(...args) { captureLog('error', args); originalError.apply(console, args); };
            console.warn = function(...args) { captureLog('warn', args); originalWarn.apply(console, args); };
            console.info = function(...args) { captureLog('info', args); originalInfo.apply(console, args); };

            window.addEventListener('error', function(e) {
                captureLog('error', ['Uncaught Error:', e.message, 'at', e.filename, 'line', e.lineno]);
            });

            window.addEventListener('unhandledrejection', function(e) {
                captureLog('error', ['Unhandled Promise Rejection:', e.reason]);
            });
        })();
    