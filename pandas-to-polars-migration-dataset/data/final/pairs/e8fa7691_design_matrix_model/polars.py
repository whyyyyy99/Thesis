        header_labels = design_matrix_df.select(pl.exclude("realization")).columns
        ...
        for row_dict in design_matrix_df.iter_rows(named=True):
            model.appendRow([
                QStandardItem(str(row_dict[col]))
                for col in design_matrix_df.select(pl.exclude("realization")).columns
            ])
        model.setVerticalHeaderLabels(
            design_matrix_df.get_column("realization").cast(pl.String).to_list()
        )
