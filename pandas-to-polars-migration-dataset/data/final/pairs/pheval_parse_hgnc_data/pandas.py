import pandas as pd

    return pd.read_csv(
        os.path.dirname(__file__).replace("utils", "resources/hgnc_complete_set.txt"),
        delimiter="\t",
        dtype=str,
    )
