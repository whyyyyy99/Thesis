import pandas as pd

        stochastic_oscillator = StochasticOscillator(
            close=self.df.Close, high=self.df.High, low=self.df.Low, window=window, smooth_window=smooth_window,
            fillna=fillna
        )
        self.df['stoch'] = stochastic_oscillator.stoch()
        self.df['stoch_signal'] = stochastic_oscillator.stoch_signal()
