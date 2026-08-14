import pandas as pd


    for key, dataset in experiment.observations.items():
        observation = {
            "name": key,
            "values": list(dataset["observations"].values.flatten()),
            "errors": list(dataset["std"].values.flatten()),
        }
        if "time" in dataset.coords:
            observation["x_axis"] = _prepare_x_axis(dataset["time"].values.flatten())
        else:
            observation["x_axis"] = _prepare_x_axis(dataset["index"].values.flatten())
        observations.append(observation)
    observations.sort(key=lambda x: x["x_axis"])
