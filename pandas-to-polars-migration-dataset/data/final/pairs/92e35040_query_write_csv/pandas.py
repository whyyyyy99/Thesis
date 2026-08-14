import pandas as pd

    first = True
    for binned, unbinned in outputs:
        binned.to_csv(binned_path, sep = "\t", mode = "a", header = first, index = False)
        unbinned.to_csv(unbinned_path, sep = "\t", mode = "a", header = first, index = False)
        first = False
