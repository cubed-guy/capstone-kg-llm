# gene -> transcripts -> exons, CDS, five_prime_UTR, three_prime_UTR, start/stop codons
# ignored - stop_codon_redefined_as_selenocysteine
import csv
import sys

def load_data(filename, records=-1):
    global out, header
    count = records
    cur = 0
    # isFirst = True
    # total, protein = 0, 0
    # seq_types = {}

    print("Reading "+filename+"...")
    with open(filename) as file:
        while cur<count:
            line = file.readline()
            if(line[0]=="#"):
                continue
            data_slice = line.split(";")
            first = data_slice[0].split('\t')
            seq_type = first[2]
            seq_len = int(first[4])-int(first[3])
            d = {}
            for kv in data_slice[1:]:
                k,v = kv.split("=")
                d[k] = v
            if seq_type=="exon" and d["gene_type"]=="protein_coding":
                li = []
                # if isFirst:
                #     for kv in data_slice[1:]:
                #         header.append(kv.split("=")[0])
                #     isFirst = False

                # keyerr = False
                if seq_len<=1024:
                    for k in ['exon_id', 'gene_type', 'gene_name', 'hgnc_id']:
                        e = d.get(k, None)
                        li.append(e.strip("\"") if e else None)
                    out.append(li)
                    cur+=1
            #     protein+=1
            # total+=1

    # print(f"there are {protein} protein_coding sequences and {total} genes")
    # print(f"different sequence types for protein coding sequences - {seq_types}")

def clean(seq):
    out = []
    for row in seq:
        row[0] = row[0][:15]
        if row[2].startswith("ENSG"):
            continue
        row[-1] = row[-1].replace('"', '').strip() if row[-1] else None
        out.append(row)

    return out


out, header = [], ['gene_id', 'gene_type', 'gene_name', 'hgnc_id']
load_data('../../gencode.v45.basic.annotation.csv', int(sys.argv[1]))

print(header)
print(f"there are {len(out)} sequences( given the size constraint )")
print(out[:1])
out = clean(out)
print(out[:1])


with open('protein_gencode_data.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(out)