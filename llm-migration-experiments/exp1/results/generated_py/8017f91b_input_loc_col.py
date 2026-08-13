from typing import cast

import polars as pl

return cast(str, self.documents_data.row(d3_document_id)[self.documents_data.columns.index("semanticscholar_url")])
