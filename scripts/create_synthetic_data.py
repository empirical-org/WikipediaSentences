""" Script to create synthetic data on the basis of backtranslation
with Google translate. Use as follows:

> python scripts/create_synthetic_data.py --lang nl --filename data_file.txt

lang: the language via which to do the backtranslation
data_file: the source file that will be translated line per line

To connect with Google Translate, the environment variable
GOOGLE_APPLICATION_CREDENTIALS needs to refer to the key file
"""

import os

import ndjson
import click

from quillnlp.data.synthetic import generate_synthetic_data


@click.command()
@click.argument('lang')
@click.argument('filename')
def generate(filename, lang):
    with open(filename) as i:
        items = ndjson.load(i)

    translated_items = generate_synthetic_data(items, lang)

    basename = os.path.basename(filename)
    basename_without_extension = os.path.splitext(basename)[0]
    output_name = "{}_{}.ndjson".format(basename_without_extension, lang)

    with open(output_name, "w") as o:
        ndjson.dump(translated_items, o)


if __name__ == '__main__':
    generate()
