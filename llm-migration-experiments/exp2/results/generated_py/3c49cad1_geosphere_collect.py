import json
import polars as pl

data = json.loads(response.read())
timestamps = data.pop("timestamps")
parameter_values = (
    pl.DataFrame(data["features"])
    .get_column("properties")
    .map_elements(lambda x: x["parameters"])
    .map_elements(_extract_parameter_values)
    .explode()
)
df = pl.DataFrame(parameter_values.to_list()).explode("value")
df = df.with_columns(pl.col("value").cast(float))
df = df.with_columns(
    pl.Series(
        Columns.DATE.value,
        list(timestamps for timestamps in timestamps for _ in range(len(parameter))),
    ).alias(Columns.DATE.value)
)
return df