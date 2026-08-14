            self.documents_data.filter(pl.col("semanticscholar_url") == semanticscholar_url)
            .select("document_id")
            .item()
