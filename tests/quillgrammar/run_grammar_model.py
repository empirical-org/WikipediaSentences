import csv
import yaml

from tqdm import tqdm

from quillgrammar.grammar.constants import GrammarError
from quillgrammar.grammar.pipeline import GrammarPipeline

csv_file = "quillgrammar/data/combined_turk_data.csv"
# csv_file = "../../data/quill/grammer_response_dump_generic_2020_07_06.csv"
config_file = "grammar_config_test.yaml"


def read_csv_file(f):
    data = []
    with open(f) as i:
        reader = csv.reader(i)
        for row in reader:
            sentence, prompt, *other = row

            # Some prompts in the file are not complete. Correct those.
            if not (prompt.strip().endswith("so") or
                    prompt.strip().endswith("because") or
                    prompt.strip().endswith("but")):

                if sentence.startswith(prompt.strip() + " so"):
                    prompt = prompt + " so"
                elif sentence.startswith(prompt.strip() + " but"):
                    prompt = prompt + " but"
                elif sentence.startswith(prompt.strip() + ", so"):
                    prompt = prompt + ", so"
                elif sentence.startswith(prompt.strip() + ", but"):
                    prompt = prompt + ", but"
                elif sentence.startswith(prompt.strip() + " because"):
                    prompt = prompt + " because"

            if sentence.startswith(prompt):
                data.append((sentence, prompt))
            else:
                data.append((sentence, ""))
    return data


grouping = {
    GrammarError.PASSIVE_WITH_INCORRECT_BE.value: "Passive been error",
    GrammarError.PASSIVE_PERFECT_WITHOUT_HAVE.value: "Passive been error"
}


def test_grammar_pipeline():

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    data = read_csv_file(csv_file)

    with open("combined_turk_output_20201030.tsv", "w") as o:
        csv_writer = csv.writer(o, delimiter="\t")

        for (sentence, prompt) in tqdm(data, desc="Predicting errors"):

            #sentence = correct_sentence_with_bing(sentence)

            try:
                errors = pipeline.check(sentence, prompt)
            except IndexError:
                errors = []

            predicted_error = None
            if len(errors) > 0:
                predicted_error = errors[0]

            if predicted_error is None:
                csv_writer.writerow([sentence, "", "", ""])
            else:
                error_type = grouping.get(predicted_error.type, predicted_error.type)

                csv_writer.writerow([sentence, error_type,
                                    predicted_error.index, predicted_error.text])


test_grammar_pipeline()
