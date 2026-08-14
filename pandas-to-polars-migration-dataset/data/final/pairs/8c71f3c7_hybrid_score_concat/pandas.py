import pandas as pd

    return pd.concat([hybrid_score.to_frame() for hybrid_score in hybrid_scores], ignore_index=True)
