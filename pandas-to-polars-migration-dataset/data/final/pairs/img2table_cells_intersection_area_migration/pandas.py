import pandas as pd

df_cross_cells["int_area"] = (df_cross_cells["x_right"] - df_cross_cells["x_left"]) \n                             * (df_cross_cells["y_bottom"] - df_cross_cells["y_top"])
