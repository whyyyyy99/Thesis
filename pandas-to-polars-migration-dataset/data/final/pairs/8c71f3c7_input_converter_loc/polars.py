        return cast(
            str,
            self.documents_data.filter(pl.col("document_id") == d3_document_id)
            .select("semanticscholar_url")
            .item(),
        )
