from setuptools import setup
from os import path

# read contents of our README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='qporcupine',
      version='0.0.4',
      description='Grammar error detection and feedback',
      url='https://github.com/empirical-org/Quill-NLP-Tools-and-Datasets',
      author='Quill.org',
      author_email='max@quill.org',
      license='MIT',
      packages=['qporcupine'],
      install_requires=[
        'allennlp==0.5.1',
        'flask==0.12.2',
        'gunicorn==19.7.1',
        'nltk==3.2.5',
        'numpy==1.14.2',
        'pandas==0.19.2',
        'pathlib==1.0.1',
        'requests==2.18.4',
        'spacy==2.0.12',
        'sqlalchemy==1.2.6',
        'tensorflow==1.5.1',
        'textacy==0.6.2',
        'tflearn==0.3.2'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False,
      long_description=long_description,
      long_description_content_type='text/markdown')
