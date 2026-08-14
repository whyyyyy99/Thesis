import pandas as pd

intersecting_lines = df_inter[df_inter['intersection'] / df_inter['length'] > 0.5]['line_id'].values.tolist()
