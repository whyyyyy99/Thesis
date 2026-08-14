        with self.connect() as connection:
            query = text(query)
            results = connection.execute(query)
            columns = list(results.keys())
            data = results.fetchall()
            results.close()
        # Convert to dict of columns for Polars
        if data:
            data_dict = {col: [row[i] for row in data] for i, col in enumerate(columns)}
            return pl.DataFrame(data_dict)
        else:
            schema = {col: pl.String for col in columns}
            return pl.DataFrame({col: [] for col in columns}, schema=schema)
