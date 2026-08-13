import polars as pl
import numpy as np

df_words = self.df.filter(pl.col("class") == "ocrx_word")
if page_number:
    df_words = df_words.filter(pl.col("page") == page_number)
df_words = df_words.filter(pl.col("value").is_not_null() & (pl.col("confidence") >= min_confidence))

list_cells = [
    {"row": id_row, "col": id_col, "x1_w": cell.x1, "x2_w": cell.x2, "y1_w": cell.y1, "y2_w": cell.y2}
    for id_row, row in enumerate(table.items)
    for id_col, cell in enumerate(row.items)
]
df_cells = pl.DataFrame(list_cells)

df_word_cells = df_words.join(df_cells, how="cross")

df_word_cells = df_word_cells.with_columns(
    x_left=pl.max_horizontal("x1", "x1_w"),
    y_top=pl.max_horizontal("y1", "y1_w"),
    x_right=pl.min_horizontal("x2", "x2_w"),
    y_bottom=pl.min_horizontal("y2", "y2_w"),
)

df_word_cells = df_word_cells.filter(
    (pl.col("x_right") > pl.col("x_left")) & (pl.col("y_bottom") > pl.col("y_top"))
)

df_text_parent = (
    df_word_cells
    .sort(["row", "col", "y1", "x1"])
    .group_by(["row", "col", "parent"], maintain_order=False)
    .agg(pl.col("value").implode().list.join(" ").alias("value"))
    .sort(["row", "col", "parent"])
    .group_by(["row", "col"], maintain_order=False)
    .agg(pl.col("value").implode().list.join("\n").alias("text"))
    .with_columns(pl.when(pl.col("text") == "").then(None).otherwise(pl.col("text")).alias("text"))
    .select(["row", "col", "text"])
)
