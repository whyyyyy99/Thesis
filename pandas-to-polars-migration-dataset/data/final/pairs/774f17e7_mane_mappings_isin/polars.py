import polars as pl

    def get_mane_from_transcripts(self, transcripts: List[str]) -> List[Dict]:
        """Get mane transcripts from a list of transcripts

        :param List[str] transcripts: RefSeq transcripts on c. coordinate
        :return: MANE data
        """
        mane_rows = self.df.filter(pl.col("RefSeq_nuc").is_in(transcripts))
        if len(mane_rows) == 0:
            return []
        return mane_rows.to_dicts()
