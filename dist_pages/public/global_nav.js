document.addEventListener('DOMContentLoaded', () => {
    // Determine active page
    const path = window.location.pathname;
    const isLanding = path === '/' || path.includes('landing.html');
    const isTracer = path.includes('tracer.html');
    const isID = path.includes('nemesis_id.html');
    const isAdmin = path.includes('admin.html');
    const isAudit = path.includes('audit_report.html');
    const isFramework = path.includes('recovery_framework.html');

    // 1. Inject Global CSS
    const style = document.createElement('style');
    style.innerHTML = `
        /* CORPORATE INTELLIGENCE LIGHT NAV */
        #global-nav {
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 70px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(226, 232, 240, 0.8);
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0 2rem;
            z-index: 99999;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
            font-family: 'Inter', sans-serif;
            transition: all 0.3s ease;
        }
        .global-nav-brand {
            display: flex; align-items: center; gap: 1rem; text-decoration: none;
        }
        .global-nav-brand img {
            height: 40px; border-radius: 8px; border: 1px solid rgba(15, 23, 42, 0.1);
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .global-nav-brand:hover img {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
        }
        .global-nav-brand span {
            font-weight: 800; font-size: 1.25rem; color: #0f172a; letter-spacing: 2px;
            text-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
        }
        .global-nav-links {
            display: flex; gap: 2rem; align-items: center;
        }
        .global-nav-links a {
            color: #94a3b8; text-decoration: none; font-size: 0.85rem; font-weight: 600;
            text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s ease;
            display: flex; align-items: center; gap: 0.5rem;
            position: relative;
        }
        .global-nav-links a::after {
            content: ''; position: absolute; width: 0; height: 2px; bottom: -5px; left: 0;
            background-color: #3b82f6; transition: width 0.3s ease;
            box-shadow: 0 0 8px #3b82f6;
        }
        .global-nav-links a:hover::after, .global-nav-links a.active::after {
            width: 100%;
        }
        .global-nav-links a:hover, .global-nav-links a.active {
            color: #60a5fa; 
            text-shadow: 0 0 8px rgba(96, 165, 250, 0.4);
        }
        
        /* CORPORATE INTELLIGENCE DARK FOOTER */
        #global-footer {
            position: fixed;
            bottom: 0; left: 0; right: 0;
            height: 40px;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(8px);
            border-top: 1px solid rgba(51, 65, 85, 0.8);
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 99999;
            color: #94a3b8;
            font-size: 0.75rem;
            font-family: 'JetBrains Mono', monospace;
            box-shadow: 0 -4px 30px rgba(0, 0, 0, 0.5);
        }
        .global-footer-status {
            display: flex; align-items: center; gap: 0.5rem; color: #10b981; font-weight: 600;
            text-shadow: 0 0 5px rgba(16, 185, 129, 0.4);
        }
        .status-dot {
            width: 8px; height: 8px; background-color: #10b981; border-radius: 50%;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.8); animation: pulse-fast 1.5s infinite alternate;
        }
        @keyframes pulse-fast { from { opacity: 0.4; box-shadow: 0 0 5px rgba(16, 185, 129, 0.5); } to { opacity: 1; transform: scale(1.1); box-shadow: 0 0 15px rgba(16, 185, 129, 1); } }

        /* Ensure body accounts for fixed nav */
        body { margin-top: 70px !important; margin-bottom: 40px !important; height: calc(100vh - 110px) !important; overflow: hidden; background-color: #0f172a; color: #e2e8f0; }
        
        /* Specific overrides for Tracer layout to prevent squishing */
        #tracer-layout-container { height: 100% !important; }
        .vis-network { outline: none; }
    `;
    document.head.appendChild(style);

    // 2. Inject Global Header
    const header = document.createElement('header');
    header.id = 'global-nav';
    header.innerHTML = `
        <a href="/landing.html" class="global-nav-brand">
            <img src="/logo_nemesis.jpeg" alt="NEMESIS Logo">
            <span>NEMESIS</span>
        </a>
        <nav class="global-nav-links">
            <a href="/landing.html" class="${isLanding ? 'active' : ''}"><i class="fa-solid fa-house"></i> Home</a>
            <a href="/tracer.html" class="${isTracer ? 'active' : ''}"><i class="fa-solid fa-project-diagram"></i> Tracer</a>
            <a href="/nemesis_id.html" class="${isID ? 'active' : ''}"><i class="fa-solid fa-id-card-clip"></i> Nemesis ID</a>
            <a href="/darknet_portal.html" class="${path.includes('darknet_portal.html') ? 'active' : ''}"><i class="fa-solid fa-user-secret"></i> Darknet</a>
            <a href="/admin.html" class="${isAdmin ? 'active' : ''}"><i class="fa-solid fa-server"></i> Admin / C2</a>
            <a href="/audit_report.html" class="${isAudit ? 'active' : ''}"><i class="fa-solid fa-shield-halved"></i> Master Audit</a>
            <a href="/recovery_framework.html" class="${isFramework ? 'active' : ''}"><i class="fa-solid fa-scale-balanced"></i> Framework</a>
        </nav>
    `;
    document.body.prepend(header);

    // 3. Inject Global Footer
    const footer = document.createElement('footer');
    footer.id = 'global-footer';
    footer.innerHTML = `
        <div class="global-footer-status">
            <div class="status-dot"></div>
            SYSTEM ONLINE & SECURE
        </div>
        <div>
            &copy; 2026 LIONSGATE INTELLIGENCE NETWORK. All Rights Reserved.
        </div>
        <div>
            Version: OMEGA 5.0 | Build: 8841x
        </div>
    `;
    document.body.appendChild(footer);
    
    // 4. Remove local headers if they exist to prevent duplication
    const oldLandingNav = document.querySelector('.landing-nav');
    if (oldLandingNav) oldLandingNav.remove();
});
