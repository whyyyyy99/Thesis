import pandas as pd

    try:
        df_bbox_delimiters = df_bbox_delimiters[df_bbox_delimiters["dels"].notnull()].explode(column="dels").reset_index()
        df_bbox_delimiters[['del1', 'del2']] = pd.DataFrame(df_bbox_delimiters.dels.tolist(), index=df_bbox_delimiters.index)
        df_bbox_delimiters["x1_bbox"] = df_bbox_delimiters["del1"]
        df_bbox_delimiters["x2_bbox"] = df_bbox_delimiters["del2"]
        df_cells = df_bbox_delimiters[["x1_bbox", "y1_bbox", "x2_bbox", "y2_bbox"]]
        df_cells.columns = ["x1", "y1", "x2", "y2"]
        return df_cells.reset_index()
    except ValueError:
        return pd.DataFrame(columns=["index", "x1", "y1", "x2", "y2"])
