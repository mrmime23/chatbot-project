import spacy
import pandas as pd
import sqlite3
from sklearn.preprocessing import LabelEncoder
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
from nltk.stem.snowball import SnowballStemmer
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import random
from collections import Counter
from sentence_transformers import SentenceTransformer
from scipy.spatial import distance
import numpy as np
from nltk.corpus import wordnet
import os
from django.conf import settings

# Hyperparameter
nlp = spacy.load('en_core_web_lg')
max_tokens = 50
stemmer = SnowballStemmer(language="english")
model_sim = SentenceTransformer('distilbert-base-nli-mean-tokens')


tokenizer_path = os.path.join(settings.BASE_DIR, 'app', 'chatbot_project', 'data', 'tokenizer.pickle')
with open(tokenizer_path, 'rb') as handle:
    tokenizer = pickle.load(handle)

all_intents_path = os.path.join(settings.BASE_DIR, 'app', 'chatbot_project', 'data', 'all_intents.pickle')
with open(all_intents_path, 'rb') as handle:
    all_intents = pickle.load(handle)

urls_path = os.path.join(settings.BASE_DIR, 'app', 'chatbot_project', 'data', 'urls.pickle')
with open(urls_path, 'rb') as handle:
    urls = pickle.load(handle)
    urls[0]["content"] = None

encoded_mri_content_path = os.path.join(settings.BASE_DIR, 'app', 'chatbot_project', 'data', 'encoded_mri_content.pickle')
with open(encoded_mri_content_path, 'rb') as handle:
    encoded_mri_content = pickle.load(handle)

encoded_mri_titles_path = os.path.join(settings.BASE_DIR, 'app', 'chatbot_project', 'data', 'encoded_mri_titles.pickle')
with open(encoded_mri_titles_path, 'rb') as handle:
    encoded_mri_titles = pickle.load(handle)

model_path = os.path.join(settings.BASE_DIR, 'app', 'chatbot_project', 'data', 'model.h5')
model = load_model(model_path)


def stem(word):
    return stemmer.stem(word.lower())


def read_database(path):
    # Loading Data from database
    connection = sqlite3.connect(path)
    db_rows = pd.read_sql('''select app_intent.name as intent, app_pattern.name as pattern
    from app_intent, app_pattern where app_intent.id = app_pattern.intent_id''', connection)

    labels = []
    sentences = []
    intents = []
    for i in range(len(db_rows)):
        labels.append(db_rows["intent"][i])
        if db_rows["intent"][i] not in intents:
            intents.append(db_rows["intent"][i])
        sentences.append(db_rows["pattern"][i])
    return sentences, labels, intents


def label_encoding(labels):
    # Calculate the length of labels
    n_labels = len(labels)
    print('Number of labels :-', n_labels)
    le = LabelEncoder()
    y = le.fit_transform(labels)
    print('Length of y :- ', y.shape)
    return y


def process_text(text):
    doc = nlp(text.lower())
    result = []

    if len(doc) <= 4:
        for token in doc:  # tokenizing the sentence
            result.append(token.lemma_)
        return " ".join(result)
    else:
        for token in doc:  # tokenizing the sentence
            if token.tag_ == "WP" or token.tag_ == "WRB" or token.tag_ == "WDT":
                to_append = stem(token.lemma_)
                result.append(to_append)
                continue
            if token.is_punct:
                continue
            # if token.text in nlp.Defaults.stop_words:
                # continue
            if token.lemma_ == '-PRON-':
                continue
            to_append = stem(token.lemma_)
            result.append(to_append)
        return " ".join(result)


def make_predictions(sentence):
    sentence = [process_text(sentence[0])]
    X = tokenizer.texts_to_sequences(sentence)

    # Bringing all samples to max_tokens length.
    X = pad_sequences(X, maxlen=max_tokens, padding="post", truncating="post", value=0.)

    # predict the right class and get the label
    preds = model.predict(X)
    pred = preds.argmax()
    predicted_intent = all_intents[pred]
    predicted_acc = preds[0][pred]
    return predicted_intent, predicted_acc


def split_words(msg):
    arr = msg.split("\n")
    return arr


def check_for_url(arr):
    index_of_urls = []
    for url in arr:
        if "www" in url or "http" in url or "https" in url or ".com" in url or ".de" in url or ".org" in url:
            # if ping(url):
            index_of_urls.append(arr.index(url))
    return index_of_urls


