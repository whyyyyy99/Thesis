import polars as pl

frame = pl.concat(data)
if drop_const_cols:
    first_row = frame.row(0, named=True)
    frame = frame.select([col for col in frame.columns if (frame[col] != first_row[col]).any()])
frame.write_csv(output_file)
