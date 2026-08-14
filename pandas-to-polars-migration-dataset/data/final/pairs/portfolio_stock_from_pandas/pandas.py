import pandas as pd

    ticker = yf.Ticker(name)
    df = ticker.history(period=period, interval=interval)
    df['Datetime'] = df.index
    return df
