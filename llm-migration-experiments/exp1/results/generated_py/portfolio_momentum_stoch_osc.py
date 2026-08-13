import polars as pl

stochastic_oscillator = StochasticOscillator(
    close=self.df.get_column("Close"),
    high=self.df.get_column("High"),
    low=self.df.get_column("Low"),
    window=window,
    smooth_window=smooth_window,
    fillna=fillna
)
self.df = self.df.with_columns([
    pl.Series("stoch", stochastic_oscillator.stoch()),
    pl.Series("stoch_signal", stochastic_oscillator.stoch_signal()),
])
