import polars as pl

        data = self.df.filter(pl.col("symbol") == gene_symbol.upper())

        if len(data) == 0:
            logger.warning(f"Unable to get MANE Transcript data for gene: {gene_symbol}")
            return None

        data = data.sort(by="MANE_status", descending=False)
        return data.to_dicts()
