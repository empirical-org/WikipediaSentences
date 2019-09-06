import click
import json
import requests
import urllib
import re

from tqdm import tqdm

from quillnlp.utils import detokenize


PERFECT_TENSE_USER_API_KEY = ""
PERFECT_TENSE_APP_KEY = ""

LANGUAGETOOL_IP = "localhost"
LANGUAGETOOL_PORT = "8081"
LANGUAGE_TOOL_LANGUAGE = "en-US"
LANGUAGE_TOOL_URL = f"http://{LANGUAGETOOL_IP}:{LANGUAGETOOL_PORT}/v2/check?language={LANGUAGE_TOOL_LANGUAGE}&text="


def run_perfect_tense(sentence):

    headers = {"Authorization": PERFECT_TENSE_USER_API_KEY,
               "AppAuthorization": PERFECT_TENSE_APP_KEY,
               "Content-Type": "application/json"}

    response = requests.post("https://api.perfecttense.com/correct",
                             headers=headers,
                             data=json.dumps({"text": sentence}))

    return response.json()


def get_correct_sentence_perfect_tense(sentence, response):
    return response["corrected"]


def run_grammarbot(sentence):
    data = {"api_key": "KS9C5N3Y", "language":"en-US", "text": sentence}

    response = requests.post("http://api.grammarbot.io/v2/check", data=data)
    return response.json()


def get_correct_sentence_grammarbot(sentence, response):

    if response is None:
        return None

    corrections = []
    for match in response["matches"]:
        start_string_idx = match["offset"]
        end_string_idx = match["offset"] + match["length"]

        if len(match["replacements"]) > 0:
            replacement = match["replacements"][0]["value"]  # pick the first replacement by default
            corrections.append((start_string_idx, end_string_idx, replacement))

    corrections.sort(key=lambda x: x[0], reverse=True)  # sort on start index

    for correction in corrections:
        start_token_idx, end_token_idx, replacement = correction
        sentence = sentence[:start_token_idx] + replacement + sentence[end_token_idx:]

    return sentence


def run_languagetool(sentence):
    encoded_sentence = urllib.parse.quote_plus(sentence)
    response = requests.get(LANGUAGE_TOOL_URL + encoded_sentence)
    return response.json()


def get_correct_sentence_languagetool(sentence, response):

    corrections = []
    for match in response["matches"]:
        start_string_idx = match["offset"]
        end_string_idx = match["offset"] + match["length"]

        if len(match["replacements"]) > 0:
            replacement = match["replacements"][0]["value"]  # pick the first replacement by default
            corrections.append((start_string_idx, end_string_idx, replacement))

    corrections.sort(key=lambda x: x[0], reverse=True)  # sort on start index

    for correction in corrections:
        start_token_idx, end_token_idx, replacement = correction
        sentence = sentence[:start_token_idx] + replacement + sentence[end_token_idx:]

    return sentence


def get_correct_sentence(sentence, corrections):

    sentence_tokens = sentence.split()

    corrections.sort(key=lambda x: x[0], reverse=True)  # sort on start index

    for correction in corrections:
        start_token_idx, end_token_idx, replacement = correction
        sentence_tokens[start_token_idx:end_token_idx] = [replacement]

    correct_sentence = " ".join([x for x in sentence_tokens if len(x) > 0])

    return correct_sentence


def evaluate(sentences, file_name):

    responses = {}
    with open(file_name) as i:
        data = json.load(i)
        for response in data:
            responses[response["sentence"]] = response["response"]

    correct, correct_if_no_error, total, total_no_error = 0, 0, 0, 0
    suggested_sentences = []
    for sentence, gold_sentence in sentences:
        if sentence in responses:

            if "grammarbot" in file_name:
                suggested_sentence = get_correct_sentence_grammarbot(detokenize(sentence),
                                                                        responses[sentence])
            elif "perfecttense" in file_name:
                suggested_sentence = get_correct_sentence_perfect_tense(detokenize(sentence),
                                                                      responses[sentence])
            elif "languagetool" in file_name:
                suggested_sentence = get_correct_sentence_languagetool(detokenize(sentence),
                                                                     responses[sentence])

            suggested_sentences.append(suggested_sentence)
            if gold_sentence == suggested_sentence:
                correct += 1

            if gold_sentence == suggested_sentence == detokenize(sentence):
                correct_if_no_error += 1

            if gold_sentence == detokenize(sentence):
                total_no_error += 1

            total += 1

            """
            print("S", sentence)
            print("G", gold_sentence)
            print("C", suggested_sentence)
            print("")
            input()
            """
        else:
            suggested_sentences.append(None)

    print(file_name)
    print(f"Correct: {correct} / {total}")
    print(f"Correct if no error: {correct_if_no_error} / {total_no_error}")
    return suggested_sentences


def read_conll_corpus(f):
    data = {}
    with open(f) as i:
        for line in i:
            line = line.strip()
            if len(line) == 0:
                sentence = None
            elif line.startswith("S"):
                sentence = line[2:]
                data[sentence] = []
            elif sentence and line.startswith("A"):
                correction = line[2:].split("|||")
                start_token_idx, end_token_idx = correction[0].split()
                start_token_idx = int(start_token_idx)
                end_token_idx = int(end_token_idx)
                if start_token_idx == -1:
                    sentence = None
                else:
                    replacement = correction[2]
                    data[sentence].append((start_token_idx, end_token_idx, replacement))

    return data


def read_darmstadt_corpus(f):
    corrections = []
    word, correction = None, None
    with open(f) as i:
        for line in i:
            line = line.strip()
            if re.search("^[A-Za-z]", line) and word is None:
                word = line
            elif re.search("^[A-Za-z]", line) and correction is None:
                correction = line
            elif re.search("^[A-Za-z]", line):
                correct_sentence = line.replace(word, correction)
                corrections.append((line, correct_sentence))

            elif len(line) == 0:
                word, correction = None, None

    return corrections


@click.command()
@click.argument("input_file")
def check_grammar(input_file):

    #corrections = read_darmstadt_corpus(input_file)

    data = read_conll_corpus(input_file)
    gold_sentences = [detokenize(get_correct_sentence(sentence, data[sentence]))
                     for sentence in data]

    sentences = list(data.keys())
    corrections = list(zip(sentences, gold_sentences))

    suggestions = {}
    suggestions["sentences"] = sentences
    suggestions["corrections"] = gold_sentences
    suggestions["grammarbot"] = evaluate(corrections[:250], "grammarbot_conll.json")
    suggestions["perfecttense"] = evaluate(corrections[:250], "perfecttense_conll.json")
    suggestions["languagetool"] = evaluate(corrections[:250], "languagetool_conll.json")



if __name__ == "__main__":
    check_grammar()
