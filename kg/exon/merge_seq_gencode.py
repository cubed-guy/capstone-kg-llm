import pandas as pd

# Load the CSVs
df1 = pd.read_csv('protein_gencode_data.csv')  # shorter CSV
df2 = pd.read_csv('exon_seq_type.csv')   # longer CSV

# Merge the data on matching IDs
merged_df = pd.merge(df1, df2, left_on='gene_id', right_on='id')

# Drop any rows with null values
filtered_df = merged_df.dropna()

# Drop the specified common columns
filtered_df = filtered_df.drop(columns=['type', 'id'])

# Drop duplicate rows if any remain
filtered_df = filtered_df.drop_duplicates()

# Save the result or display it
filtered_df.to_csv('exon_sequences.csv', index=False)
print(filtered_df)
