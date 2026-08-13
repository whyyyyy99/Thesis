import json
import numpy as np
import polars as pl

data = json.loads(response.read())
timestamps = data.pop("timestamps")
features_df = pl.DataFrame(data["features"])
properties = features_df["properties"].to_list()
parameters = [x["parameters"] for x in properties]
exploded = []
for x in parameters:
    extracted = _extract_parameter_values(x)
    if isinstance(extracted, list):
        exploded.extend(extracted)
    else:
        exploded.append(extracted)

df = pl.DataFrame(exploded).explode("value")
df = df.with_columns(pl.col("value").cast(pl.Float64))

repeat_count = 0 if len(timestamps) == 0 else df.height // len(timestamps)
df = df.with_columns(
    pl.Series(
        Columns.DATE.value,
        np.repeat(timestamps, repeat_count).tolist(),
    ).cast(pl.Datetime, strict=False)
)

return df
