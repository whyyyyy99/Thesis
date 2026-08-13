import polars as pl

return pl.concat([hybrid_score.to_frame() for hybrid_score in hybrid_scores])