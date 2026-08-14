import pandas as pd

    if not all(files_server["filename"].str.endswith(".bz2")):
        files_server = files_server[~files_server["filename"].str.endswith(".bz2")]
