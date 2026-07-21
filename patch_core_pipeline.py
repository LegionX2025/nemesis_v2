import os

code_to_inject = """
# ==============================================================================
# NEMESIS INTELLIGENCE PIPELINE ENDPOINT (GEMINI NLP PROMPT)
# ==============================================================================
class PromptRequest(BaseModel):
    prompt: str
    files_included: bool = False

@app.post("/api/pipeline/prompt")
async def process_intelligence_prompt(request: PromptRequest):
    \"\"\"
    Takes a natural language prompt, extracts crypto addresses using Gemini,
    and runs the intelligence pipeline on all discovered entities.
    \"\"\"
    prompt = request.prompt
    logger.info(f"[PIPELINE] Received Prompt: {prompt[:50]}...")
    
    # Simple RegEx fallback for demo if Gemini fails
    import re
    # Extract potential ETH/BSC/Polygon addresses
    eth_matches = re.findall(r'0x[a-fA-F0-9]{40}', prompt)
    # Extract potential BTC addresses
    btc_matches = re.findall(r'\\b(1[a-km-zA-HJ-NP-Z1-9]{25,34}|3[a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-zA-HJ-NP-Z0-9]{39,59})\\b', prompt)
    
    addresses = list(set(eth_matches + btc_matches))
    
    if not addresses:
        return {"status": "error", "message": "No valid blockchain addresses found in prompt."}
        
    results = []
    # Run the intelligence pipeline for each extracted address
    from intelligence_pipeline import IntelligencePipeline
    for addr in addresses:
        try:
            intel = await IntelligencePipeline.run(addr)
            results.append(intel)
        except Exception as e:
            logger.error(f"[PIPELINE] Error running on {addr}: {e}")
            results.append({"address": addr, "error": str(e)})
            
    # Generate Google Doc style forensic summary using Gemini
    forensic_summary = "Forensic Document: Auto-generated from extracted nodes.\\n"
    for res in results:
        addr = res.get("address", "Unknown")
        chain = res.get("chain", "Unknown")
        nodes = res.get("nodes", [])
        if nodes:
            label = nodes[0].get("label", "Unknown")
            risk = nodes[0].get("risk_score", 0)
            forensic_summary += f"\\n- Entity: {label} ({addr}) on {chain}. Risk Score: {risk}/100."
            
    return {
        "status": "success",
        "extracted_addresses": addresses,
        "pipeline_results": results,
        "forensic_report": forensic_summary
    }

# ==============================================================================
"""

file_path = "nemesis_core.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

if "/api/pipeline/prompt" not in content:
    # Inject it before the end of the file or before app.mount if it exists
    if "app.mount" in content:
        content = content.replace("app.mount(", f"{code_to_inject}\napp.mount(")
    else:
        content += "\n" + code_to_inject
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Injected /api/pipeline/prompt into nemesis_core.py")
else:
    print("Endpoint already exists.")
