    unbinned_otu_table = unbinned_otu_table.select([
        "gene", "sequence",
        pl.first("target").over(["gene", "sequence"]).cast(str),
        pl.first("taxonomy").over(["gene", "sequence"]),
    ]).unique().drop_nulls()
