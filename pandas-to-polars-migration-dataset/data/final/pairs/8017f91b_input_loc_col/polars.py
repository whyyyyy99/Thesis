        return cast(
            str,
            self.documents_frame.filter(pl.col("d3_document_id") == d3_document_id)
            .select("semanticscholar_url")
            .item(),
        )
