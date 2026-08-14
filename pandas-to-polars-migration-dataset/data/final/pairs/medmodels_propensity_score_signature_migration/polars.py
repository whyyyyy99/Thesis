from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Tuple, Union

import numpy as np
import polars as pl
...
from medmodels.matching.metrics import Metric
from medmodels.medrecord.types import MedRecordAttributeInputList

if TYPE_CHECKING:
    import sys
    if sys.version_info >= (3, 10):
        from typing import TypeAlias
    else:
        from typing_extensions import TypeAlias

Model: TypeAlias = Literal["logit", "dec_tree", "forest"]

def run_propensity_score(
    treated_set: pl.DataFrame,
    control_set: pl.DataFrame,
    model: Model = "logit",
    metric: Metric = "absolute",
    number_of_neighbors: int = 1,
    hyperparam: Optional[Dict[str, Any]] = None,
    covariates: Optional[MedRecordAttributeInputList] = None,
) -> pl.DataFrame:
