import polars as pl

def create_params(config: ModelConfig) -> pl.DataFrame | None:
    crossby = list(param_dict.keys())
    params = pl.DataFrame(
        [list(param_set) for param_set in product(*param_dict.values())],
        schema=crossby,  # TODO: I think schema is incorrectly provided
    )
    params = params.with_row_index(name="param_id")
    return params.select(["param_id", *crossby])
