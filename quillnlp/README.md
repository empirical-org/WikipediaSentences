# QuillNLP

The main package with Quill's NLP code.

# Structure

```bash
.
├── allennlp        # code and configuration for AllenNLP experiments
├── data            # code for data processing (e.g. diversifying training sets)
├── distillation    # code that has been used for data augmentation in distilling a large BERT model to a small spaCy model
├── grammar         # code for the generation of synthetic grammar training data
├── models          # code for experiments with particular ML models (such as BERT)
├── preprocessing   # code for preprocessing Comprehension data with semantic role labeling
├── spelling        # code for spelling correction
├── README.md       # this file
└── __init__.py
```