import re

path = 'report_template.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace watermark
watermark_css = '''
        .watermark { position: fixed; top: 30%; left: 15%; opacity: 0.1; z-index: -1; transform: rotate(-20deg); width: 70%; text-align: center; }
        .watermark img { max-width: 100%; height: auto; }
'''
if '.watermark {' in html:
    html = re.sub(r'\.watermark \{.*?\}', watermark_css, html, flags=re.DOTALL)
else:
    html = html.replace('</style>', watermark_css + '\n</style>')

if '<div class="watermark">' in html:
    html = re.sub(r'<div class="watermark">.*?</div>', '<div class="watermark"><img src="/logo_nemesis.jpeg" alt="LIONSGATE"></div>', html, flags=re.DOTALL)
else:
    html = html.replace('<body>', '<body>\n    <div class="watermark"><img src="/logo_nemesis.jpeg" alt="LIONSGATE"></div>')

# Rewrite nav section
nav_html = '''
        <nav class="flex flex-col gap-3 text-sm font-bold overflow-y-auto max-h-[70vh] pb-8 pr-2 custom-scrollbar">
            <button onclick="window.print()" class="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded shadow-md transition flex justify-center items-center gap-2 sticky top-0 z-10">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path></svg>
                Print to PDF / Save
            </button>
            <div class="border-t border-slate-200 my-2"></div>
            <a href="#section-1" class="text-slate-600 hover:text-blue-600 transition">1. Introduction - Incident</a>
            <a href="#section-2" class="text-slate-600 hover:text-blue-600 transition">2. Executive Summary</a>
            <a href="#section-3" class="text-slate-600 hover:text-blue-600 transition">3. Incident Details</a>
            <a href="#section-4" class="text-slate-600 hover:text-blue-600 transition">4. Investigation Methodology</a>
            <a href="#section-5" class="text-slate-600 hover:text-blue-600 transition">5. Chronological Fund Flow</a>
            <a href="#section-6" class="text-slate-600 hover:text-blue-600 transition">6. Timeline of Events</a>
            <a href="#section-7" class="text-slate-600 hover:text-blue-600 transition">7. Findings</a>
            <a href="#section-8" class="text-slate-600 hover:text-blue-600 transition">8. Conclusion & Recommendations</a>
            <a href="#section-9" class="text-slate-600 hover:text-blue-600 transition">9. Purpose and Scope</a>
            <a href="#section-10" class="text-slate-600 hover:text-blue-600 transition">10. Data Sources</a>
            <a href="#section-11" class="text-slate-600 hover:text-blue-600 transition">11. Transaction Analysis & Patterns</a>
            <a href="#section-12" class="text-slate-600 hover:text-blue-600 transition">12. Source and Destination Entities</a>
            <a href="#section-13" class="text-slate-600 hover:text-blue-600 transition">13. Blockchain Snapshot Transaction Graph</a>
            <a href="#section-14" class="text-slate-600 hover:text-blue-600 transition">14. Investigation Summary and Conclusion</a>
            <a href="#section-15" class="text-slate-600 hover:text-blue-600 transition">15. Glossary of Cryptocurrency Terms</a>
            <a href="#section-16" class="text-slate-600 hover:text-blue-600 transition">16. Crypto Victims Guidelines (By Zip Code)</a>
            <a href="#section-17" class="text-slate-600 hover:text-blue-600 transition">17. Disclaimer & Scope of Services</a>
        </nav>
'''
html = re.sub(r'<nav.*?>.*?</nav>', nav_html.strip(), html, flags=re.DOTALL)

# Rewrite TOC
toc_html = '''
            <div class="text-sm text-slate-700 mb-8 space-y-1 font-mono">
                <p>1. Introduction - Incident</p>
                <p>2. Executive Summary</p>
                <p class="pl-4">- Recovery Probability Percentage</p>
                <p class="pl-4">- Identified CEX Terminals and Amounts</p>
                <p>3. Incident Details</p>
                <p>4. Investigation Methodology</p>
                <p>5. Chronological Fund Flow</p>
                <p>6. Timeline of Events</p>
                <p>7. Findings</p>
                <p>8. Conclusion & Recommendations</p>
                <p>9. Purpose and Scope</p>
                <p>10. Data Sources</p>
                <p>11. Transaction Analysis & Patterns</p>
                <p>12. Source and Destination Entities</p>
                <p>13. Blockchain Snapshot Transaction Graph</p>
                <p>14. Investigation Summary and Conclusion</p>
                <p>15. Glossary of Cryptocurrency Terms</p>
                <p>16. Crypto Victims Guidelines (By Zip Code)</p>
                <p>17. Disclaimer & Scope of Services</p>
            </div>
'''
html = re.sub(r'<div class="text-sm text-slate-700 mb-8 space-y-1 font-mono">.*?</div>', toc_html.strip(), html, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Applied TOC and Watermark to report_template.html')
