        data_raw = json.loads(response.read())
        timestamps = data_raw.pop("timestamps")
        data = {Columns.DATE.value: timestamps}
        for par, par_dict in data_raw["features"][0]["properties"]["parameters"].items():
            data[par] = par_dict["data"]
        df = pl.DataFrame(data)
        df = df.melt(
            id_vars=[Columns.DATE.value], variable_name=Columns.PARAMETER.value, value_name=Columns.VALUE.value
        )
        return df.with_columns(
            pl.col(Columns.DATE.value)
            .str.strptime(pl.Datetime, fmt="%Y-%m-%dT%H:%M+%H:%M")
            .dt.replace_time_zone("UTC"),
        )
