# Models

Here we save our best models for several NLP tasks. Models are
stored and versioned with DVC (see also the `data/` directory).

- `models/spacy_sva_xl`: spaCy model for subject-verb agreement
- `models/spacy_3p`: spaCy model for passive, perfect and progressive
errors
- `models/spacy_grammar`: spaCy model for other grammar errors
- `models/spacy_grammar_mix`: spaCy model for all errors that are not covered
by our rule-based or LM-based approach
