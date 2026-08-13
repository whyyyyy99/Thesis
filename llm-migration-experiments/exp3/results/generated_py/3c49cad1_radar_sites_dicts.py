import polars as pl

def all(df):
    result = {}
    for item in df.to_dicts():
        key = item["dwd_id"]
        value = item
        result[key] = value
    return result
