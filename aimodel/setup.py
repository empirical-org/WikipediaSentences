from setuptools import setup

#REQUIRED_PACKAGES = ['oauth2client==3.0.0',
#                     'google-cloud-core==1.3.0',
#                     'google-cloud-logging==1.15.0',
#                     'google-cloud-storage==1.30.0',
#                     'spacy==2.3.2']

REQUIRED_PACKAGES = ['transformers==2.5.1']
#REQUIRED_PACKAGES = ['nltk']

setup(
    name="quill_grammartest",
    version="0.1",
    include_package_data=True,
    scripts=["albert_predictor.py"],
    install_requires=REQUIRED_PACKAGES
)
