import geopandas as gpd
import polars as pl

fp = pl.from_pandas(gpd.read_file(args.pkg, layer="flowpaths")).drop("id")
network = pl.from_pandas(gpd.read_file(args.pkg, layer="network")).drop("id")