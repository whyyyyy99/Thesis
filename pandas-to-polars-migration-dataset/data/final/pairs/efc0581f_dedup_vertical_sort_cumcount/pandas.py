import pandas as pd

    df_cells = df_cells.sort_values(by=["x1", "x2", "y1", "y2"])
    df_cells["cell_rk"] = df_cells.groupby(["x1", "x2", "y1"]).cumcount()
    df_cells = df_cells[df_cells["cell_rk"] == 0]
