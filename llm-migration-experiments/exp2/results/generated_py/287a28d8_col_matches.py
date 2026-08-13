import re
import polars as pl

return list(
    [
        c
        for c in data.columns
        if (
            re.search(pat, c, **kwargs)
            if kwargs.get("regex", True)
            else (
                (pat in c)
                if kwargs.get("case", True)
                else (pat.lower() in c.lower())
            )
        )
    ]
)