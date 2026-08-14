import pandas as pd

    appraise_binned["sample"] = appraise_binned["sample"].str.replace("\.1$", "", regex=True)
    appraise_binned = appraise_binned[appraise_binned["sample"] == sample]
