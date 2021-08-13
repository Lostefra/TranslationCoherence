from graph_utilities.compare_pair import compare_pair
import os

en_sentence = "EuroParl/Paragraph1/turtle/en/en_sentence"

ontologies_dir = os.path.join("EuroParl", "Paragraph1", "turtle")
for lang in os.listdir(ontologies_dir):
    lang_dir = os.path.join(ontologies_dir, lang)
    if os.path.isdir(lang_dir):
        for file in os.listdir(lang_dir):
            filename = os.path.join(lang_dir, file)
            if not lang == "en" and filename.endswith(".ttl"):
                lang_1 = "en/en"
                lang_2 = lang + "/en_" + lang + "_en"
                sentence = filename.split(".")[0][-1]
                compare_pair(lang_1, en_sentence + sentence + ".ttl", lang_2, filename, "sentence" + sentence)
