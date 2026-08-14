import pandas as pd

df_cross_cells["contained"] = ((df_cross_cells["x_right"] >= df_cross_cells["x_left"])
                                   & (df_cross_cells["y_bottom"] >= df_cross_cells["y_top"])
                                   & (df_cross_cells["int_area"] / df_cross_cells["area"] >= 0.9))
