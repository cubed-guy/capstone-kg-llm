from biomart import BiomartServer
import time
import threading
import queue
import csv

server = BiomartServer("http://www.ensembl.org/biomart")
print("connecting to biomart server...")
start = time.time()

# Connect to the Ensembl BioMart server

f = open("ensembl-ids-4.txt", "r")
li = eval(f.read())
f.close()

# out = []
# with open('exon_sequences.csv', 'r') as f:
#     reader = csv.reader(f)
#     for row in reader:
#         out.append(row[0])
# out = out[1:]
# chunk_size = 200
# li = []
# for i in range(0, len(out)-chunk_size, chunk_size):
#     li.append(out[i:i+chunk_size])

# print(f"got {len(li)} chunks, expected {len(out)//200} chunks!")

f = open("ensembl_go_mappings.txt", "w")
fail = open("failed_chunks.txt", "w")
log = open("log_biomart_ensembl_go.txt", "w")
total_time = 0
q = queue.Queue()
output_lock = threading.Lock()

for chunk in li:
    q.put(chunk)

# Select the dataset
dataset = server.datasets['hsapiens_gene_ensembl']

# 'name_1006',
# 'definition_1006',
# 'go_linkage_type',
# 'namespace_1003',
# 'start_position',
# 'end_position',
# 'transcript_gencode_basic',
# 'gene_biotype',
# 'external_synonym',
# 'external_gene_name',
# 'phenotype_description'

def worker(thread_number):
    failed = False

    while not q.empty():
        start = time.time()
        chunk = q.get()
        filters = {
            'ensembl_exon_id': chunk
        }

        try:
            response = dataset.search({
                'filters': filters,
                'attributes': attributes
            })
        except Exception as e:
            print(f"THREAD {thread_number}: failed to fetch chunk")
            failed = True
            with output_lock:
                fail.write(str(chunk))
                log.write(str(e)+"\n")
            pass

        end = time.time()

        if not failed:
            with output_lock:
                for line in response:
                    f.write(str(line.decode('utf-8')))
            print(f"THREAD {thread_number}: chunk fetched! process took {end-start} seconds")

        failed = False
        q.task_done()

attributes = [
    'ensembl_exon_id',
    'go_id',
]

end = time.time()

print(f"connected! process took {end-start} seconds")
print("querying biomart server...")
print(f"loading {len(li)} chunks...")

num_threads = 16 if q.qsize()>15 else q.qsize()
try:
    for thread in range(num_threads):
        threading.Thread(target=worker, args=(thread,)).start()
except RuntimeError as e:
    print(f"Reached thread limit: {e}")

# q.join()
# f.close()
# fail.close()
# print("done!")