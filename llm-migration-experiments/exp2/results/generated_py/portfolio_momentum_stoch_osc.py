stochastic_oscillator_low_min = self.df["Low"].rolling_min(window_size=window)
stochastic_oscillator_high_max = self.df["High"].rolling_max(window_size=window)

stochastic_oscillator_stoch = (
    (self.df["Close"] - stochastic_oscillator_low_min)
    / (stochastic_oscillator_high_max - stochastic_oscillator_low_min)
    * 100
)

if fillna:
    stochastic_oscillator_stoch = stochastic_oscillator_stoch.fill_nan(50).fill_null(50)
    stochastic_oscillator_stoch_signal = (
        stochastic_oscillator_stoch.rolling_mean(window_size=smooth_window)
        .fill_nan(50)
        .fill_null(50)
    )
else:
    stochastic_oscillator_stoch_signal = stochastic_oscillator_stoch.rolling_mean(window_size=smooth_window)

self.df = self.df.with_columns(
    stoch=stochastic_oscillator_stoch,
    stoch_signal=stochastic_oscillator_stoch_signal,
)