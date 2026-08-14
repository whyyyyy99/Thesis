import pandas as pd

        header_labels = design_matrix_df.columns.astype(str).tolist()
        for index, _ in design_matrix_df.iterrows():
            model.appendRow([
                QStandardItem(str(design_matrix_df.at[index, col]))
                for col in design_matrix_df.columns
            ])
        model.setVerticalHeaderLabels(design_matrix_df.index.astype(str).tolist())
