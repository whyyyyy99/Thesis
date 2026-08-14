        matches = self.identifier_map.filter(
            (pl.col("gene_symbol") == gene_symbol)
            & (pl.col("identifier_type") == self.gene_identifier)
        )
        if matches.height > 0:
            return matches["identifier"][0]
        prev_symbol_matches = self.identifier_map.filter(
            (pl.col("identifier_type") == self.gene_identifier)
            & (pl.col("prev_symbols").list.contains(gene_symbol))
        )
        if prev_symbol_matches.height > 0:
            return prev_symbol_matches["identifier"][0]
        return None
