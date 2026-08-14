        df_page = self.df.filter(pl.col('page') == page_number)
        return OCRDataframe(df=df_page)
