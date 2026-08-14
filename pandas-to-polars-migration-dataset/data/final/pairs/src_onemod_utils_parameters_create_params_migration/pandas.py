from pandas import DataFrame

def create_params(config: ModelConfig) -> DataFrame | None:
    param_dict = extract_param_dict(config)
    if len(param_dict) == 0:
        return None
    crossby = list(param_dict.keys())
    params = DataFrame(
        [param_set for param_set in product(*param_dict.values())],
        columns=crossby,
    )
    params["param_id"] = params.index
    return params[["param_id", *crossby]]
