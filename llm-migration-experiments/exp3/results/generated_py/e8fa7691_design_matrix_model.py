import polars as pl

header_labels = [str(col) for col in design_matrix_df.columns]
for row in design_matrix_df.iter_rows():
    model.appendRow([
        QStandardItem(str(value))
        for value in row
    ])
model.setVerticalHeaderLabels([str(i) for i in range(design_matrix_df.height)])
