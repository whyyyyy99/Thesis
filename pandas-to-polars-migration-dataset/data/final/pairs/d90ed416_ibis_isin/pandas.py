import pandas as pd

        elusive_clusters = pd.read_csv(os.path.abspath(args.elusive_clusters), sep="\t")
        elusive_clusters = elusive_clusters[elusive_clusters["coassembly"].isin(args.coassemblies)]
