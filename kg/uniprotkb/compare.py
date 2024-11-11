import heapq

freq = [1842, 1842, 1842, 1842, 1842, 1842, 1842, 1842, 2, 196, 344, 432, 145, 30, 22, 161, 60, 1188, 139, 447, 2, 364, 90, 6, 636, 155, 40, 1842, 1650, 235, 777, 155, 1188, 113, 1188, 1109, 231, 269, 927]
header = ["From","Entry","Reviewed","Entry Name","Protein names","Gene Names","Organism","Length","Absorption","Active site","Binding site","Catalytic activity","Cofactor","DNA binding","pH dependence","Pathway","Kinetics","Function [CC]","Activity regulation","EC number","Redox potential","Rhea ID","Site","Temperature dependence","Tissue specificity","Induction","Developmental stage","Annotation","Comments","Coiled coil","Compositional bias","Motif","Protein families","Zinc finger","Sequence similarities","Region","Repeat","Domain [CC]","Domain [FT]"]

h = []
for k,v in zip(header, freq):
    heapq.heappush(h, [-v, k])

total = 0
while len(h)>0:
    v, k = heapq.heappop(h)
    print(f"{k}: {-v}")
    total+=-v

print(f"total nodes: {total}")