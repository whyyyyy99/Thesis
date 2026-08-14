import pandas as pd

    unbinned.drop(["found_in"], axis=1, errors="ignore", inplace=True)
    unbinned["target"] = unbinned.groupby(["gene", "sequence"]).ngroup()
    unbinned["target"] = unbinned["target"].astype(str)

    taxonomy = unbinned.groupby("target")["taxonomy"].first()
