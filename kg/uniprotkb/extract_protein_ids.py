# extract protein ids from data/exon/exon_sequences.csv
# feed to online unitprotkb portal - https://www.uniprot.org/id-mapping
# download data

import csv

li = []
with open("data/exon/exon_sequences.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        li.append(row[-2])
    li = li[1:]

# print(li[0])
# print(li[-1])
print(f"read {len(li)} records!")

print(*li, file=open("data/uniprotkb/protein_ids.txt", "w"))