import re

f = open('failed_chunks.txt', 'r')
data = f.readline()

list_pattern = re.compile(r'\[.*?\]')
matches = list_pattern.findall(data)

out = []

for match in matches:
    try:
        # Safely evaluate the list and append it
        evaluated_list = eval(match)
        out.append(evaluated_list)
    except Exception as e:
        print(f"Error evaluating list: {match}, error: {e}")

print(out, file=open('ensembl-ids-4.txt', 'w'))
