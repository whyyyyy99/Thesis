import polars as pl

def compare_hybrid_scores(*hybrid_scores: HybridScore) -> pl.DataFrame:
    """
    Stacks the hybrid recommender scores for multiple query documents vertically in a
    DataFrame.
    """
    return pl.concat([hybrid_score.to_frame() for hybrid_score in hybrid_scores])
