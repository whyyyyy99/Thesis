import pandas as pd

from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
...

def run_propensity_score(
    treated_set: pd.DataFrame,
    control_set: pd.DataFrame,
    model: str = "logit",
    hyperparam: Optional[Any] = None,
    covariates: Optional[Union[List[str], pd.Index[str]]] = None,
) -> pd.DataFrame:
