        frame = polars.concat(data)
        columns_to_export = ["Realization", *cols_index, ..., "Pressure", ...]
        to_export = frame.select(columns_to_export)
        to_export.write_csv(output_file, include_header=True)
