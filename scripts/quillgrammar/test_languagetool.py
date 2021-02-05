# run languagetool with the following command:
# java -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 8081 --allow-origin '*'
#
# and then make requests like this:
# http://localhost:8081/v2/check?language=en-US&text=the+man+are+small

import requests
import urllib
import random
import json
import re
import csv
from tqdm import tqdm
from scripts.check_grammar import run_grammarbot, run_ginger

IP = "localhost"
PORT = "8081"
LANGUAGE = "en-US"
URL = f"http://{IP}:{PORT}/v2/check?language={LANGUAGE}&text="


def test_on_junkfood():
    INPUT_FILE = "data/raw/junkfood_because.tsv"
    OUTPUT_FILE = "junkfood_because_languagetool.tsv"

    sentences = []
    with open(INPUT_FILE) as i:
        for line in i:
            sentences.append("Schools should not allow junk food to be sold on campus, " + line.strip().split("\t")[0])

    output = []
    for sentence in sentences:

        sentence = re.sub("\s+", " ", sentence)
        original_sentence = sentence
        encoded_sentence = urllib.parse.quote_plus(sentence)
        r = requests.get(URL + encoded_sentence).json()

        if len(r["matches"]) > 0:
            print(r)

        corrections = []

        index_correction = 0
        for correction in r["matches"]:
            if len(correction["replacements"]) > 0:
                start = correction["offset"] + index_correction
                end = start + correction["length"]
                replacement = correction["replacements"][0]["value"]

                corrections.append(" ".join([sentence[start:end], "=>", replacement]))
                corrections.append(correction["message"])
                corrections.append(correction["rule"])

                sentence = sentence[:start] + replacement + sentence[end:]

                index_correction += len(replacement) - (end-start)

        #sentence = urllib.parse.unquote(sentence)
        #sentence = sentence.replace("+", " ")

        if sentence != original_sentence:
            print(original_sentence)
            print(sentence)

        sentence_info = [original_sentence, sentence]
        sentence_info += corrections

        output.append(sentence_info)

    with open(OUTPUT_FILE, "w") as o:
        csvwriter = csv.writer(o, delimiter="\t")
        csvwriter.writerow(["Input sentence", "Corrected sentence", "Correction", "Message", "Rule info"])
        for row in output:
            csvwriter.writerow(row)


def test_on_quill_errors(f):

    with open(f) as i:
        sentences = [line.strip() for line in i]

    # random.seed = 1
    # random.shuffle(sentences)
    sentences = sentences[:100]

    errors_caught = 0
    responses = []
    for sentence in tqdm(sentences):
        #encoded_sentence = urllib.parse.quote_plus(sentence)
        #r = requests.get(URL + encoded_sentence).json()

        r = run_grammarbot(sentence)
        #r = run_ginger(sentence)

        responses.append({"sentence": sentence,
                          "response": r})

        #if len(r["GingerTheDocumentResult"]["Corrections"]) > 0:
        #    errors_caught += 1

        if len(r["matches"]) > 0:
            errors_caught += 1

    print(f)
    print("Errors caught:", errors_caught)
    print("Total sentences:", len(sentences))
    print("Performance:", errors_caught/len(sentences))

    with open("quill_spelling_grammarbot.json", "w") as o:
        json.dump(responses, o)

    return errors_caught/len(sentences)


def test_on_artificial_errors(f):
    with open(f) as i:
        corpus = json.load(i)

    tp, tn, fp, fn = 0, 0, 0, 0

    responses = []
    for example in tqdm(corpus[:100]):

        sentence = example["new_sentence"]
        encoded_sentence = urllib.parse.quote_plus(sentence)
        r = requests.get(URL + encoded_sentence).json()

        #r = run_grammarbot(sentence)
        #r = run_ginger(sentence)
        responses.append({"sentence": sentence,
                          "response": r})

        #num_found_errors = len(r["matches"])  # for LanguageTool and GrammarBot
        num_found_errors = len(r["GingerTheDocumentResult"]["Corrections"])  # for Ginger
        num_true_errors = len(example["corrections"])

        if num_found_errors > 0 and num_true_errors > 0:
            tp += 1

        elif num_found_errors > 0 and num_true_errors == 0:
            fp += 1

        elif num_found_errors == 0 and num_true_errors > 0:
            fn += 1

        elif num_found_errors == 0 and num_true_errors == 0:
            tn += 1

        #r = run_ginger(sentence)

        #if len(r["GingerTheDocumentResult"]["Corrections"]) > 0:
        #    errors_caught += 1

        #if len(r["matches"]) > 0:
        #    errors_caught += 1

    print(f)
    print(tp, fp, tn, fn)
    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    fscore = 2*precision*recall/(precision+recall)
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 score:", fscore)

    return fscore


if __name__ == "__main__":
    #test_on_quill_errors("data/raw/raw_spelling_mistakes_9_26_2019.csv")
    test_on_quill_errors("quill_spelling.txt")
    #test_on_quill_errors("data/raw/raw_grammar_errors_9_26_2019.csv")
    #test_on_artificial_errors("error_corpus.json")