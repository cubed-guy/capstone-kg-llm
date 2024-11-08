import pandas as pd 

tsv_file = "data/uniprotkb/idmapping_2024_11_08.tsv"
csv_file = "data/uniprotkb/uniprotkb_protein_coding.csv"
csv_table=pd.read_table(tsv_file, sep='\t')
csv_table.to_csv(csv_file,index=False)
