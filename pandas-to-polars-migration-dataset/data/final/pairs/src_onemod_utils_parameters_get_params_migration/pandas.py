from pandas import DataFrame

def get_params(params: DataFrame, param_id: int) -> dict[str, Any]:
    params = params.query("param_id == @param_id").drop(columns=["param_id"])
    return {
        str(param_name): param_value.item()
        for param_name, param_value in params.items()
    }
