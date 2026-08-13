import json
import pandas as pd
import polars as pl

data = json.loads(response.read())
timestamps = data.pop("timestamps")
df = pl.DataFrame(data["features"])
properties = df.drop_in_place("properties")
parameters = pl.Series([x["parameters"] for x in properties.to_list()])
parameter_values = [_extract_parameter_values(x) for x in parameters.to_list()]
df = pl.DataFrame(pl.Series(parameter_values).explode().to_list())
df = df.explode("value")
df = df.with_columns(pl.col("value").cast(pl.Float64))
df = df.with_columns(
    pl.Series(timestamps)
    .cast(pl.Utf8)
    .str.to_datetime(strict=False)
    .repeat_by(len(parameter))
    .explode()
    .alias(Columns.DATE.value)
)
return df
