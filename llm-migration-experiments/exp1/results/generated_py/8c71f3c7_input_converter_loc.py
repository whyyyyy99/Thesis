from typing import cast

return cast(str, self.documents_data.filter(pl.col("d3_document_id") == d3_document_id).get_column("semanticscholar_url").item())
