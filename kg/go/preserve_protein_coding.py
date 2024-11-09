# read all ensembl_go_mappings
# do a join with exon_sequences on exon_id

import pandas as pd
base = "data/"

def clean_df(df, preserve_columns):
    filtered = df.dropna()
    filtered = filtered.loc[:, preserve_columns]
    filtered = filtered.drop_duplicates()
    return filtered

# for mappings
df1 = pd.read_csv(base+"exons/exon_sequences.csv")
df2 = pd.read_csv(base+"go/ensembl_go_mappings.csv")

print(df1.head())
print(df2.head())

merged_df = pd.merge(df2, df1, left_on='ensembl', right_on='gene_id')
preserve_columns = ["gene_id", "go"]
filtered_df = clean_df(merged_df, preserve_columns)

filtered_df.to_csv(base+'go/ensembl_go_protein_coding.csv', index=False)

# for triples
f = open(base+"go/go_triples.txt")
triples = eval(f.read())
triples = pd.DataFrame(triples, columns=["head", "relation", "tail"])

merged_triples = pd.merge(filtered_df, triples, left_on='go', right_on='head')
preserve_columns = ["head", "relation", "tail"]
filtered_triples = clean_df(merged_triples, preserve_columns)

filtered_triples.to_csv(base+'go/go_triples_protein_coding.csv', index=False)