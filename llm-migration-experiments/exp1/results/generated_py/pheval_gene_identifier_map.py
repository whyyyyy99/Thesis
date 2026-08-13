import polars as pl

hgnc_df = read_hgnc_data()
identifier_map = {}
for row in hgnc_df.iter_rows(named=True):
    identifier_map[row["ensembl_gene_id"]] = row["symbol"]
    identifier_map[row["hgnc_id"]] = row["symbol"]
    identifier_map[row["entrez_id"]] = row["symbol"]
    identifier_map[row["refseq_accession"]] = row["symbol"]
return identifier_map
