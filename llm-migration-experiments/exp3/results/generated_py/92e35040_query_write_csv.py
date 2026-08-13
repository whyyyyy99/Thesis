import polars as pl

first = True
for binned, unbinned in outputs:
    binned.write_csv(binned_path, separator="\t", include_header=first)
    unbinned.write_csv(unbinned_path, separator="\t", include_header=first)
    first = False
