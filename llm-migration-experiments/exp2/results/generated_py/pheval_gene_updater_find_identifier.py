if gene_symbol in self.hgnc_data.keys():
    return self.hgnc_data[gene_symbol][self.gene_identifier]
else:
    for _symbol, data in self.hgnc_data.items():
        for prev_symbol in data["previous_symbol"]:
            if prev_symbol == gene_symbol:
                return data[self.gene_identifier]