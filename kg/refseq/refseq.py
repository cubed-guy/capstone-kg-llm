import sys

example = {
    'Dbxref': 0,
    'Name': 1,
    'chromosome': 2,
    'gbkey': 3,
    'genome': 4,
    'mol_type': 5,
    'description': 6,
    'gene': 7,
    'gene_biotype': 8,
    'pseudo': 9,
    'Parent': 10,
    'product': 11,
    'transcript_id': 12,
    'gene_synonym': 13,
    'Note': 14,
    'experiment': 15,
    'function': 16,
    'regulatory_class': 17,
    'standard_name': 18,
    'model_evidence': 19,
    'tag': 20,
    'protein_id': 21,
    'inference': 22,
    'recombination_class': 23,
    'feat_class': 24,
    'rpt_type': 25,
    'rpt_unit_seq': 26,
    'exception': 27,
    'anticodon': 28,
    'partial': 29,
    'start_range': 30,
    'end_range': 31
}

def enumerate_example():
    for i,k in enumerate(example.keys()):
        example[k] = i
    print(example)

def process_line(line):
    slice = line.split(";")
    seq_type = slice[0].split("\t")
    if seq_type[2]=="CDS":
        refseq = seq_type[-1].split("=")[1]
        d = {}
        for kv in slice[1:]:
            k, v = kv.split("=")
            d[k] = v
        return [d["hgnc_id"], refseq]    
    return None

def load_refseq_data(filename, count=-1):
    # by default count=-1 implies ALL.
    all, cur = False, 0
    if count<0: all=True

    d = {}
    
    global out

    print("Reading "+filename+"...")
    with open(filename) as file:
        if all:
            while line:=file.readline():
                if(line[0]=="#"):
                    continue
                res = process_line(line)
                if not res: continue
                out.append(res)
        else:
            while cur<count:
                line = file.readline()
                if(line[0]=="#"):
                    continue
                res = process_line(line)
                if not res: continue
                out.append(res)
                cur+=1

    for k,v in d.items():
        v = v.split(";")[1:]
        print(len(v), k, "|", *v)

    print(f"found {len(d)} types!")

out = []
load_refseq_data('../../GRCh38_latest_genomic.gff', int(sys.argv[1]))

# import csv

# index = ["hgnc", "refseq", *example.keys()]

# with open('refseq_cleaned.csv', 'w') as f:
#     writer = csv.writer(f)
#     writer.writerow(index)
#     writer.writerows(out)
