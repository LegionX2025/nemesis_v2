import logging

logger = logging.getLogger("HEURISTICS")

class HeuristicsEngine:
    def __init__(self):
        # Known Mixer & Privacy Protocol Addresses (Hardcoded for demonstration, ideally from DB)
        self.known_mixers = {
            "0xd90e2f925da726b50c4ed8d0fb90ad053324f31b": "Tornado Cash 100 ETH",
            "0x910cbd523d972eb0a6f4cae4618ad62622b39dbf": "Tornado Cash 10 ETH",
            "0x47ce0c6ed5b0ce3d3a51fdb1c52dc66a7c3c2936": "Tornado Cash 1 ETH",
            "0x12d66f87a04a9e220743712ce6d9bb1b5616b8fc": "Tornado Cash 0.1 ETH"
        }
        
    def analyze_node(self, target_node_id: str, incoming_edges: list, outgoing_edges: list) -> dict:
        """
        Analyzes a single node and its immediate transaction edges to detect suspicious patterns.
        Returns a dictionary of flagged behaviors.
        """
        flags = []
        confidence_modifiers = 0
        
        # 1. Mixer Interaction Detection
        for edge in incoming_edges + outgoing_edges:
            if edge.source in self.known_mixers or edge.target in self.known_mixers:
                mixer_name = self.known_mixers.get(edge.source) or self.known_mixers.get(edge.target)
                flags.append(f"Direct Interaction with {mixer_name}")
                confidence_modifiers += 40

        # 2. Peeling Chain Detection
        # A node in a peeling chain usually has 1 large incoming TX and exactly 2 outgoing TXs
        # (1 small drop to a new address, 1 large return to change address).
        if len(incoming_edges) == 1 and len(outgoing_edges) == 2:
            in_val = incoming_edges[0].value
            out_vals = [e.value for e in outgoing_edges]
            if max(out_vals) > (in_val * 0.7) and min(out_vals) < (in_val * 0.2):
                flags.append("Potential Peeling Chain Intermediate Node")
                confidence_modifiers += 25

        # 3. Smurfing / Structuring Detection
        # Multiple small incoming transactions right below a reporting threshold, followed by aggregation
        if len(incoming_edges) > 5:
            avg_in = sum(e.value for e in incoming_edges) / len(incoming_edges)
            # Threshold logic (e.g. consistently receiving exactly ~9.9k equivalent, mocked here)
            if all(0.5 < e.value < 1.5 for e in incoming_edges): # E.g. consistent ~1 ETH drops
                flags.append("High-Frequency Structured Deposits (Smurfing)")
                confidence_modifiers += 30

        # 4. Rapid Pass-Through (Wash Node)
        # Funds received and sent within a very short timeframe
        if incoming_edges and outgoing_edges:
            # We assume edges have 'timestamp' property
            in_times = [getattr(e, 'timestamp', 0) for e in incoming_edges if getattr(e, 'timestamp', 0) > 0]
            out_times = [getattr(e, 'timestamp', 0) for e in outgoing_edges if getattr(e, 'timestamp', 0) > 0]
            if in_times and out_times:
                min_diff = min(abs(ot - it) for ot in out_times for it in in_times)
                if min_diff < 300: # Less than 5 minutes
                    flags.append("Rapid Pass-Through Node (Wash Trading / Chaining)")
                    confidence_modifiers += 15

        return {
            "node_id": target_node_id,
            "flags": flags,
            "risk_modifier": min(confidence_modifiers, 100),
            "is_suspicious": len(flags) > 0
        }
