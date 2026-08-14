        return self.identifier_map.filter(pl.col("identifier") == query_gene_identifier)[
            "gene_symbol"
        ][0]
