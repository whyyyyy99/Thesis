import polars as pl

first = True
for binned, unbinned in outputs:
    with open(binned_path, "a", encoding="utf-8") as f:
        binned.write_csv(f, separator="\t", include_header=first)
    with open(unbinned_path, "a", encoding="utf-8") as f:
        unbinned.write_csv(f, separator="\t", include_header=first)
    first = False