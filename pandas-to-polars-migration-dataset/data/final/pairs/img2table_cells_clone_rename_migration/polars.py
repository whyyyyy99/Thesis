df_cells_cp = (df_cells.clone()
                   .rename({col: f"{col}_" for col in df_cells.columns})
                   )
