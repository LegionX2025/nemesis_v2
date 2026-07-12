import re

with open('nemesis_core.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add import
if 'from intelligence_pipeline import IntelligencePipeline' not in code:
    code = code.replace(
        'import google.generativeai as genai\n', 
        'import google.generativeai as genai\nfrom intelligence_pipeline import IntelligencePipeline\n'
    )

# 2. Replace /api/node/graph
graph_pattern = re.compile(r'@app\.get\("/api/node/graph"\)\nasync def node_graph\(address: str\):.*?(?=@app\.get)', re.DOTALL)
new_graph = """@app.get("/api/node/graph")
async def node_graph(address: str):
    try:
        addresses = [a.strip() for a in address.split(",") if a.strip()]
        if not addresses: return {"real_transactions": []}
        
        # NEMESIS OMEGA: Route through the new Intelligence Pipeline Bitquery Plugin
        # We run the pipeline for the primary address
        pipeline_result = await IntelligencePipeline.run(addresses[0])
        
        # Translate GBIO edges back to legacy format for frontend compatibility during transition
        raw_txs = []
        for edge in pipeline_result.get("edges", []):
            raw_txs.append({
                "tx": {
                    "hash": edge.get("properties", {}).get("tx_hash", "0x0"),
                    "from": edge.get("source", ""),
                    "to": edge.get("target", ""),
                    "value": edge.get("properties", {}).get("amount", "0"),
                    "from_cex": pipeline_result["nodes"][0].get("properties", {}).get("name", "") if edge.get("source") == addresses[0] else "",
                    "to_cex": pipeline_result["nodes"][0].get("properties", {}).get("name", "") if edge.get("target") == addresses[0] else "",
                    "timeStamp": "0"
                }
            })
            
        return {"real_transactions": raw_txs, "omega_pipeline": pipeline_result}
    except Exception as e:
        logger.error(f"/api/node/graph failed: {e}")
        return {"real_transactions": []}

"""

code = graph_pattern.sub(new_graph, code)

# 3. Replace /api/node_intelligence
intel_pattern = re.compile(r'@app\.get\("/api/node_intelligence"\)\nasync def node_intelligence\(address: str\):.*?(?=@app\.get)', re.DOTALL)
new_intel = """@app.get("/api/node_intelligence")
async def node_intelligence(address: str):
    \"\"\"
    Returns the comprehensive 6-Tab intelligence payload dynamically generated via Deepmind AI and Live OSINT.
    NEMESIS OMEGA: Now routed through the full 9-step Intelligence Pipeline.
    \"\"\"
    try:
        pipeline_result = await IntelligencePipeline.run(address)
        return {
            "status": "success",
            "header": {
                "nemesis_id": f"NEM-{address[:6].upper()}-OMEGA",
                "primary_entity": pipeline_result["nodes"][0].get("properties", {}).get("name", "Unknown"),
                "chain": pipeline_result.get("chain", "Ethereum")
            },
            "omega_pipeline": pipeline_result
        }
    except Exception as e:
        logger.error(f"/api/node_intelligence failed: {e}")
        return {"status": "error", "message": str(e)}

"""
code = intel_pattern.sub(new_intel, code)

with open('nemesis_core.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("nemesis_core.py successfully patched to route via IntelligencePipeline.")
