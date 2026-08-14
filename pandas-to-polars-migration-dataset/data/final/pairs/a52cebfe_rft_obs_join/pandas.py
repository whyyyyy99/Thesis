import pandas as pd


                rft_data = pd.DataFrame(pressure_vals, index=range(len(tvd_arg)))
                ensemble_data = []
                for iens in realizations:
                    frame = pd.DataFrame(
                        data={"TVD": tvd_arg, "Pressure": rft_data[iens],
                              "ObsValue": obs_node["observations"].values[0],
                              "ObsStd": obs_node["std"].values[0]},
                    )
                    realization_frame["Realization"] = iens
                    realization_frame["Well"] = well
                    ensemble_data.append(realization_frame)
                data.append(pd.concat(ensemble_data))
