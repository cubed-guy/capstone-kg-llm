import requests, sys
import json
import csv
import math
import queue
import threading
import time

out = []
q = queue.Queue()
output = open('exon_seq_type.csv', 'w')
writer = csv.writer(output)
output_lock = threading.Lock()

def process_line(line):
    data_slice = line.split(";")
    d = {}
    for kv in data_slice[1:]:
        k,v = kv.split("=")
        d[k] = v
    d["seq_type"] = data_slice[0].split("\t")[2]
    return d

# gene id, transcript id, hgnc_id, gene_type, gene_name, exon_id, protein_id
def load_geneID_annotation(filename, count=100):
    global out
    visited = set()
    num_lines=0

    foundTranscript = False
    preceded = set()

    print("Reading "+filename+"...")
    with open(filename) as file:
        while num_lines<count: 
            # line=file.readline()

            if foundTranscript:
                foundTranscript = False
            else:
                line=file.readline()
                if(line[0]=="#"):
                    continue
                d = process_line(line)

            if d["seq_type"]=="transcript" and d["gene_type"]=="protein_coding":
                try:
                    prefix = [d["gene_id"], d["transcript_id"], d["hgnc_id"], d["gene_type"], d["gene_name"]] # ensembl gene id, transcript id, hgnc id, gene_type, gene_name
                except KeyError:
                    continue

                row = [] # exon id, protein id
                # while d["seq_type"] != "gene" and d["seq_type"]!="three_prime_UTR":
                while True:
                    d=process_line(file.readline())
                    if d["seq_type"]=="exon" and d["gene_type"]=="protein_coding":
                        row = [d["exon_id"], d["protein_id"]]
                        row = prefix + row
                        out.append(row)
                        num_lines+=1
                    if d["seq_type"] == "transcript":
                        foundTranscript = True
                        break

    print(f"every sequence type preceding a transcript: {preceded}")

def post_request(ids_chunk, out_chunk):
    headers={ "Content-Type" : "application/json", "Accept" : "application/json"}

    # commons.ENSEMBL_URL+commons.SEQUENCE_FROM_ID
    server = "https://rest.ensembl.org"
    ext = "/sequence/id"
    headers={ "Content-Type" : "application/json", "Accept" : "application/json"}

    # r = requests.post(server+ext, headers=headers, data='{ "ids" : ["ENSG00000157764", "ENSG00000248378" ] }')
    r = requests.post('https://rest.ensembl.org/sequence/id', headers=headers, data=f'{"{"}"ids": {ids_chunk}{"}"}')
    if not r.ok:
        r.raise_for_status()
        sys.exit()
    
    decoded = r.json()
    for gene, gene_seq in zip(out_chunk, decoded):
        gene.append(gene_seq['seq'])
    
    return out_chunk

def chunkify():
    global out, chunks
    #the REST server doesn't accept big POST bodies, so chunking them
    size = len(out)
    chunk_size = 32
    chunks = math.floor(size/chunk_size)

    print("Loading "+str(size)+" rows of data in chunks of "+str(chunk_size))
    for chunk in range(0, chunks):
        q.put(fetch_chunk(chunk, chunk_size))
    q.put(fetch_chunk(chunks, chunk_size, isLast=True))

def fetch_chunk(chunk, chunk_size, isLast=False):
    global out
    out_chunk = []
    idx = lambda idx: idx*chunk_size

    if not(isLast):
        out_chunk = out[idx(chunk):idx(chunk+1)]
    else:
        out_chunk = out[idx(chunk):]

    idx_chunk = [gene[-2] for gene in out_chunk]
    # idx_chunk - list of exon_ids( we send requests based on this )
    # out_chunk - rest of the data, associated with every exon_id
    # they are sent as a tuple to maintain their coupling / association
    return [idx_chunk, out_chunk]

def clean_rows():
    global out
    for line in out: 
        line[0], line[1], line[-2], line[-1] = line[0][0:15], line[1][0:15], line[-2][0:15], line[-1][0:15]

labels = ["gene_id", "transcript_id", "hgnc_id", "gene_type", "gene_name", "exon_id", "protein_id", "sequence"]
load_geneID_annotation(sys.argv[1], int(sys.argv[2]))
print(f"len: {len(out)}")
clean_rows()
print(f"len: {len(out)}")

s = set()
td = {}
for li in out:
    # s.add(tuple(li))
    # s.add(li[0])
    s.add((li[1], li[-1]))
print(f"unique records: {len(s)}")

for t, p in s:
    if t not in td:
        td[t] = []
    td[t].append(p)

print(f"got {len(td)} unique transcripts")

for k,v in td.items():
    if len(v)>1:
        print(k, v)

print(f"got {len(out)} exon data slices!")
# # print(out, file=open("output.txt", 'w'))
chunkify()
writer.writerow(labels)
# writer.writerows(out)
total = q.qsize()

def worker(thread_number):
    global chunks, total
    out = []
    while not q.empty():
        idx_chunk, out_chunk = q.get()
        resp = post_request(json.dumps(idx_chunk), out_chunk) # output, evne thought it's coalesced, is still chunked
        # now we have result, want to write it
        with output_lock:  # this will block until the lock is available
            writer.writerows(resp)
        print(f"CHUNKS({chunks+1}/{total}): Thread {thread_number} got {len(resp)} results!")
        chunks+=1
        q.task_done()

try:
    for thread in range(8):
        threading.Thread(target=worker, args=(thread,)).start()
except RuntimeError as e:
    print(f"Reached thread limit: {e}")


print("waiting for all tasks to complete")
chunks = 0
# # q.join()