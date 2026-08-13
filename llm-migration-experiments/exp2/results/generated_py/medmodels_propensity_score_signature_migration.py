import polars as pl

from typing import Any, List, Optional, Union


def run_propensity_score(
    treated_set: pl.DataFrame,
    control_set: pl.DataFrame,
    model: str = "logit",
    hyperparam: Optional[Any] = None,
    covariates: Optional[Union[List[str], pl.Series]] = None,
) -> pl.DataFrame:
    raise NotImplementedError("Source function body was not provided for translation.")