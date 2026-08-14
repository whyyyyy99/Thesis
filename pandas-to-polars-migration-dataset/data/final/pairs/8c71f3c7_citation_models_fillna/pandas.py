import pandas as pd

    return df.assign(publication_date_rank=df["publication_date_rank"].fillna(len(df)))
