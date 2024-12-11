{
  "cells": [
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "2Lfa6NV8axoV"
      },
      "outputs": [],
      "source": [
        "\"\"\"\n",
        "파일 실행을 위해서 필요한 모듈(module, 필요한 기능들의 모음이라고 생각하시면 됩니다)을 불러오는 부분입니다.\n",
        "jupyter notebook 또는 google colab에서 사용하는 경우 \"import sys\" 부분은 삭제해도 무방합니다.\n",
        "\"\"\"\n",
        "import sys\n",
        "import os\n",
        "from collections import defaultdict\n",
        "from tqdm import tqdm"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "QoJFq-LqUlVA"
      },
      "outputs": [],
      "source": [
        "\"\"\"\n",
        "CoLLN format으로 분석된 파일을 읽어오는 부분입니다.\n",
        "id 부분에 대한 처리 (if sentence.startswith(\"<s id\"): ... 로 시작하는 부분) 이 있기 때문에\n",
        "tagger.py 를 이용하여 만들어진 파일만 제대로 읽어들일 수 있습니다.\n",
        "(sentence_id, sentence)의 tuple 형태로 list에 누적되어 저장된 값을 리턴합니다.\n",
        "id 값이 0으로 되어 있는 경우는 tagging 과정에서 오류로 인해 id 값이 제대로 부여받지 못한 경우입니다.\n",
        "\"\"\"\n",
        "def read_tagged_file(tagged_file) :\n",
        "    data = []\n",
        "    with open(tagged_file, \"r\", encoding = \"utf-8\") as f :\n",
        "        raw_data = f.read()\n",
        "        raw_data = raw_data.split(\"</s>\")\n",
        "\n",
        "\n",
        "    for sentence in raw_data :\n",
        "        sentence = sentence.strip()\n",
        "        if sentence.startswith(\"<s id\") :\n",
        "            sentence = sentence.split(\"\\n\")\n",
        "            sent_id = sentence[0].strip().replace(\"<s id=\", \"\")\n",
        "            sent_id = sent_id.replace(\">\", \"\")\n",
        "            sentence = sentence[1:]\n",
        "\n",
        "        else :\n",
        "            sentence = sentence.split(\"\\n\")\n",
        "            sent_id = \"0\"\n",
        "\n",
        "        tokens = []\n",
        "        for token in sentence :\n",
        "            token = token.strip()\n",
        "            token = token.split(\"\\t\")\n",
        "            tokens.append(token)\n",
        "\n",
        "        if tokens != [[\"\"]] :\n",
        "            data.append((sent_id, tokens))\n",
        "\n",
        "    return data"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "Gb7r29MXUsgP"
      },
      "outputs": [],
      "source": [
        "\"\"\"\n",
        "verb_list.txt 와 같은 동사의 리스트를 읽어들이는 함수입니다.\n",
        "동사의 리스트를 리턴합니다.\n",
        "\"\"\"\n",
        "def read_verb_list(verb_list_file) :\n",
        "    verb_list = defaultdict(list)\n",
        "    with open(verb_list_file, \"r\", encoding = \"utf-8\") as f :\n",
        "        for line in f.readlines() :\n",
        "            verb = line.strip()\n",
        "            verb_list[verb] = []\n",
        "\n",
        "    return verb_list"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "wYcv0lS7T2ho"
      },
      "outputs": [],
      "source": [
        "\"\"\"\n",
        "동사 리스트에 있는 동사가 head verb로 사용된 경우를 추출하는 함수입니다.\n",
        "\"\"\"\n",
        "def count_head_verb(data, verb_dict) :\n",
        "    for sent_id, sentence in tqdm(data,\n",
        "                                  total = len(data),\n",
        "                                  desc = 'Head word sentence extraction',\n",
        "                                  leave = True,\n",
        "                                 ):\n",
        "        s = []\n",
        "        count_flag = False\n",
        "        target_word = []\n",
        "\n",
        "        for token in sentence:\n",
        "            s.append(token[0])\n",
        "            if token[2] in verb_dict and token[1] == \"VERB\" and token[6] == \"root\" :\n",
        "                count_flag = True\n",
        "                target_word.append(token[2])\n",
        "\n",
        "        if count_flag == True :\n",
        "            s = ' '.join(s)\n",
        "            for w in target_word :\n",
        "                verb_dict[w].append((sent_id, s))\n",
        "\n",
        "    return verb_dict"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "XHWViWjuU5ue"
      },
      "outputs": [],
      "source": [
        "\"\"\"\n",
        "동사 리스트에 있는 동사가 수동태로 사용된 경우를 추출하는 함수입니다.\n",
        "\"\"\"\n",
        "def count_passive(data, verb_dict) :\n",
        "    for sent_id, sentence in tqdm(data,\n",
        "                                  total = len(data),\n",
        "                                  desc = 'Passive sentence extraction',\n",
        "                                  leave = True,\n",
        "                                 ):\n",
        "        s = []\n",
        "        target_word = {}\n",
        "        target_word_particle = {}\n",
        "        passive_flag = False\n",
        "        head_id = -1\n",
        "\n",
        "        for token in sentence :\n",
        "            s.append(token[0])\n",
        "\n",
        "            if token[2] in verb_dict and token[1] == \"VERB\" and token[6] == \"root\" :\n",
        "                target_word[(token[3], token[2])] = []\n",
        "                target_word_particle[(token[3], token[2])] = []\n",
        "                head_id = token[3]\n",
        "\n",
        "            for token in sentence :\n",
        "                if token[6] == \"aux:pass\" and token[4] == head_id :\n",
        "                    passive_flag = True\n",
        "\n",
        "            for token in sentence :\n",
        "                if token[6] == \"compound:prt\" :\n",
        "                    head_idx = int(token[4]) - 1\n",
        "                    head_token = sentence[head_idx]\n",
        "                    if (head_token[3], head_token[2]) in target_word :\n",
        "                        target_word_particle[(head_token[3], head_token[2])].append(token)\n",
        "\n",
        "        if target_word != {} :\n",
        "            s = ' '.join(s)\n",
        "\n",
        "            for key in target_word :\n",
        "                if target_word_particle[key] == [] and passive_flag == True :\n",
        "                    verb_dict[key[1]].append((sent_id, s))\n",
        "\n",
        "    return verb_dict"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "T5WVKNboVCZf"
      },
      "outputs": [],
      "source": [
        "\"\"\"\n",
        "동사 리스트에 있는 동사가 타동사로 사용된 경우를 추출하는 함수입니다.\n",
        "\"\"\"\n",
        "def count_transitivity(data, verb_dict) :\n",
        "    for sent_id, sentence in tqdm(data,\n",
        "                                  total = len(data),\n",
        "                                  desc = 'Transitive sentence extraction',\n",
        "                                  leave = True,\n",
        "                                 ):\n",
        "        s = []\n",
        "        target_word = {}\n",
        "        target_word_particle = {}\n",
        "        passive_flag = False\n",
        "        head_id = -1\n",
        "\n",
        "        for token in sentence :\n",
        "            s.append(token[0])\n",
        "            if token[2] in verb_dict and token[1] == \"VERB\" and token[6] == \"root\" : #본동사로 사용되는 동사\n",
        "                target_word[(token[3], token[2])] = []\n",
        "                target_word_particle[(token[3], token[2])] = []\n",
        "                head_id = token[3]\n",
        "\n",
        "            for token in sentence : #수동태의 경우 flag를 True 로 설정\n",
        "                if token[6] == \"aux:pass\" and token[4] == head_id :\n",
        "                    passive_flag = True\n",
        "\n",
        "            for token in sentence : #목적어가 있는지 확인\n",
        "                if token[6] == \"obj\" :\n",
        "                    head_idx = int(token[4])-1\n",
        "                    head_token = sentence[head_idx]\n",
        "                    if (head_token[3], head_token[2]) in target_word :\n",
        "                        target_word[(head_token[3], head_token[2])].append(token)\n",
        "\n",
        "            for token in sentence : #동사구 제외\n",
        "                if token[6] == \"compound:prt\" :\n",
        "                    head_idx = int(token[4]) - 1\n",
        "                    head_token = sentence[head_idx]\n",
        "                    if (head_token[3], head_token[2]) in target_word :\n",
        "                        target_word_particle[(head_token[3], head_token[2])].append(token)\n",
        "\n",
        "        if target_word != {} :\n",
        "            s = ' '.join(s)\n",
        "\n",
        "            for key in target_word :\n",
        "                if target_word[key] != [] and target_word_particle[key] == [] and passive_flag == False :\n",
        "                    verb_dict[key[1]].append((sent_id, s))\n",
        "\n",
        "    return verb_dict"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "XoMJWQjTVI8-"
      },
      "outputs": [],
      "source": [
        "\"\"\"\n",
        "동사 리스트에 있는 동사가 자동사로 사용된 경우를 추출하는 함수입니다.\n",
        "\"\"\"\n",
        "def count_intransitivity(data, verb_dict) :\n",
        "    for sent_id, sentence in tqdm(data,\n",
        "                                  total = len(data),\n",
        "                                  desc = 'Intransitive sentence extraction',\n",
        "                                  leave = True,\n",
        "                                 ):\n",
        "        s = []\n",
        "        target_word = {}\n",
        "        target_word_particle = {}\n",
        "        passive_flag = False\n",
        "        head_id = -1\n",
        "\n",
        "        for token in sentence :\n",
        "            s.append(token[0])\n",
        "            if token[2] in verb_dict and token[1] == \"VERB\" and token[6] == \"root\" : #본동사로 사용되는 동사\n",
        "                target_word[(token[3], token[2])] = []\n",
        "                target_word_particle[(token[3], token[2])] = []\n",
        "                head_id = token[3]\n",
        "\n",
        "            for token in sentence : #수동태의 경우 flag를 True 로 설정\n",
        "                if token[6] == \"aux:pass\" and token[4] == head_id :\n",
        "                    passive_flag = True\n",
        "\n",
        "            for token in sentence : #목적어가 있는지 확인\n",
        "                if token[6] == \"obj\" :\n",
        "                    head_idx = int(token[4])-1\n",
        "                    head_token = sentence[head_idx]\n",
        "                    if (head_token[3], head_token[2]) in target_word :\n",
        "                        target_word[(head_token[3], head_token[2])].append(token)\n",
        "\n",
        "            for token in sentence : #동사구 제외\n",
        "                if token[6] == \"compound:prt\" :\n",
        "                    head_idx = int(token[4]) - 1\n",
        "                    head_token = sentence[head_idx]\n",
        "                    if (head_token[3], head_token[2]) in target_word :\n",
        "                        target_word_particle[(head_token[3], head_token[2])].append(token)\n",
        "\n",
        "        if target_word != {} :\n",
        "            s = ' '.join(s)\n",
        "\n",
        "            for key in target_word :\n",
        "                if target_word[key] == [] and target_word_particle[key] == [] and passive_flag == False :\n",
        "                    verb_dict[key[1]].append((sent_id, s))\n",
        "\n",
        "    return verb_dict"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "zmyCwnKCT2hq"
      },
      "outputs": [],
      "source": [
        "\"\"\"\n",
        "각 경우마다 만들어진 동사-문장 리스트를 이용하여 새로운 텍스트 파일을 만드는 부분입니다.\n",
        "\"\"\"\n",
        "def write_file(word_verb_dict, folder, header, type):\n",
        "    count_word_file = f\"{folder}/{header}_word_{type}_count.txt\"\n",
        "    sentence_file = f\"{folder}/{header}_word_{type}.txt\"\n",
        "\n",
        "    f_count = open(count_word_file, \"w\", encoding = \"utf-8\")\n",
        "    f_sentence = open(sentence_file, \"w\", encoding = \"utf-8\")\n",
        "\n",
        "    for w in word_verb_dict:\n",
        "        sentence_list = list(set(word_verb_dict[w]))\n",
        "\n",
        "        if len(sentence_list) != 0:\n",
        "            print(w, len(sentence_list), sentence_list[0], sep = \"\\t\", file = f_count)\n",
        "\n",
        "            for sent in sentence_list:\n",
        "                sent_id = sent[0]\n",
        "                sentence = sent[1]\n",
        "\n",
        "                if sentence.startswith(\"'\") or sentence.startswith('\"'):\n",
        "                    sentence = sentence[1:]\n",
        "\n",
        "                print(w, sent_id, sentence, sep = \"\\t\", file = f_sentence)\n",
        "\n",
        "\n",
        "        else :\n",
        "            print(w, len(sentence_list), \"[]\", sep = \"\\t\", file = f_count)\n",
        "\n",
        "    f_count.close()\n",
        "    f_sentence.close()\n",
        "\n",
        "    return"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "Km5yiwuQT2hq"
      },
      "outputs": [],
      "source": [
        "\"\"\"\n",
        "위에서 정의한 함수들을 순서에 맞게 사용하도록 하는 main 함수입니다.\n",
        "\"\"\"\n",
        "def main():\n",
        "    #verb_file = input(\"동사 리스트가 들어있는 파일을 확장자까지 입력하세요. \") #동사 리스트를 입력받는 부분\n",
        "    verb_file = \"./sample_data/verb_list.txt\"\n",
        "    #data_file = input(\"CoNLL format으로 분석되어 있는 데이터 파일을 확장자까지 입력하세요. \") #태깅 결과가 있는 파일을 입력받는 부분\n",
        "    data_file = \"./sample_data/bnc_tagged.txt\"\n",
        "    #folder_name = input(\"새로 생성할 폴더 이름을 입력하세요. 새로운 폴더를 만들고 싶지 않은 경우 엔터를 치면 됩니다. \")\n",
        "    folder_name = \"output\" #신규생성폴더\n",
        "    #header = input(\"output 파일의 이름을 입력하세요. \") #output 파일의 header 이름을 입력받는 부분\n",
        "    header = \"output\" #폴더 아래에 생성되는 파일 이름\n",
        "\n",
        "    #만약 입력한 파일이 존재하지 않는 경우 error 메시지를 띄우고 실행을 중단합니다.\n",
        "    try:\n",
        "        verb_list = read_verb_list(verb_file)\n",
        "    except FileNotFoundError:\n",
        "        print(\"동사 리스트 파일이 없는 파일로 나타납니다\")\n",
        "        return\n",
        "\n",
        "    try:\n",
        "        data = read_tagged_file(data_file)\n",
        "    except FileNotFoundError:\n",
        "        print(\"CoNLL format으로 분석되어 있는 데이터 파일이 없는 파일로 나타납니다.\")\n",
        "        return\n",
        "\n",
        "    #head word, passive, transitive, intransitive 각각의 경우에 대해서 문장의 리스트를 뽑는 과정입니다.\n",
        "\n",
        "    head_word_dict = count_head_verb(data, verb_list)\n",
        "    passive_word_dict = count_passive(data, verb_list)\n",
        "    transitive_word_dict = count_transitivity(data, verb_list)\n",
        "    intransitive_word_dict = count_intransitivity(data, verb_list)\n",
        "\n",
        "    if folder_name != \"\":\n",
        "        os.mkdir(folder_name)\n",
        "        folder_name = \"./\" + folder_name\n",
        "    else:\n",
        "        folder_name = \"./\"\n",
        "\n",
        "    #추출된 문장 리스트를 이용해 파일을 만드는 과정입니다.\n",
        "    write_file(head_word_dict, folder_name, header, \"head\")\n",
        "    write_file(passive_word_dict, folder_name, header, \"passive\")\n",
        "    write_file(transitive_word_dict, folder_name, header, \"transitive\")\n",
        "    write_file(intransitive_word_dict, folder_name, header, \"intransitive\")"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "vh3BJkzOT2hq",
        "outputId": "f27b4166-83db-4022-a05d-8574dc01f2ab"
      },
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": [
            "Head word sentence extraction: 100%|██████████| 94171/94171 [00:00<00:00, 132474.75it/s]\n",
            "Passive sentence extraction: 100%|██████████| 94171/94171 [00:21<00:00, 4445.54it/s]\n",
            "Transitive sentence extraction: 100%|██████████| 94171/94171 [00:28<00:00, 3260.19it/s]\n",
            "Intransitive sentence extraction: 100%|██████████| 94171/94171 [00:29<00:00, 3241.58it/s]\n"
          ]
        }
      ],
      "source": [
        "main()"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "32e6F6-7T2hs",
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "outputId": "55bed002-8f8c-4d46-ba5e-ede5ee932da9"
      },
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "[\tPUNCT\t[\t10\t11\tunclear\tpunct\r\n",
            "unclear\tADJ\tunclear\t11\t7\tturn\tconj\r\n",
            "]\tPUNCT\t]\t12\t11\tunclear\tpunct\r\n",
            "</s>\r\n",
            "<s id=\"91573\">\r\n",
            "Turn\tVERB\tturn\t1\t0\troot\troot\r\n",
            "it\tPRON\tit\t2\t1\tTurn\tobj\r\n",
            "up\tADP\tup\t3\t1\tTurn\tcompound:prt\r\n",
            "!\tPUNCT\t!\t4\t1\tTurn\tpunct\r\n",
            "</s>\r\n"
          ]
        }
      ],
      "source": [
        "!tail ./sample_data/bnc_tagged.txt"
      ]
    },
    {
      "cell_type": "code",
      "source": [],
      "metadata": {
        "id": "5am4oJsNgUPi"
      },
      "execution_count": null,
      "outputs": []
    }
  ],
  "metadata": {
    "colab": {
      "provenance": []
    },
    "kernelspec": {
      "display_name": "Python 3 (ipykernel)",
      "language": "python",
      "name": "python3"
    },
    "language_info": {
      "codemirror_mode": {
        "name": "ipython",
        "version": 3
      },
      "file_extension": ".py",
      "mimetype": "text/x-python",
      "name": "python",
      "nbconvert_exporter": "python",
      "pygments_lexer": "ipython3",
      "version": "3.9.13"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 0
}