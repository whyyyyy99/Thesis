import pandas as pd

    read_size = pd.read_csv(snakemake.input.read_size, names = ["sample", "read_size"])
    read_sizes = read_size.set_index("sample").to_dict()["read_size"]
    summary["unmapped_size"] = summary["samples"].apply(lambda x: sum([read_sizes[sample] for sample in x.split(",")]))
