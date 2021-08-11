FROM openjdk:8
RUN apt-get update && apt-get -y install maven unzip
# ADD https://github.com/essepuntato/LODE/archive/master.zip /lode/
ADD https://github.com/Lostefra/TranslationCoherence/blob/main/lode/master.zip?raw=true /lode/

RUN ls /lode

EXPOSE 9090

RUN cd /lode \
		&& unzip master.zip \
		&& cd LODE-master

WORKDIR /lode/LODE-master
CMD ["mvn", "clean", "jetty:run"]