# AI Model

In this directory we keep the Albert model that we deploy with the Google AI engine. This deployment happens as follows:

- Delete the previous version (if any)

`gcloud ai-platform versions delete v2 --model=grammar`

- Set up the new version:

`python setup.py sdist`

- Upload the package to the Google Cloud:

`gsutil cp ./dist/quill_grammartest-0.1.tar.gz gs://quill-grammar-models/packages/quill_grammartest-01.tar.gz`

- Create a new version:

`gcloud beta ai-platform versions create v2 --model grammar --python-version=3.7 --runtime-version=1.15 --package-uris=gs://quill-grammar-models/packages/quill_grammartest-01.tar.gz,gs://quill-grammar-models/packages/torch-1.4.0+cpu-cp37-cp37m-linux_x86_64.whl --machine-type=mls1-c4-m2 --origin=gs://quill-grammar-models/albert-large/ --prediction-class=albert_predictor.BertPredictor`

