import click
import json
import requests
import urllib
import re
import csv
import spacy
import time

from collections import defaultdict

from tqdm import tqdm

from quillnlp.utils import detokenize
from private import BING_KEY, BING_URL

PERFECT_TENSE_USER_API_KEY = ""
PERFECT_TENSE_APP_KEY = ""

GRAMMAR_BOT_API_KEY = "KS9C5N3Y"

GINGER_API_KEY = "6959e8fb-7b83-49e9-835d-808f8b0dfc62"
GINGER_API_URL = f"https://sb-partner-services.gingersoftware.com/correction/v1/document?apiKey={GINGER_API_KEY}&lang=US"

LANGUAGETOOL_IP = "localhost"
LANGUAGETOOL_PORT = "8081"
LANGUAGE_TOOL_LANGUAGE = "en-US"
LANGUAGE_TOOL_URL = f"http://{LANGUAGETOOL_IP}:{LANGUAGETOOL_PORT}/v2/check?language={LANGUAGE_TOOL_LANGUAGE}&text="
LANGUAGETOOL_ONLINE_URL = "https://languagetool.org/api/v2/check"


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
    data = {"api_key": GRAMMAR_BOT_API_KEY, "language":"en-US", "text": sentence}

    response = requests.post("http://api.grammarbot.io/v2/check", data=data)
    return response.json()


def run_ginger(sentence):
    r = requests.post(GINGER_API_URL, sentence.encode('utf-8'))

    return r.json()


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


def run_languagetool_online(sentence):
    encoded_sentence = urllib.parse.quote_plus(sentence)
    post_parameters = {
        "text": sentence,
        "language": "en-US",
    }

    response = requests.post(LANGUAGETOOL_ONLINE_URL, post_parameters)
    return response.json()


def run_bing(sentence):
    data = {'text': sentence}

    params = {
        'mkt': 'en-us',
        'mode': 'proof'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Ocp-Apim-Subscription-Key': BING_KEY,
    }

    response = requests.post(BING_URL, headers=headers, params=params, data=data)
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


def read_quill_data(f):
    data = defaultdict(list)
    with open(f) as i:
        reader = csv.reader(i, delimiter=",")
        for row in reader:
            error_type, sentence = row
            data[error_type].append(sentence)

    return data


def detect_missing_verb(sentence):
    """Return True if the sentence appears to be missing a main verb"""
    # TODO: should this be relocated?
    doc = nlp(sentence)
    for w in doc:
        if w.tag_.startswith('VB') and w.dep_ == 'ROOT':
            return False # looks like there is at least 1 main verb
    return True # we scanned the whole sting and didn't see a main verb

def detect_infinitive_phrase(sentence):
    """Given a string, return true if it is an infinitive phrase fragment"""

    # eliminate sentences without to
    if not 'to' in sentence.lower():
        return False

    doc = nlp(sentence)
    prev_word = None
    for w in doc:
        # if statement will execute exactly once
        if prev_word == 'to':
            if w.dep_ == 'ROOT' and w.tag_.startswith('VB'):
                return True # this is quite likely to be an infinitive phrase
            else:
                return False
        prev_word = w.text.lower()


nlp = spacy.load("en_core_web_lg")


def run_qfragment(sentence):
    result = {}
    is_missing_verb = detect_missing_verb(sentence)
    is_infinitive = detect_infinitive_phrase(sentence)
    if is_missing_verb:  # Lowest priority
        result["missing_verb"] = True

    if is_infinitive:
        result["infinitive_phrase"] = True

    return result



@click.command()
@click.argument("input_file")
def check_grammar(input_file):

    data = read_quill_data(input_file)

    results = []
    concepts_and_sentences = [(c, s) for c in data for s in data[c]]

    for (concept, sentence) in tqdm(concepts_and_sentences):
        response = run_bing(sentence)
        results.append({"concept": concept,
                        "sentence": sentence,
                        "response": response})
        time.sleep(1)

        with open("grammar_bing.json", "w") as o:
            json.dump(results, o)

if __name__ == "__main__":
    check_grammar()
