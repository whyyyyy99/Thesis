                row_indices.append(lookup.filter(uid=id_)[0, "row_index"])
                column_indices.append(lookup.filter(uid=id_)[0, "column_index"])
        row_indices = [i for i in row_indices if i is not None]
        column_indices = [i for i in column_indices if i is not None]
