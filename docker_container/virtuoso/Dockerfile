FROM tenforce/virtuoso:virtuoso7.2.5

ARG KG_VERSION

RUN apt-get update && apt-get install -y wget

# # Add ontologies
RUN mkdir /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/translation_coherence.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_VS_en_it_en__sentence4.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en__sentence4.owl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/en_it_en__sentence4.owl /ontologies

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
