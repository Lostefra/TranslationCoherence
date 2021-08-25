# TranslationCoherence
## Exploiting Knowledge Engineering technologies to compare translations across multiple languages

This project aims at exploiting Knowledge Engineering technologies to compare translations across multiple languages by formal reasoning on them. Our goal is to understand which subtle modifications occur when going back and forth from a language to another using off-the-shelf translators (such as [DeepL](https://www.deepl.com/translator)).

We have chosen the open-source [Europarl](https://www.statmt.org/europarl/) parallel corpus for this task. In particular we have taken the first 6 sentences from the English dataset and we have subsequently translated them to German, Italian and Chinese, and then we have translated them back to English. The choice of the languages is not incidental: we aimed at observing whether more differences pop up by translating towards more and more exotic languages with respect to English, thus we picked up a West Germanic language - German - a Latin language - Italian - and a non-European language - Chinese.

Once we have translated the sentences as described above, we employed the machine reader [FRED](http://wit.istc.cnr.it/stlab-tools/fred/) to encode them as knowledge graphs. Starting with 6 sentences translated from 4 languages we ended up with 24 different ontologies.

The attempts we made to address the problem of computing the semantic differences between a pair of ontologies are described in the following sections.

All the code is available on [GitHub](https://github.com/Lostefra/TranslationCoherence/).

## Instructions
This tool runs on Python 3.

### Install dependency packages
The following packages are required to run the scripts:
- [rdflib](https://rdflib.readthedocs.io/en/stable/)
- [spaCy](https://spacy.io/)
- [nltk](https://www.nltk.org/)

On UNIX systems (Linux+macOS) this can be easily achieved through:
```
pip install rdflib spacy nltk
```
Otherwise, or in case of troubles, please refer to the documentation of each single package.

Before proceeding, we need to download the WordNet database using nltk (needed to recognize synonyms) and the spaCy model (needed to perform the *tokenization* of words). Both are one-off operations, i.e. they need to be run only once for all.
Regarding spaCy, it is sufficient to run the following command:
```
python -m spacy download en_core_web_sm
```
while WordNet requires to open a **Python shell** and run the following line:
```
>>> nltk.download("wordnet")
```

### Clone the repository
To deploy TranslationCoherence, firstly clone the repository (or download it as a ```.zip``` archive):
```
git clone https://github.com/Lostefra/TranslationCoherence/
```
and make sure the current working directory is the root directory of the project:
```
cd TranslationCoherence
```

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

### Inspecting the results
To inspect the results, please follow the instructions included in the README file inside subfolder [docker_container](https://github.com/Lostefra/TranslationCoherence/tree/main/docker_container).
