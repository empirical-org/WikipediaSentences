import csv
import yaml

from tqdm import tqdm
from sklearn.metrics import classification_report, precision_recall_fscore_support
from sklearn.preprocessing import MultiLabelBinarizer

from quillgrammar.grammar.pipeline import GrammarPipeline
from tests.quillgrammar.error_files import files

config_file = "grammar_config_production.yaml"


def test_grammar_pipeline():

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    predicted_labels = []
    correct_labels = []

    data = []
    for f in files:
        error_label = f["error"].replace("_", " ")
        if error_label in config["errors"] and config["errors"][error_label] == 1:
            with open(f["positive"]) as i:
                for line in i:
                    data.append((line.strip(), "", error_label))
            with open(f["negative"]) as i:
                for line in i:
                    data.append((line.strip(), "", "Correct"))

    import random
    random.seed(42)
    random.shuffle(data)

    with open("grammar_output.tsv", "w") as o:
        csv_writer = csv.writer(o, delimiter="\t")

        for (sentence, prompt, error) in tqdm(data, desc="Predicting errors"):

            errors = pipeline.check(sentence, prompt)
            predicted_error_types = []
            if len(errors) > 0:
                predicted_error_types.append(errors[0].type)
            else:
                predicted_error_types.append("Correct")

            predicted_labels.append(predicted_error_types)
            correct_label = [] if not error else [error]
            correct_labels.append(correct_label)

            csv_writer.writerow([sentence, "Cor:" + ";".join(correct_label),
                                 "Pred:" + ";".join(predicted_error_types),
                                 ";".join([str(e) for e in errors])])


    mlb = MultiLabelBinarizer()
    correct_labels_binary = mlb.fit_transform(correct_labels)
    predicted_labels_binary = mlb.transform(predicted_labels)

    print(classification_report(correct_labels_binary,
                                predicted_labels_binary, target_names=mlb.classes_))

    p, r, f1, s = precision_recall_fscore_support(correct_labels_binary, predicted_labels_binary, beta=0.5)
    rows = zip(mlb.classes_, p, r, f1, s)

    with open("evaluation_report.csv", "w") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["Error type", "Precision", "Recall", "F0.5-score"])
        for row in rows:
            writer.writerow(row)

