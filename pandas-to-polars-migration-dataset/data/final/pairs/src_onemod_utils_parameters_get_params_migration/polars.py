def get_params(params: pl.DataFrame, param_id: int) -> dict[str, Any]:
    params = params.filter(pl.col("param_id") == param_id).drop("param_id")
    return {str(col): params[col][0] for col in params.columns}
