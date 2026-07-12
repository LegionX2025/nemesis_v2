import asyncio
from typing import Dict, Any, List
from gbio_ontology import GBIONode, GBIOEdge, EntityClass, TransferAction
from protocol_registries import identify_entity
from bitquery_collectors import run_all_collectors
import google.generativeai as genai
import os

class EntityResolutionEngine:
    @staticmethod
    def resolve(edges: List[GBIOEdge], existing_nodes: Dict[str, Any] = None) -> Dict[str, Any]:
        from gbio_ontology import BlockchainNetwork
        nodes = existing_nodes or {}
        for edge in edges:
            for addr in [edge.source_node_id, edge.target_node_id]:
                # In cross-chain scenarios, target might be DEX_POOL or similar abstractions
                if addr == "DEX_POOL":
                    if addr not in nodes:
                        nodes[addr] = {"id": addr, "entity_class": "DEFI_PROTOCOL", "properties": {"name": "Liquidity Pool"}, "risk_score": 0}
                    continue

                if addr not in nodes:
                    node = {"id": addr, "entity_class": "EOA_WALLET", "properties": {}, "risk_score": 0}
                    entity_info = identify_entity(addr)
                    if entity_info:
                        node["entity_class"] = entity_info.get("entity_class", "EOA_WALLET")
                        node["risk_score"] = entity_info.get("risk_score", 0)
                        node["properties"]["name"] = entity_info.get("name", "")
                        node["properties"]["category"] = entity_info.get("category", "")
                        node["properties"]["tags"] = entity_info.get("tags", [])
                    nodes[addr] = node
        return nodes

class RiskEngine:
    @staticmethod
    def score_graph(nodes: Dict[str, Any], edges: List[GBIOEdge]):
        for edge in edges:
            source_node = nodes.get(edge.source_node_id)
            target_node = nodes.get(edge.target_node_id)
            if source_node and target_node:
                # Basic graph centrality/exposure calculation
                if target_node.get("entity_class") in ["MIXER_ROUTER", "EntityClass.MIXER_ROUTER"]:
                    source_node["risk_score"] = source_node.get("risk_score", 0) + target_node.get("risk_score", 0) * 0.5
                    edge.risk_score = 90.0
                if target_node.get("entity_class") in ["BRIDGE_ENDPOINT", "EntityClass.BRIDGE_ENDPOINT"]:
                    # Bridging carries inherent risk of obfuscation
                    edge.risk_score = max(edge.risk_score, 40.0)

class TemporalAnalysis:
    @staticmethod
    def analyze(edges: List[GBIOEdge]) -> List[GBIOEdge]:
        # Sort edges by timestamp if available
        return edges

class AIInvestigationLayer:
    @staticmethod
    async def analyze(target: str, nodes: Dict[str, GBIONode], edges: List[GBIOEdge]) -> Dict[str, Any]:
        api_keys_str = os.environ.get("GEMINI_API_KEYS", "")
        keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]
        if not keys:
            return {"summary": "AI disabled. Missing GEMINI_API_KEYS."}
        
        graph_summary = f"Target: {target}\n"
        for edge in edges[:50]:
            s_node = nodes[edge.source_node_id]
            t_node = nodes[edge.target_node_id]
            s_name = s_node.get("properties", {}).get("name", edge.source_node_id)
            t_name = t_node.get("properties", {}).get("name", edge.target_node_id)
            amount = str(edge.amount_native)
            curr = edge.asset_symbol
            s_class = s_node.get("entity_class", "UNKNOWN")
            t_class = t_node.get("entity_class", "UNKNOWN")
            if amount:
                graph_summary += f"{s_name} ({s_class}) --[{edge.action.value} {amount} {curr}]--> {t_name} ({t_class})\n"
            else:
                graph_summary += f"{s_name} ({s_class}) --[{edge.action.value}]--> {t_name} ({t_class})\n"
            
        prompt = f"""
        You are an elite blockchain forensic investigator. Analyze the following Omni-Directional Knowledge Graph traversal for {target}.
        This graph includes advanced cross-chain asset movements, DEX swaps, and Bridge interactions.
        
        Provide a chronological narrative of the asset movement, obfuscation techniques used, and overall AML risk. 
        Focus on entities like Exchanges, Mixers, and Bridges. Output your response as plain text or markdown.
        
        Graph Traversal:
        {graph_summary}
        """
        last_error = ""
        for key in keys:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = await asyncio.to_thread(model.generate_content, prompt)
                return {"summary": response.text}
            except Exception as e:
                last_error = str(e)
                if "429" in last_error or "quota" in last_error.lower():
                    continue # Rotate to next key
                else:
                    break # Other errors like invalid key format might break, but let's try next key anyway just in case
                    
        return {"summary": f"AI analysis failed across all {len(keys)} keys. Last Error: {last_error}"}

class IntelligencePipeline:
    @staticmethod
    async def run(target_address: str, initial_chain: str = "Ethereum", max_depth: int = 2) -> Dict[str, Any]:
        print(f"--- NEMESIS OMEGA: KNOWLEDGE GRAPH INIT ({target_address}) ---")
        
        all_edges = []
        visited_nodes = set()
        queue = [(target_address, initial_chain, 0)]
        
        import aiohttp
        async with aiohttp.ClientSession() as session:
            # Cross-Chain Spawning loop
            while queue:
                current_addr, current_chain, depth = queue.pop(0)
                if depth >= max_depth or current_addr in visited_nodes:
                    continue
                    
                visited_nodes.add(current_addr)
                print(f"[Depth {depth}] Spawning Multi-Chain Collectors for {current_addr} on {current_chain}")
                
                raw_edges = await run_all_collectors(session, current_addr, current_chain)
                all_edges.extend(raw_edges)
                
                # Follow the asset: If it was bridged or swapped, queue the destination
                for edge in raw_edges:
                    if edge.action == TransferAction.BRIDGED_TO:
                        # In a real implementation, we extract the destination chain/address from Bitquery Event Logs
                        # For this PoC architecture, we queue the bridge contract itself or a simulated destination
                        target = edge.target_node_id
                        if target not in visited_nodes:
                            print(f"  -> Cross-Chain recursion detected. Spawning tracker for bridge: {target}")
                            queue.append((target, "Arbitrum", depth + 1))  # Example multi-chain hop

        print("\n[Ontology Translation & Entity Resolution]")
        nodes_map = EntityResolutionEngine.resolve(all_edges)
        
        print("[Risk Engine Scoring]")
        RiskEngine.score_graph(nodes_map, all_edges)
        
        print("[Temporal Analysis]")
        ordered_edges = TemporalAnalysis.analyze(all_edges)
        
        print("[AI Investigation Layer]")
        ai_report = await AIInvestigationLayer.analyze(target_address, nodes_map, ordered_edges)
        
        print(f"--- NEMESIS OMEGA: ANALYSIS COMPLETE ---")
        return {
            "target": target_address,
            "chain": initial_chain,
            "nodes": [n for n in nodes_map.values()],
            "edges": [e.dict() if hasattr(e, "dict") else e.model_dump() if hasattr(e, "model_dump") else e.__dict__ for e in ordered_edges],
            "investigation": ai_report
        }

if __name__ == "__main__":
    async def test():
        res = await IntelligencePipeline.run("0xd90e2f925DA726b50C4Ed8D0Fb90Ad053324F31b")
        print(res["investigation"]["summary"])
    asyncio.run(test())
