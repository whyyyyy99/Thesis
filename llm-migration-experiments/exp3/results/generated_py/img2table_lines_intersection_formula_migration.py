import polars as pl

vert_int = (
    ((df_w_l["x1_line"] > df_w_l["x1"]) & (df_w_l["x1_line"] < df_w_l["x2"])).cast(pl.Int64)
    * (
        pl.min_horizontal(df_w_l["y2"], df_w_l["y2_line"])
        - pl.max_horizontal(df_w_l["y1"], df_w_l["y1_line"])
    ).clip(lower_bound=0)
)

hor_int = (
    ((df_w_l["y1_line"] > df_w_l["y1"]) & (df_w_l["y1_line"] < df_w_l["y2"])).cast(pl.Int64)
    * (
        pl.min_horizontal(df_w_l["x2"], df_w_l["x2_line"])
        - pl.max_horizontal(df_w_l["x1"], df_w_l["x1_line"])
    ).clip(lower_bound=0)
)
