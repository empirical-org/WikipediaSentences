import re

from quillopinion.opinioncheck import OpinionCheck


def test_opinion_check_on_quill_data():
    input_file = "tests/data/opinion_sentences.txt"
    labeled_file = "tests/data/opinion_labeled.tsv"

    check = OpinionCheck()

    sentences = []
    with open(input_file) as i:
        for line in i:
            line = line.strip()
            sentences.append(line)

    opinion_labels = {}
    with open(labeled_file) as i:
        for line in i:
            line = line.strip().split("\t")
            if len(line) == 2:
                sentence, label = line

                opinion_labels[sentence] = label

    print("Labeled opinions:", len(list(opinion_labels.keys())))

    opinions = 0
    fp = 0
    fn = 0
    tp = 0
    with open("opinion_output.tsv", "w") as o:
        for sentence in sentences:
            prompt = re.match(".*?(because|, but|, so)", sentence)
            prompt = prompt.group(0) if prompt else ""


            feedback = check.check_from_text(sentence, prompt)
            if feedback:
                opinions += 1
                feedback.sort(key=lambda x: -x.precedence)
                o.write(sentence + "\t" + ",".join([str(opinion) for opinion in feedback]) + "\n")
            else:
                o.write(sentence + "\t\n")

            if sentence in opinion_labels and not feedback:
                print("False negative (missed opinion):\t", sentence)
                fn += 1
            elif sentence not in opinion_labels and feedback:
                print("False positive (incorrectly identified as an "
                      "opinion):\t", sentence, "\t" + feedback[0].type)
                fp += 1
            elif sentence in opinion_labels and feedback:
                tp += 1

    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    f1_score = (2 * precision * recall) / (precision + recall) if precision + recall > 0 else 0

    print(f"Opinions: {opinions}/{len(sentences)} = {opinions/len(sentences)}%")
    print("Precision:", precision)
    print("Recall:", recall)
    print("F1-score:", f1_score)
