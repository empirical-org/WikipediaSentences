import csv
from collections import Counter

f = "connect_sentences_output_20201118.tsv"
error_counter = Counter()

error = 0
total = 0
with open(f) as i:
    reader = csv.reader(i, delimiter="\t")
    for row in reader:
        total += 1
        if len(row) == 4:
            sentence, error_type, index, token = row
            if error_type:
                error += 1
                error_counter.update([error_type])

print(f"{error}/{total} = {error/total*100}%")

for error_type, number in error_counter.most_common():
    print(error_type, number, number/total)