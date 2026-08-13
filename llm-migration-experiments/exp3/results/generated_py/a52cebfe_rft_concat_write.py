import polars as pl

frame = pl.concat(data)
if drop_const_cols and frame.height > 0:
    first_row = frame.row(0, named=True)
    keep_cols = [
        col for col in frame.columns
        if frame.select((pl.col(col) != first_row[col]).any()).item()
    ]
    frame = frame.select(keep_cols)
frame.write_csv(output_file)
