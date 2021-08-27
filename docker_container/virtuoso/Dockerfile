FROM tenforce/virtuoso:virtuoso7.2.5

RUN apt-get update && apt-get install -y wget

# # Add ontologies
RUN mkdir /ontologies

## Vocabulary
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/translation_coherence.owl /ontologies

## EN
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en__sentence1.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en__sentence2.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en__sentence3.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en__sentence4.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en__sentence5.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en__sentence6.owl /ontologies

## EN_IT_EN
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_it_en__sentence1.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_it_en__sentence1.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_it_en__sentence2.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_it_en__sentence2.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_it_en__sentence3.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_it_en__sentence3.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_it_en__sentence4.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_it_en__sentence4.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_it_en__sentence5.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_it_en__sentence5.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_it_en__sentence6.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_it_en__sentence6.owl /ontologies

## EN_DE_EN
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_de_en__sentence1.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_de_en__sentence1.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_de_en__sentence2.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_de_en__sentence2.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_de_en__sentence3.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_de_en__sentence3.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_de_en__sentence4.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_de_en__sentence4.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_de_en__sentence5.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_de_en__sentence5.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_de_en__sentence6.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_de_en__sentence6.owl /ontologies


## EN_CN_EN
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_cn_en__sentence1.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_cn_en__sentence1.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_cn_en__sentence2.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_cn_en__sentence2.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_cn_en__sentence3.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_cn_en__sentence3.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_cn_en__sentence4.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_cn_en__sentence4.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_cn_en__sentence5.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_cn_en__sentence5.owl /ontologies

ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_cn_en__sentence6.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_cn_en__sentence6.owl /ontologies


# Add Virtuoso config
COPY virtuoso.ini /virtuoso.ini

# Add startup script
COPY virtuoso.sh /virtuoso.sh


EXPOSE 8890
EXPOSE 1111

VOLUME /data
WORKDIR /data
VOLUME /usr/local/virtuoso-opensource/share/virtuoso/vad/

CMD ["/bin/bash", "/virtuoso.sh"]
