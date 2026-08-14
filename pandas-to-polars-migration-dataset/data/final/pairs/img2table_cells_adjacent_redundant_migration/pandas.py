import pandas as pd

condition_adjacent = (((df_cross_cells["overlapping_y"] > 5)
                       & (df_cross_cells["diff_x"] / df_cross_cells[["width", "width_"]].max(axis=1) <= 0.05))
                      | ((df_cross_cells["overlapping_x"] > 5)
                         & (df_cross_cells["diff_y"] / df_cross_cells[["height", "height_"]].max(axis=1) <= 0.05))
                      )
df_cross_cells["adjacent"] = condition_adjacent
df_cross_cells["redundant"] = df_cross_cells["contained"] & df_cross_cells["adjacent"]
