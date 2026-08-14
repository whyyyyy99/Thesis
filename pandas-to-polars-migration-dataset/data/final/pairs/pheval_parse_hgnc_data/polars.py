    return (
        pl.read_csv(
            os.path.dirname(__file__).replace("utils", "resources/hgnc_complete_set.txt"),
            separator="\t",
            infer_schema=10000000000,
            dtypes={"omim_id": pl.Utf8},
        )
        .select(
            [
                pl.col("hgnc_id").alias("hgnc_id"),
                pl.col("symbol").alias("gene_symbol"),
                pl.col("ensembl_gene_id").alias("ensembl_id"),
                pl.col("entrez_id").alias("entrez_id"),
                pl.col("refseq_accession").alias("refseq_accession"),
                pl.col("prev_symbol").alias("previous_symbol_raw"),
            ]
        )
        .with_columns(
            pl.col("previous_symbol_raw")
            .str.split("|")
            .list.eval(pl.element().str.strip_chars('"'))
            .alias("prev_symbols")
        )
    )
