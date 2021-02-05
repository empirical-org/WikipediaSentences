import os
import click
import ndjson

@click.command()
@click.argument('input_file')
@click.option('--prompt', default="", help='Prompt for the responses')
def prepare_data(input_file, prompt):

    target_path = "data/interim"

    data = []
    with open(input_file) as i:
        for line in i:
            line = line.strip().split("\t")
            if len(line) >= 2:
                text = " ".join([prompt, line[0]])
                labels = [l.strip() for l in line[1:] if len(l.strip()) > 0]
                data.append({"text": text, "labels": labels})

    file_out = os.path.basename(input_file).replace(".tsv", "_withprompt.ndjson")

    with open(file_out, "w") as o:
        ndjson.dump(data, o)


if __name__ == "__main__":
    prepare_data()
