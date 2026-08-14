import pandas as pd

vert_int = (
        ((df_w_l['x1_line'] > df_w_l['x1']) & (df_w_l['x1_line'] < df_w_l['x2'])).astype(int)
        * (df_w_l[['y2', 'y2_line']].min(axis=1) - df_w_l[['y1', 'y1_line']].max(axis=1)).clip(0, None)
    )
hor_int = (
        ((df_w_l['y1_line'] > df_w_l['y1']) & (df_w_l['y1_line'] < df_w_l['y2'])).astype(int)
        * (df_w_l[['x2', 'x2_line']].min(axis=1) - df_w_l[['x1', 'x1_line']].max(axis=1)).clip(0, None)
    )
