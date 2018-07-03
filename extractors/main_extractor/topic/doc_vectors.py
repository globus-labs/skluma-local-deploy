import os
import numpy as np

from preprocessing import preprocess
from word_vectors import load_glove_model
from vectorizers import ImportanceEmbeddingVectorizer, NTFImportanceEmbeddingVectorizer

# NOTE: Currently, docs_to_vectors and docs_to_keywords are separate functions
# I need to tidy this up and wrap them into one which avoids repeated work

### Tyler-note: needs to run nltk.download("punkt") once before running!


vectorizers = {
    'ntf-imp': NTFImportanceEmbeddingVectorizer,
    'imp': ImportanceEmbeddingVectorizer,
}

def read_files(files):
    '''Reads in each file in files and returns a list of docs'''
    docs = list()
    for name in files:
        with open(name, 'rb') as f:
            t = f.read()
            t = t.decode('utf-8', errors='replace')
            docs.append(t)
    return docs


def docs_to_vectors(docs, word_vectors, mode='ntf-imp'):
    '''
    Returns a list of representative word vectors, one for each doc in docs
    :param docs: iterable of documents/strings
    :param word_vectors: loaded word2vec model (use word_vectors module)
    :param mode: must be one of ['ntf-imp', 'imp'], which vectorizer to use
    '''
    vectorizer = vectorizers.get(mode.lower(), None)
    if vectorizer is None:
        raise ValueError('mode must be one of' + ', '.join(vectorizers.keys()))
        return None

    model = vectorizer(word_vectors)
    model = model.fit(docs)
    doc_vectors = model.transform(docs)
    return doc_vectors


def files_to_vectors(files, word_vectors, mode='ntf-imp'):
    '''
    Reads in each file in files and calls docs_to_vectors on this collection
    '''
    docs = read_files(files)
    return docs_to_vectors(docs, word_vectors, mode=mode)


def directory_to_vectors(directory, word_vectors, mode='ntf-imp'):
    '''
    Reads in each file in directory and calls docs_to_vectors on this collection
    '''
    files = list()
    for path, _, filenames in os.walk(directory):
        for file in filenames:
            files.append(os.path.join(path, file))
    return files_to_vectors(files, word_vectors, mode=mode)


def docs_to_keywords(docs, top_n=10, mode='ntf-imp', scores=True):
    '''
    Returns a list of keyword lists using the given importance measure in mode,
    one for each doc in docs, employing the vectorizer module without word2vec
    :param docs: iterable of documents/strings
    :param mode: must be one of ['ntf-imp', 'imp'], which vectorizer to use
    :param scores: if True, ech keyword list is a list of (word, score) tuples,
    otherwise, each keyword list is a list of words
    '''
    vectorizer = vectorizers.get(mode.lower(), None)
    if vectorizer is None:
        raise ValueError('mode must be one of' + ', '.join(vectorizers.keys()))
        return None

    model = vectorizer()    # notice no word vectors passed in
    model = model.fit(docs)
    keywords = model.keywords(docs, top_n=top_n, scores=scores)
    return keywords


def files_to_keywords(files, top_n=10, mode='ntf-imp', scores=True):
    '''
    Reads in each file in files and calls docs_to_keywords on this collection
    '''
    docs = read_files(files)
    return docs_to_keywords(docs, top_n=top_n, mode=mode, scores=scores)


def directory_to_keywords(directory, top_n=10, mode='ntf-imp', scores=True):
    '''
    Reads in each file in directory and calls docs_to_keywords on this collection
    '''
    files = list()
    for path, _, filenames in os.walk(directory):
        for file in filenames:
            files.append(os.path.join(path, file))
    return files_to_keywords(files, top_n=top_n, mode=mode, scores=scores)



