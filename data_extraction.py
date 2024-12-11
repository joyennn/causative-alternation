import sys
import os
from collections import defaultdict
from tqdm import tqdm

def read_tagged_file(tagged_file) :
    data = []
    with open(tagged_file, "r", encoding = "utf-8") as f :
        raw_data = f.read()
        raw_data = raw_data.split("</s>")


    for sentence in raw_data :
        sentence = sentence.strip()
        if sentence.startswith("<s id") :
            sentence = sentence.split("\n")
            sent_id = sentence[0].strip().replace("<s id=", "")
            sent_id = sent_id.replace(">", "")
            sentence = sentence[1:]

        else :
            sentence = sentence.split("\n")
            sent_id = "0"

        tokens = []
        for token in sentence :
            token = token.strip()
            token = token.split("\t")
            tokens.append(token)

        if tokens != [[""]] :
            data.append((sent_id, tokens))

    return data

def read_verb_list(verb_list_file) :
    verb_list = defaultdict(list)
    with open(verb_list_file, "r", encoding = "utf-8") as f :
        for line in f.readlines() :
            verb = line.strip()
            verb_list[verb] = []

    return verb_list

def count_head_verb(data, verb_dict) :
    for sent_id, sentence in tqdm(data,
                                  total = len(data),
                                  desc = 'Head word sentence extraction',
                                  leave = True,
                                 ):
        s = []
        count_flag = False
        target_word = []

        for token in sentence:
            s.append(token[0])
            if token[2] in verb_dict and token[1] == "VERB" and token[6] == "root" :
                count_flag = True
                target_word.append(token[2])

        if count_flag == True :
            s = ' '.join(s)
            for w in target_word :
                verb_dict[w].append((sent_id, s))

    return verb_dict

def count_passive(data, verb_dict) :
    for sent_id, sentence in tqdm(data,
                                  total = len(data),
                                  desc = 'Passive sentence extraction',
                                  leave = True,
                                 ):
        s = []
        target_word = {}
        target_word_particle = {}
        passive_flag = False
        head_id = -1

        for token in sentence :
            s.append(token[0])

            if token[2] in verb_dict and token[1] == "VERB" and token[6] == "root" :
                target_word[(token[3], token[2])] = []
                target_word_particle[(token[3], token[2])] = []
                head_id = token[3]

            for token in sentence :
                if token[6] == "aux:pass" and token[4] == head_id :
                    passive_flag = True

            for token in sentence :
                if token[6] == "compound:prt" :
                    head_idx = int(token[4]) - 1
                    head_token = sentence[head_idx]
                    if (head_token[3], head_token[2]) in target_word :
                        target_word_particle[(head_token[3], head_token[2])].append(token)

        if target_word != {} :
            s = ' '.join(s)

            for key in target_word :
                if target_word_particle[key] == [] and passive_flag == True :
                    verb_dict[key[1]].append((sent_id, s))

    return verb_dict

def count_transitivity(data, verb_dict) :
    for sent_id, sentence in tqdm(data,
                                  total = len(data),
                                  desc = 'Transitive sentence extraction',
                                  leave = True,
                                 ):
        s = []
        target_word = {}
        target_word_particle = {}
        passive_flag = False
        head_id = -1

        for token in sentence :
            s.append(token[0])
            if token[2] in verb_dict and token[1] == "VERB" and token[6] == "root" :
                target_word_particle[(token[3], token[2])] = []
                head_id = token[3]

            for token in sentence :
                if token[6] == "aux:pass" and token[4] == head_id :
                    passive_flag = True

            for token in sentence : 
                if token[6] == "obj" :
                    head_idx = int(token[4])-1
                    head_token = sentence[head_idx]
                    if (head_token[3], head_token[2]) in target_word :
                        target_word[(head_token[3], head_token[2])].append(token)

            for token in sentence :
                if token[6] == "compound:prt" :
                    head_idx = int(token[4]) - 1
                    head_token = sentence[head_idx]
                    if (head_token[3], head_token[2]) in target_word :
                        target_word_particle[(head_token[3], head_token[2])].append(token)

        if target_word != {} :
            s = ' '.join(s)

            for key in target_word :
                if target_word[key] != [] and target_word_particle[key] == [] and passive_flag == False :
                    verb_dict[key[1]].append((sent_id, s))

    return verb_dict

