import pandas as pd
from pandas import DatetimeIndex

return pd.DatetimeIndex([pd.Timestamp(i.text) for i in timesteps.getchildren()])
