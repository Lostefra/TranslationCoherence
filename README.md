# TranslationCoherence
## Exploiting Knowledge Engineering technologies to compare translations across multiple languages

This project aims at exploiting Knowledge Engineering technologies to compare translations across multiple languages by formal reasoning on them. Our goal is to understand which subtle modifications occur when going back and forth from a language to another using off-the-shelf translators (such as [DeepL](https://www.deepl.com/translator)).

We have chosen the open-source [Europarl](https://www.statmt.org/europarl/) parallel corpus for this task. In particular we have taken the first 6 sentences from the English dataset and we have subsequently translated them to German, Italian and Chinese, and then we have translated them back to English. The choice of the languages is not incidental: we aimed at observing whether more differences pop up by translating towards more and more exotic languages with respect to English, thus we picked up a West Germanic language - German - a Latin language - Italian - and a non-European language - Chinese.

Once we have translated the sentences as described above, we employed the machine reader [FRED](http://wit.istc.cnr.it/stlab-tools/fred/) to encode them as knowledge graphs. Starting with 6 sentences translated from 4 languages we ended up with 24 different ontologies.

The attempts we made to address the problem of computing the semantic differences between a pair of ontologies are described in the following sections.

All the code is available on [GitHub](https://github.com/Lostefra/TranslationCoherence/).

## Instructions
This tool runs on Python 3.x. We recommend to install the latest available version of the required packages (listed below in brackets), which requires **Python ≥ 3.7**.

### Install dependency packages using pip
The following packages are required to run the scripts:
- [RDFLib](https://rdflib.readthedocs.io/en/stable/) (6.0.0)
- [spaCy](https://spacy.io/) (3.1.2)
- [nltk](https://www.nltk.org/) (3.6.2)

Assuming that the command ```python``` points to the installation of Python 3 to be used, this can be easily achieved through:
```
python -m pip install -U pip setuptools wheel --user
python -m pip install -U rdflib spacy nltk --user
```
(where the first command installs packages required by ```spacy```, the flag ```--user``` is used for a local installation, and the flag ```-U``` takes care of upgrading the specified packages to the latest available version)

In case of troubles, please refer to the documentation of each single package: [pip](https://pip.pypa.io/en/stable/), [rdflib](https://rdflib.readthedocs.io/en/stable/gettingstarted.html), [spacy](https://spacy.io/usage), [nltk](https://www.nltk.org/install.html).

Before proceeding, we need to download the ```spacy``` model (needed to perform the *tokenization* of words):
```
python -m spacy download en_core_web_sm
```
and the [WordNet<sup>®</sup>](https://wordnet.princeton.edu/) database (needed to recognize synonyms) using ```nltk``` - which requires opening a **Python shell** and executing: 
```
>>> import nltk
>>> nltk.download("wordnet")
```
Both are _one-off operations_, i.e. they need to be run only once for all.

### Clone the repository
To deploy TranslationCoherence, firstly clone the repository (or download it as a ```.zip``` archive):
```
git clone https://github.com/Lostefra/TranslationCoherence/
```
and make sure the current working directory is the root directory of the project:
```
cd TranslationCoherence
```

### Inspecting the results
To inspect the example results provided with this repository, please follow the instructions included in the README file inside subfolder [docker_container](https://github.com/Lostefra/TranslationCoherence/tree/main/docker_container).

### Deploy the tool
There are two Python scripts that allow for the comparison of ontologies: ```main_compare_pair.py``` and ```main_compare_all.py```.
As the names suggest, the first one is designed to run on two ontologies, while the second one takes the ontologies stored in [this folder](https://github.com/Lostefra/TranslationCoherence/tree/main/EuroParl/Paragraph1/turtle) and compares them all pairwise.
To start the scripts, simply run:
```
python main_compare_pair.py
```
(eventually having care of modifying it to compare the desired files), or
```
main_compare_all.py
```
to compare them all at once.

### Report

For further information about our project, read our report [here](https://github.com/Lostefra/TranslationCoherence/blob/main/report.pdf) or download it [here](https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/report.pdf).
