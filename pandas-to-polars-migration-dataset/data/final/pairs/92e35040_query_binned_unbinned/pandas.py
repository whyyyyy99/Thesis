import pandas as pd

def before_binned_unbinned(
    appraised: pd.DataFrame,
    pipe_read: pd.DataFrame,
    output_columns: list,
) -> tuple:
    binned = (appraised[appraised["binned"]]
              .drop(["divergence","binned"], axis=1)
              .reset_index(drop=True))
    unbinned = pipe_read.join(
        appraised.set_index(output_columns[0:-1]),
        on=output_columns[0:-1],
    )
    unbinned = (unbinned[~unbinned["binned"].fillna(False)]
                .drop(["divergence","binned"], axis=1)
                .reset_index(drop=True))
    unbinned["found_in"] = None
    return binned, unbinned
