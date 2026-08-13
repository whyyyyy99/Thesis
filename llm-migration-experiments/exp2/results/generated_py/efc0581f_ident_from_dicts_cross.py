import polars as pl
from typing import List

def get_cells_dataframe(horizontal_lines: List[Line], vertical_lines: List[Line]) -> pl.DataFrame:
    default_df = pl.DataFrame({"x1": [], "x2": [], "y1": [], "y2": [], "width": [], "height": []})
    df_h_lines = pl.DataFrame([l.dict for l in horizontal_lines]) if horizontal_lines else default_df.clone()
    df_v_lines = pl.DataFrame([l.dict for l in vertical_lines]) if vertical_lines else default_df.clone()

    df_h_lines_cp = df_h_lines.clone()
    df_h_lines_cp.columns = ["x1_", "x2_", "y1_", "y2_", "width_", "height_"]

    cross_h_lines = df_h_lines.join(df_h_lines_cp, how="cross")
    cross_h_lines = cross_h_lines.filter(pl.col("y1") < pl.col("y1_"))

    cross_h_lines = cross_h_lines.with_columns([
        ((pl.col("x1") - pl.col("x1_") / pl.col("width")).abs() <= 0.02).alias("l_corresponds"),
        ((pl.col("x2") - pl.col("x2_") / pl.col("width")).abs() <= 0.02).alias("r_corresponds"),
        (
            ((pl.col("x1") <= pl.col("x1_")) & (pl.col("x1_") <= pl.col("x2")))
            | ((pl.col("x1_") <= pl.col("x1")) & (pl.col("x1") <= pl.col("x2_")))
        ).alias("l_contained"),
        (
            ((pl.col("x1") <= pl.col("x2_")) & (pl.col("x2_") <= pl.col("x2")))
            | ((pl.col("x1_") <= pl.col("x2")) & (pl.col("x2") <= pl.col("x2_")))
        ).alias("r_contained"),
    ])

    matching_condition = ((pl.col("l_corresponds") | pl.col("l_contained")) & (pl.col("r_corresponds") | pl.col("r_contained")))
    cross_h_lines = cross_h_lines.filter(matching_condition)

    cross_h_lines = cross_h_lines.with_columns([
        pl.max_horizontal("x1", "x1_").alias("x1_bbox"),
        pl.min_horizontal("x2", "x2_").alias("x2_bbox"),
        pl.col("y1").alias("y1_bbox"),
        pl.col("y1_").alias("y2_bbox"),
    ])
    df_bbox = cross_h_lines.select(["x1_bbox", "y1_bbox", "x2_bbox", "y2_bbox"]).with_row_index("index")

    df_bbox = df_bbox.with_columns(
        pl.max_horizontal(
            (pl.col("x2_bbox") - pl.col("x1_bbox")) * 0.05,
            pl.lit(5.0),
        ).round().alias("h_margin")
    )

    df_bbox_v = df_bbox.join(df_v_lines, how="cross")

    horizontal_cond = (
        (pl.col("x1_bbox") - pl.col("h_margin") <= pl.col("x1"))
        & (pl.col("x2_bbox") + pl.col("h_margin") > pl.col("x1"))
    )
    df_bbox_v = df_bbox_v.filter(horizontal_cond)

    df_bbox_v = df_bbox_v.with_columns(
        (pl.min_horizontal("y2", "y2_bbox") - pl.max_horizontal("y1", "y1_bbox")).alias("overlapping")
    )
    df_bbox_v = df_bbox_v.filter((pl.col("overlapping") / (pl.col("y2_bbox") - pl.col("y1_bbox"))) >= 0.8)

    if df_bbox_v.is_empty():
        return pl.DataFrame({"index": [], "x1": [], "y1": [], "x2": [], "y2": []})

    df_bbox_delimiters = (
        df_bbox_v.group_by(["index", "x1_bbox", "x2_bbox", "y1_bbox", "y2_bbox"])
        .agg(pl.col("x1").sort().alias("x1_sorted"))
    )

    df_bbox_delimiters = df_bbox_delimiters.with_columns(
        pl.when(pl.col("x1_sorted").list.len() > 1)
        .then(
            pl.col("x1_sorted").map_elements(
                lambda x: list(zip(x, x[1:])) if x is not None and len(x) > 1 else None,
                return_dtype=pl.List(pl.Object),
            )
        )
        .otherwise(None)
        .alias("dels")
    )

    df_bbox_delimiters = df_bbox_delimiters.filter(pl.col("dels").is_not_null())

    try:
        if df_bbox_delimiters.is_empty():
            raise ValueError

        df_bbox_delimiters = df_bbox_delimiters.explode("dels")
        df_bbox_delimiters = df_bbox_delimiters.with_columns([
            pl.col("dels").list.get(0).alias("del1"),
            pl.col("dels").list.get(1).alias("del2"),
        ])

        df_bbox_delimiters = df_bbox_delimiters.with_columns([
            pl.col("del1").alias("x1_bbox"),
            pl.col("del2").alias("x2_bbox"),
        ])

        df_cells = df_bbox_delimiters.select(["x1_bbox", "y1_bbox", "x2_bbox", "y2_bbox"])
        df_cells.columns = ["x1", "y1", "x2", "y2"]

        return df_cells.with_row_index("index")
    except ValueError:
        return pl.DataFrame({"index": [], "x1": [], "y1": [], "x2": [], "y2": []})