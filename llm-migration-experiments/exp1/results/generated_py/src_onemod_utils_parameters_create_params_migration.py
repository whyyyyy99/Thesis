import polars as pl
from itertools import product


def create_params(config: ModelConfig) -> pl.DataFrame | None:
    param_dict = extract_param_dict(config)
    if len(param_dict) == 0:
        return None
    crossby = list(param_dict.keys())
    params = pl.DataFrame(
        [param_set for param_set in product(*param_dict.values())],
        schema=crossby,
    ).with_row_index("param_id")
    return params.select(["param_id", *crossby])
