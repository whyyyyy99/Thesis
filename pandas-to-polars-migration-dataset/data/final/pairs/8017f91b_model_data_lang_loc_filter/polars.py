            query_document=self.query_document,
            info_frame=self.info_frame.filter(pl.col("candidate_d3_document_id").is_in(indices)),
            features_frame=self.features_frame.filter(
                pl.col("candidate_d3_document_id").is_in(indices)
            ),
            integer_labels_frame=self.integer_labels_frame.filter(
                pl.col("candidate_d3_document_id").is_in(indices)
            ),
