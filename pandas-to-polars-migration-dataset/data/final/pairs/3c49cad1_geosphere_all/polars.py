        df = pl.read_csv(response).lazy()
        df = df.drop(columns=["Sonnenschein", "Globalstrahlung"])
        df = df.rename(mapping={...})
        return df.with_columns(
            pl.col(Columns.FROM_DATE.value).str.strptime(pl.Datetime),
            pl.col(Columns.TO_DATE.value).str.strptime(pl.Datetime),
        )
