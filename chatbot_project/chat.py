from .functions import make_predictions, search_mri2
import pandas as pd
import sqlite3
from pathlib import Path
import wget
import random
from django.conf import settings
import os


# get responses
def get_data_chat(intent):
    db_path = os.path.join(settings.BASE_DIR,'db.sqlite3')
    connection = sqlite3.connect(db_path)
    db_rows = pd.read_sql('select app_response.name as response from app_response, app_intent where app_response.intent_id = app_intent.id and '
                          + 'app_intent.name = "' + str(intent)+'"', connection)
    return db_rows


# global variables
accreditation = False
search_Request = (False, "")
downloads_path = str(Path.home() / "Downloads")


def write_to_file(index, text):
    file_path = os.path.join(settings.BASE_DIR, 'app', 'chatbot_project', 'files', str(index) + '.txt')
    with open(file_path, "a") as f:
        f.write(text + '\n')
        f.close()


def new_line(msg):
    nl = "\\"
    nl_2 = "n"
    indices = []
    with_nl = ""
    bs = [i for i, c in enumerate(msg) if c == nl]
    for i in range(len(bs)):
        if msg[bs[i]+1] == nl_2:
            indices.append(bs[i])
    substrings = msg.split('\\n', len(indices))
    for x in substrings:
        if x == substrings[-1]:
            with_nl += x
        else:
            with_nl += x + '\n'
    return with_nl


def chat(msg, index):
    global search_Request
    write_to_file(index, "You: " + msg)
    predicted_intent, probability = make_predictions([msg])
    db_rows = get_data_chat(predicted_intent)
    print('TEST: ', predicted_intent, probability)
    all_responses = db_rows["response"]

    if search_Request[0]:
        if predicted_intent == "yes":
            response = search_mri2(search_Request[1])
        elif predicted_intent == "no":
            response = "Ok. is there anything else I can do for you?"
        else:
            response = "I'm sorry, I couldn't understand your response."  # Default response added

        search_Request = (False, "")

    else:
        if probability > 0.8:
            if list(all_responses) == [None]:
                response = "I didn't get that, try again."
            else:
                response = random.choice(list(all_responses))
                response = new_line(response)
        else:
            response = "Unfortunately, I have no knowledge of your request. Do you want me to look it up for you?"
            search_Request = (True, msg)

    write_to_file(index, "Bot: " + response)
    return response


