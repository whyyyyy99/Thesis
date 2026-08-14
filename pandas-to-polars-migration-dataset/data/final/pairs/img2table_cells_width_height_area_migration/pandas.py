import pandas as pd

df_cells["width"] = df_cells["x2"] - df_cells["x1"]
df_cells["height"] = df_cells["y2"] - df_cells["y1"]
df_cells["area"] = df_cells["width"] * df_cells["height"]
