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

# load ensembl gene/transcript id, exon id, protein id, hgnc id, type, name, *sequence
def load_geneID_annotation(filename):
    global out
    visited = set()
    num_lines=0
    print("Reading "+filename+"...")
    with open(filename) as file:
        while line:=file.readline():
            if(line[0]=="#"):
                continue
            # print(line)
            data_slice = line.split(";")
            if(data_slice[0].split('\t')[2]=="exon"):
                gene_id = data_slice[9][8:-2]
                gene_type = data_slice[4][10:]
                if gene_id not in visited:
                    out.append({"gene_id": gene_id, "gene_type": gene_type})
                    visited.add(gene_id)
            num_lines+=1

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
        gene['gene'] = gene_seq['seq']
    
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

    idx_chunk = [gene["gene_id"] for gene in out_chunk]
    return [idx_chunk, out_chunk]

load_geneID_annotation(sys.argv[1])
print(out, file=open("output.txt", 'w'))
chunkify()
writer.writerow(["id","type","seq"])
total = q.qsize()


def worker(thread_number):
    global chunks, total
    out = []
    while not q.empty():
        idx_chunk, out_chunk = q.get()
        resp = post_request(json.dumps(idx_chunk), out_chunk)
        resp = list(filter(lambda x: len(x)==3, resp))
        
        for gene in resp:
            out.append([gene["gene_id"], gene["gene_type"], gene["gene"]])
        
        # now we have result, want to write it
        with output_lock:  # this will block until the lock is available
            writer.writerows(out)
        print(f"CHUNKS({chunks+1}/{total}): Thread {thread_number} got {len(resp)} results!")
        chunks+=1
        q.task_done()

try:
    for thread in range(16):
        threading.Thread(target=worker, args=(thread,)).start()
except RuntimeError as e:
    print(f"Reached thread limit: {e}")


print("waiting for all tasks to complete")
chunks = 0
# q.join()