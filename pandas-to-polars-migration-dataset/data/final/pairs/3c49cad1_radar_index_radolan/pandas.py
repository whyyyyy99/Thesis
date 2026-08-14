import pandas as pd

    file_index = file_index[
        file_index["filename"].str.contains("/bin/")
        & file_index["filename"].str.endswith((Extension.GZ.value, Extension.TAR_GZ.value))
    ].copy()
