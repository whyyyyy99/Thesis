import pandas as pd

redundant_cells = df_cross_cells[df_cross_cells["redundant"]]['index_'].drop_duplicates().values.tolist()
df_final_cells = df_cells.drop(labels=redundant_cells)
