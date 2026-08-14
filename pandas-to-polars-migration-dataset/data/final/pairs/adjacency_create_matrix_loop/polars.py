    fp_rows = fp.select([pl.col("id"), pl.col("toid")]).collect()
    network_df = network.collect()
    network_lookup = dict(zip(network_df["id"].to_list(), network_df["toid"].to_list()))
    network_changes = []
    fp_changes = []
    for row in tqdm(fp_rows.iter_rows(), desc="finding indices"):
        id_val = row[0]
        nex = row[1]
        ds_wb = network_lookup.get(nex)
        if ds_wb is None:
            ...
        network_changes.extend([(nex, ds_wb), (ds_wb, None)])
        fp_changes.append((ds_wb, None))
        sorter.add(ds_wb, id_val)
    # Apply all changes after loop
    if network_changes:
        network = network_df.with_columns([pl.col("id").map_elements(lambda x: changes_dict.get(x, ...), return_dtype=pl.String).alias("toid")])
    if fp_changes:
        fp = fp.with_columns([pl.col("id").map_elements(lambda x: fp_changes_dict.get(x, x), return_dtype=pl.String).alias("toid")]).collect()
