import pandas as pd

df_w_l['intersection'] = (df_w_l['vertical'].astype(int) * vert_int
                              + (1 - df_w_l['vertical'].astype(int)) * hor_int)
