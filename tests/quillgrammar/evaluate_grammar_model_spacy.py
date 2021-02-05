import csv
from collections import Counter

import yaml

from tqdm import tqdm
from sklearn.metrics import classification_report, precision_recall_fscore_support, confusion_matrix
from sklearn.preprocessing import MultiLabelBinarizer

from quillgrammar.grammar.constants import GrammarError
from quillgrammar.grammar.pipeline import GrammarPipeline
from tests.quillgrammar.error_files import files

config_file = "grammar_config_test.yaml"

grouping = {
    GrammarError.SIMPLE_PAST_INSTEAD_OF_PRESENT_PERFECT.value: "Past instead of perfect",
    GrammarError.SIMPLE_PAST_INSTEAD_OF_PAST_PERFECT.value: "Past instead of perfect",
    GrammarError.PERFECT_PROGRESSIVE_WITH_INCORRECT_BE_AND_WITHOUT_HAVE.value: "Perfect progressive error",
    GrammarError.PERFECT_PROGRESSIVE_WITHOUT_HAVE.value: "Perfect progressive error",
    GrammarError.PASSIVE_WITHOUT_BE.value: "Passive be error",
    GrammarError.PASSIVE_WITH_INCORRECT_BE.value: "Passive be error",
    GrammarError.PAST_TENSE_INSTEAD_OF_PARTICIPLE.value: "Past-participle",
    GrammarError.PERFECT_WITH_INCORRECT_PARTICIPLE.value: "Past-participle",
    GrammarError.PASSIVE_WITH_SIMPLE_PAST_INSTEAD_OF_PARTICIPLE.value: "Past-participle",
    GrammarError.PASSIVE_WITH_INCORRECT_PARTICIPLE.value: "Past-participle",
    GrammarError.PASSIVE_PERFECT_WITH_INCORRECT_PARTICIPLE.value: "Past-participle"
}

grouping = {
    GrammarError.PASSIVE_WITH_INCORRECT_BE.value: "Passive been error",
    GrammarError.PASSIVE_PERFECT_WITHOUT_HAVE.value: "Passive been error"
}


def test_grammar_pipeline():

    with open(config_file) as i:
        config = yaml.load(i, Loader=yaml.FullLoader)

    pipeline = GrammarPipeline(config)

    predicted_labels = []
    correct_labels = []

    data = []
    for f in files:
        if f["error"] in config["errors"] and config["errors"][f["error"]] > 0:
            if "positive" in f:
                with open(f["positive"]) as i:
                    for line in i:
                        data.append((line.strip(), "", f["error"]))
            if "negative" in f:
                with open(f["negative"]) as i:
                    for line in i:
                        data.append((line.strip(), "", "Correct"))

    import random
    random.seed(42)
    random.shuffle(data)

    suffix = "_before"

    with open(f"grammar_output{suffix}.tsv", "w") as o:
        csv_writer = csv.writer(o, delimiter="\t")

        for (sentence, prompt, error) in tqdm(data, desc="Predicting errors"):

            errors = pipeline.check(sentence, prompt)
            predicted_error_types = []
            if len(errors) > 0:
                error_type = grouping.get(errors[0].type, errors[0].type)
                predicted_error_types.append(error_type)
            else:
                predicted_error_types.append("Correct")

            predicted_labels.append(predicted_error_types)
            error = grouping.get(error, error)

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

    with open(f"evaluation_report{suffix}.csv", "w") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["Error type", "Precision", "Recall", "F0.5-score"])
        for row in rows:
            writer.writerow(row)

    # print(confusion_matrix(correct_labels, predicted_labels, labels=mlb.classes_))

    cm = confusion_matrix(correct_labels, predicted_labels, labels=mlb.classes_)
    with open(f"confusion_matrix{suffix}.tsv", "w") as o:
        csv_writer = csv.writer(o, delimiter="\t")
        csv_writer.writerow(mlb.classes_)
        for label, row in zip(mlb.classes_, cm):
            row = [str(e) for e in row]
            csv_writer.writerow([label] + row)

    misclassifications = Counter()
    for (c, p) in zip(correct_labels, predicted_labels):
        if c != p:
            misclassifications.update([f"{c[0]} as {p[0]}"])

    print("Most common misclassifications:")
    for x in misclassifications.most_common(30):
        print(x)