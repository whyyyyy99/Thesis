import pandas as pd

    df_cross_cells = df_cells.reset_index().merge(df_cells_cp, how='cross')
    df_cross_cells = df_cross_cells[df_cross_cells["index"] != df_cross_cells["index_"]]
    df_cross_cells = df_cross_cells[df_cross_cells["area"] <= df_cross_cells["area_"]]
