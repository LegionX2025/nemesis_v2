import re

input_file = r"C:\Users\LEGIONX\Downloads\ultra\crypto.html"
output_file = r"C:\Users\LEGIONX\Downloads\nemesis\tracer_scripts\recovery_framework.html"

with open(input_file, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Inject missing sections into the main content
missing_sections = """
        <!-- ========================================== -->
        <!-- PHASE 2: EVIDENCE PRESERVATION             -->
        <!-- ========================================== -->
        <section id="phase-2" class="content-section">
            <div class="print-actions"><button class="btn-print" onclick="window.print()"><i class="ph-bold ph-printer"></i> Export PDF</button></div>
            <div class="legal-document">
                <div class="watermark">LIONSGATE</div>
                <h1>Phase 2: Evidence Preservation</h1>
                <p>Forensic preservation of all data elements required to establish legal standing and attribute malicious activity.</p>
                <h2>Required Protocols</h2>
                <ul>
                    <li>Capture full disk images or RAM captures using write-blockers.</li>
                    <li>Secure all phishing vectors: copy headers from malicious emails, archive rogue smart contracts.</li>
                    <li>Document IP addresses, device metadata, and browser history logs surrounding the event.</li>
                    <li>Generate SHA-256 hash signatures for all collected evidentiary files.</li>
                </ul>
            </div>
        </section>

        <!-- ========================================== -->
        <!-- PHASE 4: INTELLIGENCE COLLECTION           -->
        <!-- ========================================== -->
        <section id="phase-4" class="content-section">
            <div class="print-actions"><button class="btn-print" onclick="window.print()"><i class="ph-bold ph-printer"></i> Export PDF</button></div>
            <div class="legal-document">
                <div class="watermark">OSINT</div>
                <h1>Phase 4: Intelligence Collection</h1>
                <p>Augmenting blockchain ledger data with open-source and proprietary intelligence to contextualize the threat actors.</p>
                <h2>Deep Web & Darknet Scraping</h2>
                <p>Our OSINT module cross-references the targeted wallet addresses against darknet forums, illicit marketplaces, ransomware leak sites, and known exploit chatter to identify organizational affiliation.</p>
                <h2>C2 Server Mapping</h2>
                <p>If the incident involved malware (e.g., InfoStealers), we map the Command & Control (C2) infrastructure to identify hosting providers and overlapping attacks.</p>
            </div>
        </section>

        <!-- ========================================== -->
        <!-- PHASE 5: ENTITY ATTRIBUTION                -->
        <!-- ========================================== -->
        <section id="phase-5" class="content-section">
            <div class="print-actions"><button class="btn-print" onclick="window.print()"><i class="ph-bold ph-printer"></i> Export PDF</button></div>
            <div class="legal-document">
                <div class="watermark">ATTRIBUTION</div>
                <h1>Phase 5: Entity Attribution</h1>
                <p>The synthesis of blockchain heuristics and OSINT data to form a definitive or probabilistic identity profile.</p>
                <h2>Identity Synthesis</h2>
                <p>Once assets hit a centralized off-ramp, we associate the blockchain address cluster with real-world KYC profiles held by the VASP (Virtual Asset Service Provider).</p>
                <ul>
                    <li><strong>Direct Attribution:</strong> Actor deposits directly into a KYC'd exchange.</li>
                    <li><strong>Indirect Attribution:</strong> Actor pays for infrastructure using crypto, leading to subpoenaing the VPS provider.</li>
                </ul>
            </div>
        </section>

        <!-- ========================================== -->
        <!-- PHASE 6: LEGAL CASE BUILDING               -->
        <!-- ========================================== -->
        <section id="phase-6" class="content-section">
            <div class="print-actions"><button class="btn-print" onclick="window.print()"><i class="ph-bold ph-printer"></i> Export PDF</button></div>
            <div class="legal-document">
                <div class="watermark">LEGAL</div>
                <h1>Phase 6: Legal Case Building</h1>
                <p>Transforming technical forensics into admissible evidence for civil litigation or criminal prosecution.</p>
                <h2>Key Deliverables</h2>
                <ul>
                    <li>Drafting Expert Witness Declarations.</li>
                    <li>Compiling the Master Forensic Trace Report.</li>
                    <li>Preparing Chain of Custody logs for submission under the Federal Rules of Evidence (or regional equivalent).</li>
                </ul>
            </div>
        </section>

        <!-- ========================================== -->
        <!-- PHASE 7: REPORTING                         -->
        <!-- ========================================== -->
        <section id="phase-7" class="content-section">
            <div class="print-actions"><button class="btn-print" onclick="window.print()"><i class="ph-bold ph-printer"></i> Export PDF</button></div>
            <div class="legal-document">
                <div class="watermark">REPORTING</div>
                <h1>Phase 7: Reporting</h1>
                <p>Disseminating findings to stakeholders, law enforcement, and legal counsel.</p>
                <p>The reporting phase involves structuring complex cryptographic data flows into a narrative that judges, juries, and non-technical officers can easily digest. This involves deep use of data visualization (graphs) and clear executive summaries.</p>
            </div>
        </section>

        <!-- ========================================== -->
        <!-- PHASE 8: EXCHANGE NOTIFICATION             -->
        <!-- ========================================== -->
        <section id="phase-8" class="content-section">
            <div class="print-actions"><button class="btn-print" onclick="window.print()"><i class="ph-bold ph-printer"></i> Export PDF</button></div>
            <div class="legal-document">
                <div class="watermark">FREEZE</div>
                <h1>Phase 8: Exchange Notification</h1>
                <p>The critical race against time to halt the dissipation of assets.</p>
                <h2>Preservation Requests</h2>
                <p>Prior to obtaining a formal subpoena, investigators will file a Preservation Request (or "Freeze Notice") to the compliance department of the receiving exchange. This places the exchange on notice that they are hosting stolen funds, triggering their internal AML/CFT protocols.</p>
            </div>
        </section>

        <!-- ========================================== -->
        <!-- PHASE 9: CIVIL LITIGATION                  -->
        <!-- ========================================== -->
        <section id="phase-9" class="content-section">
            <div class="print-actions"><button class="btn-print" onclick="window.print()"><i class="ph-bold ph-printer"></i> Export PDF</button></div>
            <div class="legal-document">
                <div class="watermark">CIVIL COURT</div>
                <h1>Phase 9: Civil Litigation</h1>
                <p>Filing lawsuits to compel identity disclosure and recover damages.</p>
                <p>We work with retained counsel to file "John Doe" lawsuits. These allow victims to initiate legal proceedings against the unknown thieves, which then grants subpoena power to uncover their true identities from the exchanges.</p>
            </div>
        </section>

        <!-- ========================================== -->
        <!-- PHASE 10: CRIMINAL INVESTIGATION           -->
        <!-- ========================================== -->
        <section id="phase-10" class="content-section">
            <div class="print-actions"><button class="btn-print" onclick="window.print()"><i class="ph-bold ph-printer"></i> Export PDF</button></div>
            <div class="legal-document">
                <div class="watermark">CRIMINAL</div>
                <h1>Phase 10: Criminal Investigation</h1>
                <p>Collaborating with Law Enforcement Agencies (LEA) for prosecution.</p>
                <p>Lionsgate Network bridges the gap by handing LEA a "turnkey" case file. We provide the IC3 complaint, the traced flow of funds, and the exact VASP terminal deposits to dramatically accelerate the issuance of federal search warrants and MLAT requests.</p>
            </div>
        </section>

        <!-- ========================================== -->
        <!-- PHASE 11: COURT ORDERS                     -->
        <!-- ========================================== -->
        <section id="phase-11" class="content-section">
            <div class="print-actions"><button class="btn-print" onclick="window.print()"><i class="ph-bold ph-printer"></i> Export PDF</button></div>
            <div class="legal-document">
                <div class="watermark">SUBPOENA</div>
                <h1>Phase 11: Court Orders</h1>
                <p>Executing legal instruments to seize assets or unmask identities.</p>
                <h2>Primary Instruments</h2>
                <ul>
                    <li><strong>Norwich Pharmacal Order (NPO):</strong> Used heavily in the UK/Commonwealth to compel an innocent third party (the exchange) to disclose the identity of the wrongdoer.</li>
                    <li><strong>Subpoena Duces Tecum:</strong> US-based demand for KYC documents and IP logs.</li>
                    <li><strong>Ex Parte Freezing Injunctions:</strong> Orders obtained without notifying the thief, ensuring they cannot move the funds before the exchange locks the account.</li>
                </ul>
            </div>
        </section>

        <!-- ========================================== -->
        <!-- PHASE 12: ASSET RESTITUTION                -->
        <!-- ========================================== -->
        <section id="phase-12" class="content-section">
            <div class="print-actions"><button class="btn-print" onclick="window.print()"><i class="ph-bold ph-printer"></i> Export PDF</button></div>
            <div class="legal-document">
                <div class="watermark">RESTITUTION</div>
                <h1>Phase 12: Asset Restitution</h1>
                <p>The final repatriation of stolen assets back to the rightful owner.</p>
                <p>Once court orders are finalized and the exchange acknowledges the claim, funds are either transferred back to the victim's secure custody, or liquidated into fiat for wire transfer. This marks the formal closure of the investigation lifecycle.</p>
            </div>
        </section>

        <!-- ========================================== -->
        <!-- LEGAL TEMPLATE: INCIDENT REPORT            -->
        <!-- ========================================== -->
        <section id="doc-incident" class="content-section">
            <div class="print-actions"><button class="btn-print" onclick="window.print()"><i class="ph-bold ph-printer"></i> Export PDF</button></div>
            <div class="legal-document">
                <div class="watermark">TEMPLATE</div>
                <div style="text-align:right; font-family:'Inter', sans-serif; font-size:0.9rem; margin-bottom:40px;">
                    <strong>[DATE]</strong><br>
                    <strong>LIONSGATE INCIDENT RESPONSE</strong>
                </div>
                <h2>T-1: Initial Incident Report</h2>
                <table class="doc-table">
                    <tr><th>Field</th><th>Input</th></tr>
                    <tr><td>Victim Name</td><td>[Full Name]</td></tr>
                    <tr><td>Date of Compromise</td><td>[Date/Time UTC]</td></tr>
                    <tr><td>Assets Lost</td><td>[e.g., 50 ETH, 100,000 USDT]</td></tr>
                    <tr><td>Victim Seed Address</td><td>[Wallet Address]</td></tr>
                    <tr><td>Attacker Address</td><td>[Destination Address]</td></tr>
                    <tr><td>Tx Hash(es)</td><td>[Transaction IDs]</td></tr>
                </table>
                <h3>Incident Narrative</h3>
                <p>[Detailed chronological description of how the compromise occurred. E.g., The victim clicked a malicious link on Twitter, approving a malicious smart contract...]</p>
            </div>
        </section>

        <!-- ========================================== -->
        <!-- LEGAL TEMPLATE: CHAIN OF CUSTODY           -->
        <!-- ========================================== -->
        <section id="doc-custody" class="content-section">
            <div class="print-actions"><button class="btn-print" onclick="window.print()"><i class="ph-bold ph-printer"></i> Export PDF</button></div>
            <div class="legal-document">
                <div class="watermark">CUSTODY</div>
                <div style="text-align:right; font-family:'Inter', sans-serif; font-size:0.9rem; margin-bottom:40px;">
                    <strong>[DATE]</strong><br>
                    <strong>LIONSGATE FORENSICS</strong>
                </div>
                <h2>T-2: Chain of Custody Log</h2>
                <p>Maintained to ensure the integrity of digital evidence and ensure admissibility in federal court.</p>
                <table class="doc-table">
                    <tr><th>Item ID</th><th>Description</th><th>SHA-256 Hash</th><th>Acquired By</th><th>Date/Time</th></tr>
                    <tr><td>001</td><td>Raw Blockchain TX Export</td><td>[Hash String]</td><td>[Analyst Name]</td><td>[Date]</td></tr>
                    <tr><td>002</td><td>Victim Browser Cache</td><td>[Hash String]</td><td>[Analyst Name]</td><td>[Date]</td></tr>
                    <tr><td>003</td><td>Malicious Smart Contract ABI</td><td>[Hash String]</td><td>[Analyst Name]</td><td>[Date]</td></tr>
                </table>
            </div>
        </section>
"""

# Find the end of the main-content section and inject the missing sections
html = html.replace('</main>', missing_sections + '\n    </main>')

# 2. Inject global_nav.js script tag
if '<script src="/global_nav.js"></script>' not in html:
    html = html.replace('</body>', '    <script src="/global_nav.js"></script>\n</body>')

# 3. Adjust CSS for the global nav
# Since global_nav.js already injects a `<style>` that sets body { margin-top: 70px !important; }
# we just need to ensure the `#sidebar` respects it by changing its top: 0 to top: 70px
# The global nav is fixed at top: 0 with height 70px.
# We will inject a style tag right before </head>
css_overrides = """
    <style>
        /* NEMESIS Global Nav Overrides for standalone Framework page */
        body { 
            background-color: #0f172a !important; 
        }
        #sidebar {
            top: 70px !important;
            height: calc(100vh - 70px) !important;
            border-right: 1px solid rgba(51, 65, 85, 0.8) !important;
            background: rgba(15, 23, 42, 0.95) !important;
        }
        #sidebar .sidebar-header {
            background: rgba(15, 23, 42, 0.95) !important;
            border-bottom: 1px solid rgba(51, 65, 85, 0.8) !important;
        }
        #sidebar .sidebar-header div.text-center {
            color: #94a3b8 !important;
            border-top: 1px solid rgba(51, 65, 85, 0.8) !important;
        }
        #sidebar .nav-item {
            color: #94a3b8 !important;
        }
        #sidebar .nav-item:hover {
            background: rgba(51, 65, 85, 0.3) !important;
            color: #e2e8f0 !important;
        }
        #sidebar .nav-item.active {
            background: rgba(59, 130, 246, 0.1) !important;
            color: #60a5fa !important;
            border-left-color: #3b82f6 !important;
        }
        #main-content {
            margin-top: 20px !important; /* The body already has margin-top: 70px from global_nav, add some padding */
            background-color: #0f172a !important;
        }
    </style>
"""
html = html.replace('</head>', css_overrides + '\n</head>')

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html)

print("Framework migration complete.")
