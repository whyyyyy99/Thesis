        pred_dfs.append(pl.DataFrame({"pred": pred, "y": valid_y, "w": valid_w}))
    pred_df = pl.concat(pred_dfs)
