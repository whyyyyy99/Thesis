import pandas as pd
import numpy as np

        df_words = self.df[(self.df["class"] == "ocrx_word")]
        if page_number:
            df_words = df_words[df_words["page"] == page_number]
        df_words = df_words[df_words["value"].notnull() & (df_words["confidence"] >= min_confidence)]

        list_cells = [{"row": id_row, "col": id_col,
                       "x1_w": cell.x1, "x2_w": cell.x2,
                       "y1_w": cell.y1, "y2_w": cell.y2}
                      for id_row, row in enumerate(table.items)
                      for id_col, cell in enumerate(row.items)]
        df_cells = pd.DataFrame(list_cells)

        df_word_cells = df_words.merge(df_cells, how="cross")

        df_word_cells["x_left"] = df_word_cells[["x1", "x1_w"]].max(axis=1)
        df_word_cells["y_top"] = df_word_cells[["y1", "y1_w"]].max(axis=1)
        df_word_cells["x_right"] = df_word_cells[["x2", "x2_w"]].min(axis=1)
        df_word_cells["y_bottom"] = df_word_cells[["y2", "y2_w"]].min(axis=1)

        df_word_cells = df_word_cells[df_word_cells["x_right"] > df_word_cells["x_left"]]
        df_word_cells = df_word_cells[df_word_cells["y_bottom"] > df_word_cells["y_top"]]

        df_text_parent = (df_word_cells
                          .groupby(['row', 'col', 'parent'])
                          .agg(value=("value", lambda x: ' '.join(x)))
                          .sort_values(by=["row", "col", "y1", "x1"])
                          .groupby(["row", "col"])
                          .agg(text=("value", lambda x: "
".join(x) or None))
                          .reset_index())
