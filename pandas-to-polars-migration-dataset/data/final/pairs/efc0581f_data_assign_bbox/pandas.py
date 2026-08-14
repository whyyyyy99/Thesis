import pandas as pd

        df_words = df_words.assign(**{"x1_bbox": bbox[0],
                                      "y1_bbox": bbox[1],
                                      "x2_bbox": bbox[2],
                                      "y2_bbox": bbox[3]})
        df_words["x_left"] = df_words[["x1", "x1_bbox"]].max(axis=1)
        df_words["y_top"] = df_words[["y1", "y1_bbox"]].max(axis=1)
        df_words["x_right"] = df_words[["x2", "x2_bbox"]].min(axis=1)
        df_words["y_bottom"] = df_words[["y2", "y2_bbox"]].min(axis=1)
