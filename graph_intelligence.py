"""
Recursive Graph Intelligence
Calculates graph metrics like PageRank, Shortest Path, and Cross-Chain correlations.
"""
import networkx as nx
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GraphIntelligence:
    def __init__(self):
        self.G = nx.DiGraph()
        
    def build_graph_from_edges(self, edges: List[Dict[str, Any]]):
        """Builds a NetworkX graph from a list of edges."""
        self.G.clear()
        for edge in edges:
            u = edge.get("from")
            v = edge.get("to")
            amt = edge.get("amount", 0.0)
            if u and v:
                if self.G.has_edge(u, v):
                    self.G[u][v]['weight'] += amt
                else:
                    self.G.add_edge(u, v, weight=amt, **edge)
                    
    def compute_pagerank(self) -> Dict[str, float]:
        """
        Calculates the PageRank (influence) of each node in the network.
        Nodes that receive a lot of funds from highly active nodes get higher scores.
        """
        if len(self.G) == 0:
            return {}
        try:
            return nx.pagerank(self.G, weight='weight')
        except Exception as e:
            logger.error(f"PageRank computation failed: {e}")
            return {}
            
    def compute_shortest_paths(self, source: str) -> Dict[str, int]:
        """
        Finds the shortest path from the initial suspect wallet to all other nodes.
        Returns a mapping of {node_address: distance}.
        """
        if source not in self.G:
            return {}
        try:
            return nx.single_source_shortest_path_length(self.G, source)
        except Exception as e:
            logger.error(f"Shortest path computation failed: {e}")
            return {}
            
    def detect_cross_chain_correlations(self) -> List[Dict[str, Any]]:
        """
        Detects entities operating across multiple chains.
        In a full implementation, this analyzes bridges and matching deposit amounts.
        """
        correlations = []
        # Mock logic for demonstration: Identify addresses that appear on multiple chains
        chain_map = {}
        for u, v, data in self.G.edges(data=True):
            chain = data.get("chain")
            if chain:
                chain_map.setdefault(u, set()).add(chain)
                chain_map.setdefault(v, set()).add(chain)
                
        for node, chains in chain_map.items():
            if len(chains) > 1:
                correlations.append({
                    "entity": node,
                    "chains": list(chains),
                    "confidence": 0.95
                })
        return correlations
