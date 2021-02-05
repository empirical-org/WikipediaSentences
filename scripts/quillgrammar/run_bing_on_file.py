import csv
import time

from tqdm import tqdm

from quillnlp.spelling.bing import correct_sentence_with_bing

input_file = "data/raw/Comprehension Responses - Full Set June 2020 - Sheet1.csv"
#input_file = "data/raw/grammar_response_dump_connect_2020_06_29.csv"
output_file = "data/raw/comprehension_sentences_bing.csv"


t = 0
with open(input_file) as csvfile, open("comprehension_sentences_bing.tsv", "a") as csv_out:
    reader = csv.reader(csvfile)
    writer = csv.writer(csv_out, delimiter="\t")
    for row in tqdm(reader):
        if t > 7153:
            sentence = row[0]
            correct_sentence = correct_sentence_with_bing(sentence)
            writer.writerow([correct_sentence])
        t += 1
