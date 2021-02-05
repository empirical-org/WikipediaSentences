# Quillgrammar

This is the package for Quill's grammar correction engine.

- `data`: data for grammar correction
- `grammar`: source code for grammar correction
- `models`: (old) spaCy models for grammar correction
- `app.yaml`: config file for deployment on Google's app engine
- `main.py`: the API file for deployment on Google's app engine
- `requirements.txt`: pip requirements file

## Grammar pipeline

The code for the grammar pipeline is in the `grammar` directory.

- `checks`: the individual checks that the pipeline contains. Currently 
there are two checks: a rule-based check (`rules.py`)
and a check that uses a supervised model trained with spaCy (`myspacy.py`).
- `constants`: a selection of constants that is used throughout the 
grammar pipeline
- `error.py`: the error class
- `pipeline.py`: the umbrella where the different components of the 
pipeline are put together
- `postprocess.py`: the postprocessing component where the output
of the pipeline is corrected or specified further
- `verbutils.py`: functions to support the rule-based grammar check
and post-processing step

