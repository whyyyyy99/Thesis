import polars as pl  # scope for faster 'import ultralytics'

df = pl.DataFrame({"class": classes, "y": y, "x": x}).with_columns(
    pl.col(["y", "x"]).round(3)
)
...
return wb.plot_table(
    "wandb/area-under-curve/v0", wb.Table(dataframe=df), fields=fields, string_fields=string_fields
)