def find_synonym(string, n):
    """ Function to find synonyms for a string"""
    try:
        results = []

        # Remove whitespace before and after word and use underscore between words
        stripped_string = string.strip()
        fixed_string = stripped_string.replace(" ", "_")

        # Set the url using the amended string
        url = f'https://thesaurus.plus/thesaurus/{fixed_string}'

        # Open and read the HTML
        req = Request(
            url=url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        webpage = urlopen(req).read()
        doc = soup(webpage, "html.parser")
        word_boxes = doc.find_all("ul", attrs={"class": "list mb-3"})

        # use negative index to get the last element, if antonyms are displayed, it is the first list
        list_elements = word_boxes[-1].find_all("div", "p-2")

        # Iterate over results and print
        for idx, element in enumerate(list_elements):
            if idx <= n-1:
                results.append(element.text.strip())

        return results

    except HTTPError:
        pass


def synonym_extractor_nltk(phrase, n):

    synonyms = []

    for syn in wordnet.synsets(phrase):
        for l in syn.lemmas():
            synonyms.append(l.name())

    return list(set(synonyms))[:n]


def augmented_sentences(sentence, stopwords, n, m):
    # variables
    doc = nlp(sentence.lower())
    counter = Counter(([token.pos_ for token in doc]))
    counted_verbs = counter['VERB']
    counted_adj = counter['ADJ'] + counter['ADV']
    counted_nouns = counter['NOUN']
    synonym_verbs = []
    synonym_noun = []
    synonym_adj = []
    new_sentences = []

    # stop if sentence is only one word
    if len(doc) == 1:
        return []

    for idx, token in enumerate(doc):  # tokenizing the sentence

        if token.pos_ == 'VERB':

            # check if verb is a self-declared stopword
            if str(token) in stopwords:
                synonym_verbs.append([])
                continue
            else:
                # check if verb has a adposition to search for it
                if token != doc[-1] and doc[idx + 1].pos_ == 'ADP':
                    to_search = str(token) + " " + str(doc[idx + 1])
                    buf = find_synonym(str(to_search), n)

                    # handle if nothing is found with adposition
                    if buf is None:
                        to_search = token
                        buf = find_synonym(str(to_search), n)

                    # append the buffer to the synonym array
                    synonym_verbs.append(buf)
                    continue

                else:
                    to_search = token
                    buf = find_synonym('to_' + str(to_search), n)

                    if buf is None:
                        buf = find_synonym(str(to_search), n)
                    synonym_verbs.append(buf)
                    continue

        if token.pos_ == 'ADV' or token.pos_ == 'ADJ':
            # check if adj is a self-declared stopword
            if str(token) in stopwords:
                synonym_adj.append([])
                continue

            buf = find_synonym(str(token.lemma_), n)
            # OR
            #  synonym_adj = synonym_extractor_nltk(str(token), n)
            if buf is None:
                synonym_adj.append([])
                continue
            synonym_adj.append(buf)
            continue

        if token.pos_ == 'NOUN':
            # check if noun is a self-declared stopword
            if str(token) in stopwords:
                synonym_noun.append([])
                continue

            buf = find_synonym(str(token.lemma_), n)
            if buf is None:
                synonym_noun.append([])
                continue
            synonym_noun.append(buf)
            continue
    # print(synonym_noun, synonym_adj, synonym_verbs)
    # print(counted_nouns, counted_adj, counted_verbs)

    # this loop is responsible for the quantity of sentences
    x = 0
    while x < m:
        # counter variables
        x += 1
        v = 0
        a = 0
        n = 0
        new_sentence = ""
        if not any(synonym_noun) and not any(synonym_adj) and not any(synonym_verbs):
            return []

        for token in doc:
            if token.pos_ == 'VERB':
                if synonym_verbs[v] and token.text not in stopwords:
                    new_sentence = "".join(new_sentence + str(random.choice(synonym_verbs[v])) + " ")
                if token.text in stopwords:
                    new_sentence = "".join(new_sentence + str(token) + " ")
                v += 1
                continue
            if token.pos_ == 'ADV' or token.pos_ == 'ADJ':
                if synonym_adj[a] and token.text not in stopwords:
                    new_sentence = "".join(new_sentence + str(random.choice(synonym_adj[a])) + " ")
                if token.text in stopwords:
                    new_sentence = "".join(new_sentence + str(token) + " ")
                a += 1
                continue
            if token.pos_ == 'NOUN':
                if synonym_noun[n] and token.text not in stopwords:
                    new_sentence = "".join(new_sentence + str(random.choice(synonym_noun[n])) + " ")
                if token.text in stopwords:
                    new_sentence = "".join(new_sentence + str(token) + " ")
                n += 1
                continue
            else:
                new_sentence = "".join(new_sentence + str(token) + " ")

        # to prevent that the same sentence is in the output array
        if new_sentence.strip() in new_sentences:
            x -= 1
        else:
            new_sentences.append(new_sentence.strip())

    return new_sentences


def prepare_for_search(text):
    result = []
    doc = nlp(text)
    for token in doc:  # tokenizing the sentence
        if token.is_punct:
            continue
        if token.text in nlp.Defaults.stop_words:
            continue
        if token.lemma_ == '-PRON-':
            continue
        result.append(token.text)
    result = " ".join(result)

    return result


def search_mri(text):
    prep_text = prepare_for_search(text)
    prep_doc = nlp(prep_text)
    try:
        acc = []

        # Remove whitespace before and after word and use underscore between words
        stripped_string = prep_text.strip()
        fixed_string = stripped_string.replace(" ", "+")

        # Set the url using the amended string
        url = f'https://mriquestions.com/apps/search?q={fixed_string}'

        # Set the url for the output
        url2 = f'https://mriquestions.com'

        # Open and read the HTML
        req = Request(
            url=url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        # get needed information
        webpage = urlopen(req).read()
        doc = soup(webpage, "html.parser")
        word_boxes = doc.find_all("ol", attrs={"id": "wsite-search-list"})
        list_elements = word_boxes[0].find_all(href=True)

        # search for suitable topic
        accuracies = np.zeros(len(list_elements))
        for idx, element in enumerate(list_elements):
            to_compare = element.find('h3').text.strip()
            sentences = [to_compare, prep_text]
            sentence_embeddings = model_sim.encode(sentences)
            print(sentence_embeddings.shape)
            accuracies[idx] = 1 - distance.cosine(sentence_embeddings[0], sentence_embeddings[1])

        if not any(accuracies):
            return "I didn't get that, try again."

        highest_acc = accuracies[accuracies.argmax()]

        if highest_acc > 0.75:
            return "I found this regarding your concern: \n" + url2 + list_elements[accuracies.argmax()]['href']
        else:
            return "Unfortunately, I do not have any information regarding your request"

    except HTTPError:
        pass
        return HTTPError


def search_mri2(text):
    prep_text = prepare_for_search(text)
    accuracies_content = np.zeros(len(urls))
    accuracies_titles = np.zeros(len(urls))
    sentence_embedding = model_sim.encode(prep_text)
    for idx, url in enumerate(urls):

        if any(encoded_mri_content[idx]) != 0:
            accuracies_content[idx] = 1 - distance.cosine(encoded_mri_content[idx], sentence_embedding)
        if any(encoded_mri_content[idx]) == 0:
            accuracies_content[idx] = 0

        if any(encoded_mri_titles[idx]) != 0:
            encoded_mri_titles[idx] = 1 - distance.cosine(encoded_mri_titles[idx], sentence_embedding)
        if any(encoded_mri_titles[idx]) == 0:
            encoded_mri_titles[idx] = 0

    if accuracies_titles[accuracies_titles.argmax()] > accuracies_content[accuracies_content.argmax()]:
        if accuracies_titles[accuracies_titles.argmax()] > 0.8:
            print("title: ", accuracies_titles[accuracies_titles.argmax()])
            return "I found this regarding your concern: \n" + urls[accuracies_titles.argmax()]['url']
        else:
            return "Unfortunately, I do not have any information regarding your request"
    if accuracies_titles[accuracies_titles.argmax()] < accuracies_content[accuracies_content.argmax()]:
        if accuracies_content[accuracies_content.argmax()] > 0.8:
            print("content: ", accuracies_content[accuracies_content.argmax()])
            return "I found this regarding your concern: \n" + urls[accuracies_content.argmax()]['url']
        else:
            return "Unfortunately, I do not have any information regarding your request"




