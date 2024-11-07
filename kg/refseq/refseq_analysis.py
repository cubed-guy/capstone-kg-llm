# download the file using https://ftp.ncbi.nlm.nih.gov/refseq/H_sapiens/annotation/GRCh38_latest/refseq_identifiers/GRCh38_latest_genomic.gff.gz

file = open('GRCh38_latest_genomic.gff')

examples = dict((attr.split('=')) for rec in lines for attr in rec.split('\t')[-1].split(';') if rec and not rec.startswith('#'))

counts = {}
for i, rec in enumerate(lines):
    if not i&65535: print(i, end='\r', flush=True)
    if not rec or rec.startswith('#'): continue
    for attr in rec.split('\t')[-1].split(';'):
        k, _ = attr.split('=')
        if k not in counts: counts[k] = 1
        else: counts[k] += 1

print(sorted((count, attr, examples[attr]) for attr, count in counts.items()))
