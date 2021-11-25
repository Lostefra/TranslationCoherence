#from googletrans import Translator
#from translate import Translator

# deepl_key = 'ef10af44-f658-5c9d-f3b0-0c1e0f4b2e6c:fx'
# translators = dict()
# translators["it"] = Translator(provider='deepl', to_lang='it', secret_access_key=deepl_key)
# translators["de"] = Translator(provider='deepl', to_lang='de', secret_access_key=deepl_key)
# translators["chi"] = Translator(provider='deepl', to_lang='chi', secret_access_key=deepl_key)
import os
import json


DeepL = True
ArgosTranslator = False


def translate(text, source_language, target_language, DeepL = False, ArgoTranslator = True):
    # DeepL
    if DeepL:
        cmd = "curl https://api-free.deepl.com/v2/translate -d auth_key=ef10af44-f658-5c9d-f3b0-0c1e0f4b2e6c:fx" \
               + " -d \"text=" + text \
               + "\" -d \"source_lang=" + source_language \
               + "\" -d \"target_lang=" + target_language + "\" > response.json"
        os.system(cmd)
        with open('response.json') as json_file:
            response = json.load(json_file)
        return response['translations'][0]['text']
    #Argos
    elif ArgosTranslator:
        cmd = "argos-translate --from-lang " + source_language.lower() + " --to-lang " + target_language.lower() + \
              " \"" + text.replace("\"", "") + "\" > response.json"
        print(cmd)
        res = os.system(cmd)
        if res:
            return ""
        with open('response.json') as text_file:
            response = text_file.read()
        return response.rstrip('\n')


languages = ['DE', 'IT', 'ZH' 'FI', 'NL', 'KO']

input_file = open("../Datasets/EuroParl/texts/first_test/first_200_sentences_europarl_en.txt", "r")
# input_file = open("../WikiNER/texts/first_800_sentences_wikiner_en.txt", "r")
source_texts = [line.rstrip('\n') for line in input_file.readlines()]
input_file.close()

# print(len(source_texts))
# print(source_texts)

for language in languages:
    output_texts = []
    intermediate_texts = []
    for i, text in enumerate(source_texts):
        translation_from_en = translate(text, "EN", language, DeepL, ArgosTranslator)
        intermediate_texts.append(translation_from_en)
        if DeepL:
            translation_to_en = translate(translation_from_en, language, "EN-GB", DeepL, ArgosTranslator)
        elif ArgosTranslator:
            translation_to_en = translate(translation_from_en, language, "EN", DeepL, ArgosTranslator)
        output_texts.append(translation_to_en)
        # print("translation of ", text, " to ", language, "\n", translation_from_en)
        # print("\tsecond step: ", translation_to_en)
        output_file = open("../EuroParl/texts/first_test/first_200_sentences_europarl_" + language.lower() + ".txt", "a")
        output_file.write(translation_to_en + "\n")
        # output_file.write(str.join("\n", output_texts))
        output_file.close()
        output2_file = open("../EuroParl/texts/first_test/intermediate_first_200_sentences_europarl_" + language.lower() + ".txt", "a")
        output2_file.write(translation_from_en + "\n")
        # output2_file.write(str.join("\n", intermediate_texts))
        output2_file.close()
