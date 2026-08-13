from typing import Any

import polars as pl


def get_params(params: pl.DataFrame, param_id: int) -> dict[str, Any]:
    params = params.filter(pl.col("param_id") == param_id).drop("param_id")
    return {
        str(param_name): param_value.item()
        for param_name, param_value in params.items()
    }
