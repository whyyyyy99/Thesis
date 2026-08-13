import polars as pl
import polars.selectors as cs

df = pl.DataFrame({"class": classes, "y": y, "x": x}).with_columns(cs.numeric().round(3))
...
return wb.plot_table(
    "wandb/area-under-curve/v0", wb.Table(dataframe=df), fields=fields, string_fields=string_fields
)