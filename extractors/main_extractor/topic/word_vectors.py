import os
from gensim.models.keyedvectors import KeyedVectors


# ---------------------------------------------------------------------------
#                         Model Loading Functions
# ---------------------------------------------------------------------------

def load_glove_model(dim=50, path='word_vectors'):
    '''
    Loads and returns GloVe model with dim-dimensional vectors as a
    KeyedVectors object.
    '''
    supported_dims = [50, 100, 200, 300]
    if dim not in supported_dims:
        raise ValueError("Word2Vec dimension must be one of " +
                         " ".join(supported_dims))
    f = os.path.join(path, 'glove.6B.' + str(dim) + 'd.cformat.txt')
    wv = KeyedVectors.load_word2vec_format(f, binary=False)
    return wv


def load_word2vec_model(path='word_vectors'):
    '''
    Loads and returns word2vec model as a KeyedVectors object
    '''
    f = os.path.join(path, 'GoogleNews-vectors-negative300.bin')
    wv = KeyedVectors.load_word2vec_format(f, binary=True)
    return wv
