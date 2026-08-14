import pandas as pd

    df_inter = (df_w_l.groupby(['line_id', 'length'])
                .agg(intersection=('intersection', np.sum))
                .reset_index())
    intersecting_lines = df_inter[df_inter['intersection'] / df_inter['length'] > 0.5]['line_id'].values.tolist()
