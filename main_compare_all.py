from graph_utilities.compare_pair import compare_pair
from graph_utilities.deploy_graph import serialize_graph
from utilities.utility_functions import get_ids_valid_ontologies
import os

# Comment or uncomment choosing the dataset
# dataset_path = "Datasets/EuroParl/ontologies/second_test/"
# ontologies_dir = os.path.join("Datasets/EuroParl", "ontologies", "second_test")
dataset_path = "Datasets/WikiNER/ontologies/"
ontologies_dir = os.path.join("Datasets", "WikiNER", "ontologies")

sentences_output_folder = dataset_path + "sentences/"
comparisons_output_folder = dataset_path + "comparisons/"
en_sentence = dataset_path + "en/en_sentence"


folders = [dataset_path + "en/", dataset_path + "de/",
           dataset_path + "it/", dataset_path + "zh/",
           dataset_path + "fi/", dataset_path + "nl/",
           dataset_path + "ko/"]
valid_ids = get_ids_valid_ontologies(folders)
# WikiNER sentences broken
# DE
# valid_ids.remove(101)
# valid_ids.remove(116)
# valid_ids.remove(155)
# valid_ids.remove(180)
# valid_ids.remove(225)
# valid_ids.remove(349)
# valid_ids.remove(405)
# valid_ids.remove(432)
# valid_ids.remove(483)
# valid_ids.remove(564)
# valid_ids.remove(641)
# valid_ids.remove(678)
# valid_ids.remove(734)
# valid_ids.remove(744)
# # IT
# valid_ids.remove(40)
# valid_ids.remove(55)
# valid_ids.remove(210)
# valid_ids.remove(232)
# valid_ids.remove(274)
# valid_ids.remove(304)
# valid_ids.remove(342)
# valid_ids.remove(414)
# valid_ids.remove(630)
# valid_ids.remove(670)
# valid_ids.remove(711)
# valid_ids.remove(745)
# # ZH
# valid_ids.remove(102)
# valid_ids.remove(103)
# # FI
# valid_ids.remove(104)
# valid_ids.remove(125)
# valid_ids.remove(290)
# valid_ids.remove(511)
# valid_ids.remove(777)
# # NL
# valid_ids.remove(41)
# valid_ids.remove(212)
# valid_ids.remove(339)
# valid_ids.remove(355)
# valid_ids.remove(537)
# valid_ids.remove(547)
# valid_ids.remove(760)
# valid_ids.remove(762)
# # KO
# valid_ids.remove(48)
# valid_ids.remove(109)
# valid_ids.remove(132)
# valid_ids.remove(149)
# valid_ids.remove(181)
# valid_ids.remove(252)
# valid_ids.remove(410)
# valid_ids.remove(543)
# valid_ids.remove(574)
# valid_ids.remove(668)
# valid_ids.remove(800)
# EuroParl sentences broken
# # EN/DE
# valid_ids.remove(9)
# valid_ids.remove(18)
# valid_ids.remove(195)
# valid_ids.remove(242)
# valid_ids.remove(333)
# valid_ids.remove(463)
# valid_ids.remove(532)
# valid_ids.remove(594)
# valid_ids.remove(631)
# # IT
# valid_ids.remove(403)
# # ZH
# valid_ids.remove(57)
# valid_ids.remove(226)
# # FI
# valid_ids.remove(462)
# valid_ids.remove(573)
# # NL
# valid_ids.remove(662)
# # KO
# valid_ids.remove(53)
# valid_ids.remove(358)
# valid_ids.remove(381) # exceeded quota
# valid_ids.remove(391) # exceeded quota
# valid_ids.remove(668)

for lang in ["ko"]:
    lang_dir = os.path.join(ontologies_dir, lang)
    if os.path.isdir(lang_dir):
        for id_sentence in valid_ids:
            lang_1 = "en/en"
            lang_2 = lang + "/" + lang
            lang_sentence = dataset_path + lang + "/" + lang + "_sentence"
            g1, g1_name, g2, g2_name, result_graph, rg_name = \
                compare_pair(lang_1, en_sentence + str(id_sentence) + ".ttl",
                             lang_2, lang_sentence + str(id_sentence) + ".ttl", "sentence" + str(id_sentence))
            serialize_graph(g1, g1_name, g2, g2_name, sentences_output_folder, result_graph, rg_name,
                            comparisons_output_folder, format='turtle')
