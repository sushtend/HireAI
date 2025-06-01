from typing import List, Dict

def rank_candidates(query: str, candidates: List[Dict]) -> List[Dict]:
    """
    Rank candidates based on their match to the search query.
    
    TODO: Implement proper ranking using:
    - sentence-transformers for skill vector comparison
    - RAG-style matching logic
    - Real embedding ranking (optional with Weaviate / Pinecone)
    
    Args:
        query (str): The original search query
        candidates (List[Dict]): List of candidate dictionaries from Supabase
        
    Returns:
        List[Dict]: Ranked list of candidates with rank_score added
    """
    # Placeholder for future RAG + embedding-based ranking
    # For now, return candidates in original order with dummy rank
    for i, c in enumerate(candidates):
        c["rank_score"] = 100 - i  # Dummy decreasing score
    return candidates 