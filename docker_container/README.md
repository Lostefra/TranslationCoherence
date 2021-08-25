# TranslationCoherence - Services
This docker container provides the following **services** to allow querying and browsing the ontologies and the vocabulary of TranslationCoherence:
 - [**Virtuoso**](http://vos.openlinksw.com/owiki/wiki/VOS) as SPARQL endpoint;
 - [**LODE**](https://essepuntato.it/lode/) for visualising ontologies as HTML pages;
 - [**LodView**](https://www.lodview.it/) for browsing ontology entities as well as vocabulary entities.

### Download
To download this container, simply clone the whole repository using the command:
```
git clone https://github.com/Lostefra/TranslationCoherence
```

The base folder of the container can be reached with
```
cd TranslationCoherence
cd docker_container
```

### Build and run
The project relies on Docker: before executing the commands make sure that the docker daemon is running (see [this link](https://docs.docker.com/config/daemon/#check-whether-docker-is-running)).

To **build** the containers type the following command in the terminal having the root of the container as base folder:
```
$> sudo docker-compose build
```
To **run** the containers type the following command in the terminal having the root of the container as base folder:
```
$> sudo docker-compose up
```

### Usage
Once the containers are up and assuming that `localhost` is the reference host, users can access:
 - the SPARQL endpoint at http://localhost:8890/sparql;
 - LODE at http://localhost:9090/lode;
 - LodView at http://localhost:8080/lodview.

### Examples
#### SPARQL

The following is an example of a SPARQL SELECT query that returns all the ObjectProperties defined in the vocabulary of TranslationCoherence.
```
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT DISTINCT ?p 
WHERE {
  GRAPH<https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/>{
    ?p a owl:ObjectProperty
  }
}
```
#### LodView

The resource
```http://localhost:8080/lodview/translation_coherence.owl/Expression```
can be used to visualise the **HTML page** of the class Expression, defined within the vocabulary.

#### WebVowl

The resource
```http://localhost:8080/webvowl/#iri=https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/translation_coherence.owl```
can be used to visualise the vocabulary with the **VOWL** notation.

#### LODE

The resource
```http://localhost:9090/lode/extract?url=https://raw.githubusercontent.com/Lostefra/TranslationCoherence/main/ontology/translation_coherence.owl```
can be used to visualise the **documentation** about the vocabulary ontology as an HTML page.
