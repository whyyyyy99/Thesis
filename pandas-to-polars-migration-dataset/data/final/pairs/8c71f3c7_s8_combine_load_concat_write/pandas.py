import pandas as pd

            df_chunk = load_df_from_pickle(filepath)
    ...
    df_combined = pd.concat(df_list)
    ...
    write_df_to_pickle(df_combined, path_documents_authors_labels_citations)
