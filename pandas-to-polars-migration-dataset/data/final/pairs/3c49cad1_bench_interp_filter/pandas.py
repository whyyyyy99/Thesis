import pandas as pd

    filtered_df = df[df["date"].astype(str).str[:] == day_time.strftime("%Y-%m-%d %H:%M:%S+00:00")]
    values = filtered_df["value"].values.tolist()
