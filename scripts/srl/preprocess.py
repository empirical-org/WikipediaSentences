import csv
import json

import click
from quillnlp.preprocessing.srl import *


@click.command()
@click.argument('input_file')
@click.argument('output_file')
@click.option('--prompt', default=None, help='An optional prompt')
def preprocess(input_file, output_file, prompt):

    # 1. Perform SRL
    print("Performing SRL...")
    with open(input_file) as i:
        responses = [line.strip() for line in i]

    srl_results = perform_srl(responses, prompt)

    # 2. Postprocess SRL
    print("Postprocessing SRL...")
    sentences = process_srl_results(srl_results)

    write_output(sentences, output_file)


if __name__ == "__main__":
    preprocess()
