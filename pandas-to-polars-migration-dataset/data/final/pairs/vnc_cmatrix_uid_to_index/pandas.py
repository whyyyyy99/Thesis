import pandas as pd

                row_indices.append(lookup.loc[lookup["uid"] == id_].row_index.values[0])
                column_indices.append(
                    lookup.loc[lookup["uid"] == id_].column_index.values[0]
                )
        row_indices = [i for i in row_indices if not pd.isna(i)]
        column_indices = [i for i in column_indices if not pd.isna(i)]
