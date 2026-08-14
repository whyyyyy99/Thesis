    namespace = "hydrofabric"
    catalog = load_catalog(namespace)
    fp = catalog.load_table("hydrofabric.flowpaths").to_polars()
    network = catalog.load_table("hydrofabric.network").to_polars()
