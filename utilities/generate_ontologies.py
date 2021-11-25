import os
import time

CALLS_PER_MINUTE = 5


def generate_ontology(text, output_file_path, output_file_name):
    # old key = 3772201c-a20c-3d22-8199-380ede20c30e
    cmd = "curl -G -X GET -H \"Accept: text/turtle\" -H \"Authorization: Bearer 53c03c0a-ada6-3a1e-a9cd-3cf74cae7eb1\"" \
          + " --data-urlencode text=\"" + text + "\" -d wsd=true -d semantic-subgraph=\"false\" " \
          + "http://wit.istc.cnr.it/stlab-tools/fred > " + output_file_path + output_file_name
    os.system(cmd)


def get_ontologies():
    # dataset_texts_path = "../Datasets/EuroParl/texts/second_test/first_700_sentences_europarl"
    dataset_texts_path = "../Datasets/WikiNER/texts/first_800_sentences_wikiner"
    input_file = open(dataset_texts_path + "_en.txt", "r")
    input_texts_en = [line.rstrip('\n') for line in input_file.readlines()]
    input_file.close()
    input_file = open(dataset_texts_path + "_de.txt", "r")
    input_texts_de = [line.rstrip('\n') for line in input_file.readlines()]
    input_file.close()
    input_file = open(dataset_texts_path + "_it.txt", "r")
    input_texts_it = [line.rstrip('\n') for line in input_file.readlines()]
    input_file.close()
    input_file = open(dataset_texts_path + "_zh.txt", "r")
    input_texts_zh = [line.rstrip('\n') for line in input_file.readlines()]
    input_file.close()
    input_file = open(dataset_texts_path + "_fi.txt", "r")
    input_texts_fi = [line.rstrip('\n') for line in input_file.readlines()]
    input_file.close()
    input_file = open(dataset_texts_path + "_nl.txt", "r")
    input_texts_nl = [line.rstrip('\n') for line in input_file.readlines()]
    input_file.close()
    input_file = open(dataset_texts_path + "_ko.txt", "r")
    input_texts_ko = [line.rstrip('\n') for line in input_file.readlines()]
    input_file.close()
    inputs_texts = {"en": input_texts_en, "de": input_texts_de, "it": input_texts_it, "zh": input_texts_zh,
                    "fi": input_texts_fi, "nl": input_texts_nl, "ko": input_texts_ko}

    # ontologies_path = "../Datasets/EuroParl/ontologies/second_test/"
    ontologies_path = "../Datasets/WikiNER/ontologies/"

    for language in inputs_texts.keys():
        for i, sentence in enumerate(inputs_texts[language]):
            sentence = sentence.replace("\"", "")
            if len(inputs_texts["en"][i].split(' ')) > 3:
                print(sentence, len(sentence.split(' ')))
                output_file_path = ontologies_path + language + "/"
                output_file_name = language+"_sentence" + str(i+1) + ".ttl"
                start_time = time.time()
                generate_ontology(sentence, output_file_path, output_file_name)
                call_time = time.time() - start_time
                # t = (60 / CALLS_PER_MINUTE) - call_time + 1
                # if t > 0:
                #     time.sleep(t)
                time.sleep(2)


get_ontologies()
# dataset_path = "Datasets/EuroParl/ontologies/second_test/"
# dataset_path = "Datasets/WikiNER/ontologies/"
# folders = [dataset_path + "en/", dataset_path + "de/",
#            dataset_path + "it/", dataset_path + "zh/",
#            dataset_path + "fi/", dataset_path + "nl/",
#            dataset_path + "ko/"]
# valid_ids = get_ids_valid_ontologies(folders)
# print(valid_ids)
# print(len(valid_ids))