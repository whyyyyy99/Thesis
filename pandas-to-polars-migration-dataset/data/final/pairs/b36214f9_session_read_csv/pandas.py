import pandas as pd
from io import StringIO

        database_info = pd.read_csv(StringIO(query_result))

        if database_info.empty or "db" not in database_info.columns:
            logger.warning("No column information found in the RDF store")
            return None

        unique_values = database_info["db"].dropna().unique()
