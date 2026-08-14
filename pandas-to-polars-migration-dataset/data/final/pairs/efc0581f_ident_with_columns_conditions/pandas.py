import pandas as pd

    cross_h_lines["l_corresponds"] = (cross_h_lines["x1"] - cross_h_lines["x1_"] / cross_h_lines["width"]).abs() <= 0.02
    cross_h_lines["r_corresponds"] = (cross_h_lines["x2"] - cross_h_lines["x2_"] / cross_h_lines["width"]).abs() <= 0.02
    cross_h_lines["l_contained"] = (((cross_h_lines["x1"] <= cross_h_lines["x1_"])
                                    & (cross_h_lines["x1_"] <= cross_h_lines["x2"]))
                                    | ((cross_h_lines["x1_"] <= cross_h_lines["x1"])
                                       & (cross_h_lines["x1"] <= cross_h_lines["x2_"])))
    cross_h_lines["r_contained"] = (((cross_h_lines["x1"] <= cross_h_lines["x2_"])
                                     & (cross_h_lines["x2_"] <= cross_h_lines["x2"]))
                                    | ((cross_h_lines["x1_"] <= cross_h_lines["x2"])
                                       & (cross_h_lines["x2"] <= cross_h_lines["x2_"])))
