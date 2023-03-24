import numpy as np
import logging
import warnings
import wandb
from pprint import pprint
from tqdm import tqdm as tqdm
import sqlite3
import json
import glob

#Gensim
# import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel, Phrases, phrases, Nmf, TfidfModel
from gensim.models import TfidfModel
from gensim.models.ldamodel import LdaModel

#spacy
import spacy
from nltk.corpus import stopwords

#vis
import pyLDAvis

def lemmatization(texts, allowed_postags=["NOUN", "ADJ", "VERB", "ADV"]):
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    return [" ".join([token.lemma_ for token in nlp(text) if token.pos_ in allowed_postags]) for text in tqdm(texts)]


def make_words(texts):
    return [simple_preprocess(text, deacc=True) for text in tqdm(texts)]


def get_bigram_trigram(texts, min_count, threshold):
    bigram_phrases = Phrases(texts, min_count=min_count, threshold=threshold)
    bigram = phrases.Phraser(bigram_phrases)
    bigram_texts = [bigram[doc] for doc in texts]

    trigram_phrases = Phrases(bigram_phrases[bigram_texts], threshold=threshold)
    trigram = phrases.Phraser(trigram_phrases)
    return [trigram[bigram[doc]] for doc in texts]


#TF-IDF REMOVAL
def create_corpus(texts):
    id2word = corpora.Dictionary(texts)
    id2word.filter_extremes(no_below=5, no_above=.5)
    corpus = [id2word.doc2bow(text) for text in texts]

    tfidf = TfidfModel(corpus, id2word=id2word)

    return id2word, list(tfidf[corpus])


def main():
    # wandb.init(project='congressional topics',
    #            entity='davisai')
    conn = sqlite3.connect('test.db')
    raw_data = [speech[4] for speech in conn.execute('SELECT * FROM speeches LIMIT 1000')]
    use_n_grams = True

    lemmatized_data = lemmatization(raw_data)
    words_data = make_words(lemmatized_data)
    if use_n_grams:
        words_data = get_bigram_trigram(words_data, 5, 30)

    id2word, corpus = create_corpus(words_data)
    nmf = Nmf(corpus,
              num_topics=45,
              id2word=id2word,
              chunksize=2000,
              passes=1,
              kappa=1.,
              minimum_probability=.01,
              w_max_iter=200,
              w_stop_condition=.0001,
              h_max_iter=50,
              h_stop_condition=.001,
              random_state=0)

    coherence = CoherenceModel(
            model=nmf,
            corpus=corpus,
            coherence='u_mass'
            ).get_coherence()
    print(f'{coherence = }')
    pprint(nmf.show_topics())




if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=DeprecationWarning) 
    logging.basicConfig(level=logging.INFO)
    main()
