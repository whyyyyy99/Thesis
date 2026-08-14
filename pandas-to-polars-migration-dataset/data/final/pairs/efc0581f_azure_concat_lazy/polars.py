        return OCRDataframe(df=pl.concat(list_dfs).lazy())
