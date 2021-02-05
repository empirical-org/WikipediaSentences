# Data

In this data directory, we keep all the data we need for training,
running and evaluating Quill's Machine Learning experiments. The
data directory is organized in the following way:

- `raw`: raw, unannotated data, for example collected from Quill's users
- `training`: training data for various ML models
- `validated`: validated testing data for evaluating the output of
our models

The `training` and `validated` data are versioned and stored in the
Google cloud bucket `quill-ml-datasets`.

## Grammar model

### Training

The `training` directory mainly contains data for training our
machine-learning models for grammar corrections. This training data
is stored in `ndjson` files, with the filename `error_type.ndjson`.

Every line of these files corresponds to a training item. These
training items have been generated automatically and therefore contain
"synthetic" errors. Every item
is a list with two elements: first the training sentence itself, and
second a dictionary with information about the error in the sentence.
In this dictionary, the `entities` are a list of errors, with for
every error the start character index, the end character index, and the
error type. `Original` is the original sentence that the synthetic
example was generated from. If the sentence does not contain an error,
the `entities` list is empty, and there is no `original` key, since
the training sentence is the same as the original sentence.

Example:
`["This is one of the most gutless Fed's I ever seen.",
{"entities": [[40, 44, "Perfect without have"]],
"original": "This is one of the most gutless Fed's I've ever seen."}]`

### Evaluation

The evaluation data for the grammar model was collected manually. It
consists of a pair of files for every error, such as:

- `passive-with-incorrect-be-negative.txt`
- `passive-with-incorrect-be-positive.txt`

These are simple txt files with one line per sentence. The `positive`
file contains sentences _with_ the grammar error. The `negative` file
contains sentences _without_ the grammar error.

## DVC

The `training` and `validated` data are versioned and stored in the
Google cloud bucket `quill-ml-datasets`. The easiest way to use
this data is to pull this repository from Github and then to `dvc pull`
the data into this `data` directory.