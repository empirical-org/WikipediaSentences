from quillnlp.grammar.modelutils import make_request_from_sentence
from quillnlp.grammar.models.albert_predictor import BertPredictor

import time

sentences = ["We should stop eating meat, because meat are bad."]
prompt = "We should stop eating meat, because"
#sentences = ["You are taller then me."]
requests = [make_request_from_sentence(s, prompt) for s in sentences]

for r in requests:
    print(r)

predictor = BertPredictor.from_path("/samba/public/albert/")
results = predictor.predict(requests)
print(results)