        return self.tokens_frame.with_columns(embedding=pl.Series(embeddings)).drop("tokens")
