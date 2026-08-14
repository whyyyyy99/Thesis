import pandas as pd

        frame = pd.concat(data)
        frame.set_index(["Realization", "Well", "Ensemble", "Iteration"], inplace=True)
        if drop_const_cols:
            frame = frame.loc[:, (frame != frame.iloc[0]).any()]
        frame.to_csv(output_file)
