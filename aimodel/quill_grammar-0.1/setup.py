from setuptools import setup

REQUIRED_PACKAGES = ['spacy']

setup(
    name="quill_grammar",
    version="0.1",
    include_package_data=True,
    scripts=["spacy_predictor.py"],
    install_requires=REQUIRED_PACKAGES
)
