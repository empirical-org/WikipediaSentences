import requests
import click
import ndjson
from tqdm import tqdm

GINGER_API_KEY = "dd348723-0ebc-48a4-909b-c4f297697596"
GINGER_API_URL = f"https://sb-partner-services.gingersoftware.com/correction/v1/document?apiKey={GINGER_API_KEY}&lang=US"


def run_ginger(sentence):
    r = requests.post(GINGER_API_URL, sentence.encode('utf-8'))

    corrections = r.json()["GingerTheDocumentResult"]["Corrections"]

    corrections.reverse()

    for correction in corrections:
        print(correction)
        if len(correction["Suggestions"]) > 0:
            sentence = sentence[:correction["From"]] + correction["Suggestions"][0]["Text"] + sentence[correction["To"]+1:]

    print(sentence)
    return sentence


@click.command()
@click.argument("input_file")
@click.argument("output_file")
def run_ginger_on_data(input_file, output_file):
    with open(input_file) as i:
        data = ndjson.load(i)

    corrected_data = []
    for item in tqdm(data):
        corrected_data.append({"text": run_ginger(item["text"]), "label": item["label"]})

    with open(output_file, "w") as o:
        ndjson.dump(corrected_data, o)


if __name__ == "__main__":
    run_ginger_on_data()

#assert run_ginger("This is a test,, and this is another test,, really")== "This is a test, and this is another test, really"
#assert run_ginger("I try to sai goodby, but I choke.") == "I try to say goodbye, but I choke."
