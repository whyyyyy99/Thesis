    fp = gpd.read_file(args.pkg, layer="flowpaths").set_index("id")
    network = gpd.read_file(args.pkg, layer="network").set_index("id")
