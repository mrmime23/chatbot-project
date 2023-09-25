import requests
from bs4 import BeautifulSoup
import urllib.request
import pickle5 as pickle
from sentence_transformers import SentenceTransformer
import numpy as np
from functions import prepare_for_search
import spacy
from scispacy.abbreviation import AbbreviationDetector

nlp_a = spacy.load("en_core_sci_lg")

# Add the abbreviation pipe to the spacy pipeline.
nlp_a.add_pipe("abbreviation_detector")


model_sim = SentenceTransformer('distilbert-base-nli-mean-tokens')


def get_mriquestions_content():
    url = 'link with content for chatbot'
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    prefix = 'https://mriquestions.com'
    urls = []
    print("getting links")

    for link in soup.find_all('a'):
        if link.get('href') is not None:
            if ".html" in link.get('href'):
                suburl = prefix + link.get('href')
                print(suburl)
                filename = link.get('href')[1:]
                filename = filename.replace("-", "_")
                webpage = requests.get(suburl)
                doc = BeautifulSoup(webpage.text, "html.parser")
                word_boxes = doc.find("h2", attrs={"class": "wsite-content-title"})
                content_boxes = doc.find("div", attrs={"class": "paragraph"})

                if word_boxes is not None and content_boxes is not None:
                    urls.append({"url": suburl, "title": word_boxes.get_text(strip=True, separator=" "),
                                 "content": content_boxes.get_text(strip=True, separator=" ")})
                if word_boxes is not None and content_boxes is None:
                    urls.append({"url": suburl, "title": word_boxes.get_text(strip=True, separator=" "), "content": None})
                if word_boxes is None and content_boxes is not None:
                    urls.append({"url": suburl, "title": None, "content": content_boxes.get_text(strip=True, separator=" ")})
                if word_boxes is None and content_boxes is None:
                    urls.append({"url": suburl, "title": None, "content": None})

                urllib.request.urlretrieve(suburl, './mriquestions/' + filename)

    with open('./data/urls.pickle', 'wb') as handle:
        pickle.dump(urls, handle, protocol=pickle.HIGHEST_PROTOCOL)

    get_encoded_content(urls)


def delete_acronyms(text):
    doc = nlp_a(text)
    at = [tok.text for tok in doc]
    acronyms = doc._.abbreviations
    for acronym in acronyms:
        at.remove(str(acronym))
    return " ".join(at)

def get_encoded_content(library):
    encoded_content = np.zeros((len(library), 768))
    encoded_titles = np.zeros((len(library), 768))
    print("start encoding...")
    for idx, entry in enumerate(library):


        if entry['title'] is not None:
            title = delete_acronyms(entry['title'])
            encoded_titles[idx] = model_sim.encode(prepare_for_search(title))
        if entry['title'] is None:
            encoded_titles[idx] = 0

        if entry['content'] is not None:
            content = delete_acronyms(entry['content'])
            encoded_content[idx] = model_sim.encode(prepare_for_search(content))
        if entry['content'] is None:
            encoded_content[idx] = 0

    with open('./data/encoded_mri_titles.pickle', 'wb') as hand:
        pickle.dump(encoded_titles, hand)

    with open('./data/encoded_mri_content.pickle', 'wb') as hand:
        pickle.dump(encoded_content, hand)

    print("finished encoding!")


if __name__ == "__main__":
    get_mriquestions_content()
