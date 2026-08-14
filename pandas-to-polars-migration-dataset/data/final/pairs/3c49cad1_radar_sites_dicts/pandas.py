import pandas as pd

def all(df):
    result = {}
    for item in df.to_dict(orient="records"):
        key = item["dwd_id"]
        value = item
        result[key] = value
    return result
