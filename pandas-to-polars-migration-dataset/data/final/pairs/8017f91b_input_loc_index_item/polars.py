            self.documents_frame.filter(pl.col("semanticscholar_url") == semanticscholar_url)
            .select("d3_document_id")
            .item()
