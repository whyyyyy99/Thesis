import polars as pl

def get_mane_from_transcripts(self, transcripts: List[str]) -> List[Dict]:
    """Get mane transcripts from a list of transcripts

    :param List[str] transcripts: RefSeq transcripts on c. coordinate
    :return: MANE data
    """
    mane_rows = self.df["RefSeq_nuc"].is_in(transcripts)
    result = self.df.filter(mane_rows)
    if len(result) == 0:
        return []
    return result.to_dicts()
