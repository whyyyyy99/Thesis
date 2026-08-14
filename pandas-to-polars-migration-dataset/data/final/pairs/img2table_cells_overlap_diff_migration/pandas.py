import pandas as pd

df_cross_cells["overlapping_x"] = df_cross_cells["x_right"] - df_cross_cells["x_left"]
df_cross_cells["overlapping_y"] = df_cross_cells["y_bottom"] - df_cross_cells["y_top"]
df_cross_cells["diff_x"] = pd.concat([(df_cross_cells["x2"] - df_cross_cells["x1_"]).abs(),
                                      (df_cross_cells["x1"] - df_cross_cells["x2_"]).abs(),
                                      (df_cross_cells["x1"] - df_cross_cells["x1_"]).abs(),
                                      (df_cross_cells["x2"] - df_cross_cells["x2_"]).abs()],
                                     axis=1).min(axis=1)
df_cross_cells["diff_y"] = pd.concat([(df_cross_cells["y1"] - df_cross_cells["y1_"]).abs(),
                                      (df_cross_cells["y2"] - df_cross_cells["y1_"]).abs(),
                                      (df_cross_cells["y1"] - df_cross_cells["y2_"]).abs(),
                                      (df_cross_cells["y2"] - df_cross_cells["y2_"]).abs()],
                                     axis=1).min(axis=1)
