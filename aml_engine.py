import logging
from heuristics_engine import HeuristicsEngine

logger = logging.getLogger("AML_ENGINE")

class AMLEngine:
    def __init__(self):
        self.heuristics = HeuristicsEngine()
        
    def evaluate_risk(self, target_node_id: str, incoming_edges: list, outgoing_edges: list, osint_score: int = 0) -> dict:
        """
        Evaluates the Anti-Money Laundering (AML) risk of a node.
        Combines behavioral heuristics with external OSINT scores to generate a 0-100 index.
        """
        base_risk = 5  # Every active address has a tiny base risk
        
        # 1. Run Behavioral Heuristics
        heuristics_result = self.heuristics.analyze_node(target_node_id, incoming_edges, outgoing_edges)
        
        # 2. Combine Scores
        # Max score is 100
        calculated_risk = base_risk + heuristics_result["risk_modifier"] + osint_score
        final_risk = min(calculated_risk, 100)
        
        # 3. Determine Risk Classification
        if final_risk >= 80:
            classification = "CRITICAL (High Probability of Illicit Activity)"
            color_code = "RED"
        elif final_risk >= 50:
            classification = "ELEVATED (Suspicious Patterns Detected)"
            color_code = "ORANGE"
        elif final_risk >= 20:
            classification = "MODERATE (Minor Anomalies)"
            color_code = "YELLOW"
        else:
            classification = "LOW (Standard Behavior)"
            color_code = "GREEN"
            
        return {
            "node_id": target_node_id,
            "risk_score": final_risk,
            "classification": classification,
            "color": color_code,
            "heuristic_flags": heuristics_result["flags"],
            "analyzed_tx_count": len(incoming_edges) + len(outgoing_edges)
        }
