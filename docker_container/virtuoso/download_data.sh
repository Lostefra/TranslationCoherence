#!/bin/bash

mkdir /ontologies 
cd /ontologies/

wget https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/vocabulary.ttl
wget https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/g1.ttl
wget https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/g2.ttl
wget https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/output.ttl
wget https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/translation_coherence_vocabulary.ttl