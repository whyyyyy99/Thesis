import pandas as pd

def compare_hybrid_scores(*hybrid_scores: HybridScore) -> pd.DataFrame:
    """
    Stacks the hybrid recommender scores for multiple query documents vertically in a
    DataFrame.
    """
    return pd.concat([hybrid_score.to_frame() for hybrid_score in hybrid_scores], ignore_index=True)
