import pandas as pd

        data = json.loads(response.read())
        timestamps = data.pop("timestamps")
        df = (
            pd.DataFrame(data["features"])
            .pop("properties")
            .map(lambda x: x["parameters"])
            .apply(_extract_parameter_values)
            .explode()
            .apply(pd.Series)
            .explode("value")
        )
        df.value = df.value.astype(float)
        df[Columns.DATE.value] = pd.to_datetime(pd.Series(timestamps).repeat(len(parameter)).values)
        return df
