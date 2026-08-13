import polars as pl

redundant_cells = (
    df_cross_cells.filter(pl.col("redundant"))
    .get_column("index_")
    .unique(maintain_order=True)
    .to_list()
)
df_final_cells = df_cells.filter(~pl.col("index_").is_in(redundant_cells))
