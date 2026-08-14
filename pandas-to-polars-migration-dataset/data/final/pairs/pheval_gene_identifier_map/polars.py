    hgnc_df = parse_hgnc_data()
    return hgnc_df.melt(
        id_vars=["gene_symbol", "prev_symbols"],
        value_vars=["ensembl_id", "hgnc_id", "entrez_id", "refseq_accession"],
        variable_name="identifier_type",
        value_name="identifier",
    ).with_columns(
        pl.col("identifier_type")
        .replace(
            {
                "ensembl_id": "ensembl:",
                "hgnc_id": "",
                "entrez_id": "ncbigene:",
                "refseq_accession": "",
            },
            default="",
        )
        .alias("prefix")
    )
