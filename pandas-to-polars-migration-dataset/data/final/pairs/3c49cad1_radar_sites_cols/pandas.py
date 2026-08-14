import pandas as pd

        data = data.drop(labels=["coordinates_wgs84_text", "coordinates_gauss"], axis="columns")
        data = data.rename(columns={"coordinates_wgs84": "latitude"})
        data.insert(4, "longitude", seconds["coordinates_wgs84"].values)
        data = data.reset_index(drop=True)
        for column in ["latitude", "longitude"]:
            data[column] = data[column].apply(lambda x: x.strip("NE").replace(",", ".")).apply(float)
        for column in ["wmo_id", "altitude"]:
            data[column] = data[column].apply(int)
