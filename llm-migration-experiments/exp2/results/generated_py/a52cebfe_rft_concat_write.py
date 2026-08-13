import polars as pl

frame = pl.concat(data)
index_cols = ["Realization", "Well", "Ensemble", "Iteration"]
frame = frame.select(index_cols + [c for c in frame.columns if c not in index_cols])
if drop_const_cols:
    first_row = frame.row(0)
    data_cols = frame.columns[len(index_cols):]
    keep_cols = index_cols + [
        c
        for c, v in zip(data_cols, first_row[len(index_cols):])
        if frame.get_column(c).ne(v).fill_null(True).any()
    ]
    frame = frame.select(keep_cols)
frame.write_csv(output_file)