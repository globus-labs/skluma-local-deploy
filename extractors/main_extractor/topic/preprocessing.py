import re
from collections import Counter, defaultdict
from nltk.tokenize import word_tokenize


def preprocess(doc):
    '''
    Extracts a list of words from a long string, strips punctuation,
    and eliminates short words or stop words, returning a list of tokens
    '''
    stop_words = ['\n']
    with open('stop-words-en.txt', 'r') as f:
        stop_words += [x.strip() for x in f.readlines()]
    tokens = [x for x in word_tokenize(doc.lower())
              if x not in stop_words and re.match("[a-zA-Z]{2,}", x)]
    return tokens
