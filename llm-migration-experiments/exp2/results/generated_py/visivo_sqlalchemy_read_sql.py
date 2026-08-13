import polars as pl

with self.connect() as connection:
    query = text(query)
    results = connection.execute(query)
    columns = results.keys()
    data = results.fetchall()
    results.close()

return pl.DataFrame(data, schema=list(columns))