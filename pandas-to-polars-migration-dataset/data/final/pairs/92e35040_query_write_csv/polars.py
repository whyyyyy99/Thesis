    with open(binned_path, "ab") as binned_file, open(unbinned_path, "ab") as unbinned_file:
        first = True
        for binned, unbinned in outputs:
            binned.write_csv(binned_file, sep="\t", has_header=first)
            unbinned.write_csv(unbinned_file, sep="\t", has_header=first)
            first = False
