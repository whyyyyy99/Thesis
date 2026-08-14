import pandas as pd

motif_binary_compare["methylation_mean_threshold"] = np.where(
    motif_binary_compare["methylation_binary"] == 1,
    np.maximum(motif_binary_compare["mean_methylation"] - 4 * motif_binary_compare["std_methylation_bin"], 0.1),
    np.nan
)
motif_binary_compare["methylation_binary_compare"] = np.where(
    (motif_binary_compare["methylation_binary"] == 1) & 
    ((motif_binary_compare["mean"] >= motif_binary_compare["methylation_mean_threshold"]) | 
    (motif_binary_compare["mean"] > 0.4)),
    1,
    np.where(motif_binary_compare["methylation_binary"] == 1, 0, np.nan)
)
motif_binary_compare["methylation_mean_threshold"] = np.where(
    motif_binary_compare["methylation_binary"] == 0,
    0.25,
    motif_binary_compare["methylation_mean_threshold"]
)
motif_binary_compare["methylation_binary_compare"] = np.where(
    motif_binary_compare["methylation_binary"] == 0,
    (motif_binary_compare["mean"] >= 0.25).astype(int),
    motif_binary_compare["methylation_binary_compare"]
)
