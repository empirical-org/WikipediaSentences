import time

from tqdm import tqdm

from neuspell import BertsclstmChecker, SclstmChecker
checker = SclstmChecker()
checker = checker.add_("elmo", at="input")
checker.from_pretrained("/home/yves/software/neuspell/data/checkpoints/elmoscrnn-probwordnoise")

input_file = "/home/yves/projects/Quill-NLP-Tools-and-Datasets/quillgrammar/data/new_turk_data.csv"

with open(input_file) as i:
    lines = i.readlines()

corrected = 0
total = 0

start = time.time()
for line in tqdm(lines):
    input_sentence = line.strip()
    output_sentence = checker.correct(input_sentence)

    if input_sentence != output_sentence:
        corrected += 1
    total += 1
    

end = time.time()
total_time = end-start

print(f"{corrected}/{total}={corrected/total*100}% sentences corrected")
print(f"{total}/{total_time}={total/total_time} sentences/second")