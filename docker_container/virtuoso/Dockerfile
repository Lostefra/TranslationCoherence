FROM tenforce/virtuoso:virtuoso7.2.5

ARG KG_VERSION

RUN apt-get update && apt-get install -y wget

# COPY download_release.sh /download_release.sh

# RUN /bin/bash /download_release.sh ${KG_VERSION}

# # Add ontologies
RUN mkdir /ontologies
# ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/vocabulary.ttl /ontologies
ADD https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/translation_coherence.owl /ontologies

# COPY download_data.sh /download_data.sh
# RUN /bin/bash /download_data.sh

# # Add DB Unico
# RUN mkdir /d/cis
# ADD http://arco.istc.cnr.it/arco-data/cis/dataset-thesaurus_definizione_del_bene_reperti_archeologici.ttl.gz /d/cis


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
