import geopandas as gpd
import polars as pl

fp = pl.from_pandas(gpd.read_file(args.pkg, layer="flowpaths"))
network = pl.from_pandas(gpd.read_file(args.pkg, layer="network"))
