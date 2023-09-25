import random
import torch
from model import NeuralNet
from functions import bag_of_words, tokenize
import pandas as pd
import sqlite3
import wget
from pathlib import Path


downloads_path = str(Path.home() / "Downloads")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
connection = sqlite3.connect("database.db")
db_rows = pd.read_sql('select tags.tag, intents.responses from intents, tags where tags.id = intents.tagid and patterns is not null order by tag', connection)
db_astm = pd.read_sql('select name, method, field_strength, devices from astm', connection)
FILE = "data.pth"
data = torch.load(FILE)


input_size = data['input_size']
hidden_size = data['hidden_size']
output_size = data['output_size']
all_words = data['all_words']
tags = data['tags']
model_state = data['model_state']

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

# global variables
accreditation = False


def write_to_file(index, text):
    with open('files/' + str(index) + ".txt", "a") as f:
        f.write(text + '\n')
        f.close()


def new_line(msg):
    nl = "\\"
    nl_2 = "n"
    indices = []
    with_nl = ""
    bs = [i for i, c in enumerate(msg) if c == nl]
    for i in range(len(bs)):
        if msg[bs[i]+1] == "n":
            indices.append(bs[i])
    substrings = msg.split('\\n', len(indices))
    for x in substrings:
        if x == substrings[-1]:
            with_nl += x
        else:
            with_nl += x + '\n'
    return with_nl


def download_accreditation():
    url = 'https://mrcomp.com/files/Redakteure/7_About_us/20210927_Accreditation_Certificate_D_PL_13383_01_00_EN_incl_annex.pdf'
    wget.download(url, downloads_path)


def chat(msg, index):
    # write the sentence
    write_to_file(index, "You: " + msg)

    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X)
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    global accreditation
    response = None

    # start accreditation download
    if accreditation:

        if msg.lower() == "yes":
            download_accreditation()
            accreditation = False
            response = "A copy of our accreditation certificate has been added to your downloads folder \nIs there anything else I can help you with?"

        else:
            accreditation = False
            response = "Is there anything else I can help you with?"

        write_to_file(index, "Bot: " + response)
        return response

    # start picking response for certain tag
    if prob.item() > 0.75:
        for i in range(len(db_rows)):
            all_responses = (db_rows[db_rows["tag"] == tag]["responses"])

            if tag == "passive-implants-more-information":
                try:
                    astm_numb = sentence.index('astm')
                except:
                    astm_numb = sentence.index('ASTM')
                try:
                    standard = "ASTM " + sentence[astm_numb + 1]
                    for x in range(len(db_astm)):
                        if db_astm["name"][x] == standard:
                            response = "with the standard" + db_astm["name"][x] + "the following method is examined: " + db_astm["method"][x] + "\nTherefore, devices with the following properties are considered:\n" + db_astm["devices"][x]
                        else:
                            response = "I didn't get that, try again."

                except:
                    response = "I didn't get that, try again."
            if list(all_responses) == [None]:
                response = "I didn't get that, try again."
            else:
                while response is None:
                    response = random.choice(list(all_responses))
            response = new_line(response)
            if tag == "accreditation":
                accreditation = True


    else:
        response = "I didn't get that, try again."

    write_to_file(index, "Bot: " + response)
    return response
