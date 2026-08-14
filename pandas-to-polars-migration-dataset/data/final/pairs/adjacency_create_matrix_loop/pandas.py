    for id in fp.index:
        nex = fp.loc[id]["toid"]
        try:
            ds_wb = network.loc[nex]["toid"]
        except KeyError:
            ...
        if isinstance(ds_wb, gpd.pd.Series):
            ds_wb = ds_wb.iloc[0]
        sorter.add(ds_wb, id)
        # mutations:
        network.loc[nex, "toid"] = ds_wb
        network.loc[ds_wb, "toid"] = np.nan
        fp.loc[ds_wb, "toid"] = np.nan
