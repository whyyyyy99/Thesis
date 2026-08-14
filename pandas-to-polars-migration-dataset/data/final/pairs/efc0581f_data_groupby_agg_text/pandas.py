import pandas as pd

        df_text_parent = (df_words_contained.groupby('parent')
                          .agg(x1=("x1", np.min),
                               x2=("x2", np.max),
                               y1=("y1", np.min),
                               y2=("y2", np.max),
                               value=("value", lambda x: ' '.join(x)))
                          .sort_values(by=["y1", "x1"]))
        return df_text_parent["value"].astype(str).str.cat(sep="\n").strip() or None
