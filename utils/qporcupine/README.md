# QPorcupine

A library from Quill.org to provide feedback on common grammar errors. Errors detected include spelling errors, fragments, and subject-verb agreement errors.


**NOTE:** This library is currently unstable; please be aware
that updates could include breaking changes.


## Usage

As a module:
```py
from qporcupine import check

feedback  = check('Until she leapt into the air and kissed him.')
print(feedback.human_readable)
```

Expected output:
```
This looks like a subordinating conjunction fragment.
Try removing the subordinating conjunction or adding a main clause.
```

## Installation

#### 1. Install languagetool

qporcupine relies on LanguageTool to function. LanguageTool is an open-source
grammar and spell-checker written in Java. In order to maximize performance, we
will run a languagetool server that qporcupine will be able to connect to.

Change to the opt directory. If you don't have one, create one with `$ sudo mkdir /opt`.
```bash
$ cd /opt
```

Download and unzip languagetool.
```bash
$ sudo curl -O "https://languagetool.org/download/LanguageTool-4.1.zip"
$ sudo unzip LanguageTool-4.1.zip
$ sudo rm LanguageTool-4.1.zip
```

Add the follwing lines to your .bash_profile or system equivalent. Do not
include a trailing slash for the LT_URI.
```bash
alias ltserver='nohup java -cp /opt/LanguageTool-4.1/languagetool-server.jar org.languagetool.server.HTTPServer --port 8081 </dev/null >/dev/null 2>&1 &'
export LT_URI=http://localhost:8081
```

Start the server
```bash
$ ltserver
```

LanguageTool is now running on port 8081. To test that it works try hitting
http://localhost:8081/v2/check?language=en-US&text=my+text in your browser.


#### 2. Download the AllenNLP Constituency Parser

qporcupine uses the [AllenNLP](https://allennlp.org/) library, a suite of open-source
natural-language processing tools developed by the Allen Institute for Artificial
Intelligence. Specifically, qporcupine uses the [constituency parse](http://demo.allennlp.org/constituency-parsing)
model from AllenNLP.

We store the AllenNLP model in `/var/lib/allennlp`. To configure this folder and download the model for use, run:

```bash
$ sudo mkdir /var/lib/allennlp
$ cd /var/lib/allennlp && { sudo curl -O https://s3-us-west-2.amazonaws.com/allennlp/models/elmo-constituency-parser-2018.03.14.tar.gz; cd -;}
```

#### 3. Install qporcupine

One of qporcupine's dependencies is a development branch of the [Pattern.en](https://www.clips.uantwerpen.be/pattern) library, which is not available through PyPi. Consequently, qporcupine must be installed with the `--process-dependency-links` flag, which will install the necessary dependency.

```bash
pip install --process-dependency-links qporcupine
```

#### 4. Configure Spacy Language Model (Optional)

qporcupine uses the `en_core_web_lg` Spacy model by default. If you wish to download and configure another model, do so with

```bash
python -m spacy download <SPACY MODEL NAME>
```

and set

```bash
export QUILL_SPACY_MODEL=<SPACY_MODEL_NAME>
```
