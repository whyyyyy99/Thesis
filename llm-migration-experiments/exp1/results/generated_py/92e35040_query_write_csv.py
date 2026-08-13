import polars as pl

first = True
for binned, unbinned in outputs:
    with open(binned_path, "a") as f:
        binned.write_csv(f, include_header=first, separator="\t")
    with open(unbinned_path, "a") as f:
        unbinned.write_csv(f, include_header=first, separator="\t")
    first = False
