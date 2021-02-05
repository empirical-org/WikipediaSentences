import json
import csv


def postprocess_ginger(sentence, response, correction_types, categories):
    corrections = response["GingerTheDocumentResult"]["Corrections"]

    corrections.reverse()
    error_classes = []
    if len(corrections) == 0:
        return "", ""
    else:
        for correction in corrections:
            if len(correction["Suggestions"]) > 0:
                correction_type = correction_types[correction["CorrectionType"]]

                print(correction)
                category = categories[correction["Suggestions"][0]["CategoryId"]]

                error_classes.append(" - ".join([correction_type, category]))
                sentence = sentence[:correction["From"]] + correction["Suggestions"][0]["Text"] + sentence[correction["To"]+1:]

        return error_classes, sentence


def postprocess_languagetool(sentence, response):

    if len(response["matches"]) == 0:
        return "", ""

    corrections = []
    error_classes = []
    for match in response["matches"]:
        start_string_idx = match["offset"]
        end_string_idx = match["offset"] + match["length"]

        error_classes.append(match["rule"]["description"])
        if len(match["replacements"]) > 0:
            replacement = match["replacements"][0]["value"]  # pick the first replacement by default
            corrections.append((start_string_idx, end_string_idx, replacement))

    corrections.sort(key=lambda x: x[0], reverse=True)  # sort on start index

    for correction in corrections:
        start_token_idx, end_token_idx, replacement = correction
        sentence = sentence[:start_token_idx] + replacement + sentence[end_token_idx:]

    return error_classes, sentence


def postprocess_bing(sentence, response):

    if not "flaggedTokens" in response or len(response["flaggedTokens"]) == 0:
        return "", ""

    corrections = response["flaggedTokens"]
    corrections.reverse()
    error_classes = []
    for error in corrections:
        error_type = error["type"]
        error_classes.append(error_type)

        original_token = error["token"]
        start_token_idx = error["offset"]
        end_token_idx = error["offset"] + len(original_token)

        replacement = error["suggestions"][0]["suggestion"]
        sentence = sentence[:start_token_idx] + replacement + sentence[end_token_idx:]

    return error_classes, sentence


def get_ginger_ids(f):
    idmap = {}
    with open(f) as i:
        reader = csv.reader(i, delimiter="\t")

        for row in reader:
            if len(row) == 2:
                idmap[int(row[0])] = row[1]

    return idmap


if __name__ == "__main__":

    with open("sentences_spreadsheet.txt") as i:
        sentences = [line.strip() for line in i]

    f = "grammar_bing.json"

    with open(f) as i:
        data = json.load(i)

    corrected = 0
    corrections = {}

    for item in data:

        sentence = item["sentence"].strip()
        error_classes, corrected_sentence = postprocess_bing(sentence, item["response"])
        corrections[sentence] = (error_classes, corrected_sentence)
        if len(corrected_sentence.strip()) > 1:
            corrected += 1

    with open("grammar_bing.csv", "w") as o:
        writer = csv.writer(o, delimiter=";")
        for sentence in sentences:
            if sentence in corrections:
                writer.writerow([", ".join(corrections[sentence][0]), corrections[sentence][1]])
            else:
                writer.writerow(["", ""])

    print("Sentences corrected:", corrected)
    print("Total sentences:", len(data))