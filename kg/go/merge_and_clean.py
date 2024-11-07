import csv

with open("ensembl_go_mappings.csv", "w") as csvf:
    writer = csv.writer(csvf)
    writer.writerow(["ensembl", "go"])

    base = "chunk"
    for i in range(2):
        f = open(base+str(i)+".txt")
        while line:=f.readline():
            line = f.readline().split()
            if len(line)>1:
                writer.writerow(line)
        f.close()