def count_intransitivity(data, verb_dict) :
    for sent_id, sentence in tqdm(data,
                                  total = len(data),
                                  desc = 'Intransitive sentence extraction',
                                  leave = True,
                                 ):
        s = []
        target_word = {}
        target_word_particle = {}
        passive_flag = False
        head_id = -1

        for token in sentence :
            s.append(token[0])
            if token[2] in verb_dict and token[1] == "VERB" and token[6] == "root" : 
                target_word[(token[3], token[2])] = []
                target_word_particle[(token[3], token[2])] = []
                head_id = token[3]

            for token in sentence : 
                if token[6] == "aux:pass" and token[4] == head_id :
                    passive_flag = True

            for token in sentence : 
                if token[6] == "obj" :
                    head_idx = int(token[4])-1
                    head_token = sentence[head_idx]
                    if (head_token[3], head_token[2]) in target_word :
                        target_word[(head_token[3], head_token[2])].append(token)

            for token in sentence :
                if token[6] == "compound:prt" :
                    head_idx = int(token[4]) - 1
                    head_token = sentence[head_idx]
                    if (head_token[3], head_token[2]) in target_word :
                        target_word_particle[(head_token[3], head_token[2])].append(token)

        if target_word != {} :
            s = ' '.join(s)

            for key in target_word :
                if target_word[key] == [] and target_word_particle[key] == [] and passive_flag == False :
                    verb_dict[key[1]].append((sent_id, s))

    return verb_dict

def write_file(word_verb_dict, folder, header, type):
    count_word_file = f"{folder}/{header}_word_{type}_count.txt"
    sentence_file = f"{folder}/{header}_word_{type}.txt"

    f_count = open(count_word_file, "w", encoding = "utf-8")
    f_sentence = open(sentence_file, "w", encoding = "utf-8")

    for w in word_verb_dict:
        sentence_list = list(set(word_verb_dict[w]))

        if len(sentence_list) != 0:
            print(w, len(sentence_list), sentence_list[0], sep = "\t", file = f_count)

            for sent in sentence_list:
                sent_id = sent[0]
                sentence = sent[1]

                if sentence.startswith("'") or sentence.startswith('"'):
                    sentence = sentence[1:]

                print(w, sent_id, sentence, sep = "\t", file = f_sentence)


        else :
            print(w, len(sentence_list), "[]", sep = "\t", file = f_count)

    f_count.close()
    f_sentence.close()

    return

def main():
    verb_file = "./sample_data/verb_list.txt"
    data_file = "./sample_data/bnc_tagged.txt"
    folder_name = "output"
    header = "output"

    try:
        verb_list = read_verb_list(verb_file)
    except FileNotFoundError:
        print("The verb list file appears to be missing.")
        return

    try:
        data = read_tagged_file(data_file)
    except FileNotFoundError:
        print("The data file analyzed in CoNLL format appears to be missing.")
        return

    head_word_dict = count_head_verb(data, verb_list)
    passive_word_dict = count_passive(data, verb_list)
    transitive_word_dict = count_transitivity(data, verb_list)
    intransitive_word_dict = count_intransitivity(data, verb_list)

    if folder_name != "":
        os.mkdir(folder_name)
        folder_name = "./" + folder_name
    else:
        folder_name = "./"

    write_file(head_word_dict, folder_name, header, "head")
    write_file(passive_word_dict, folder_name, header, "passive")
    write_file(transitive_word_dict, folder_name, header, "transitive")
    write_file(intransitive_word_dict, folder_name, header, "intransitive")

main()
