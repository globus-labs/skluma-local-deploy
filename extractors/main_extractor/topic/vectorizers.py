import numpy as np

from corpus import Corpus
from preprocessing import preprocess


class MeanEmbeddingVectorizer(object):
    '''
    Maps each document to the mean word vector of all valid tokens found in it
    '''
    def __init__(self, word2vec):
        self.word2vec = word2vec
        self.corpus = None
        self.dim = self.word2vec.vector_size

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = [preprocess(doc) for doc in X]
        return np.array([
            np.mean([self.word2vec[w]
                        for w in words if w in self.word2vec], axis=0)
            for words in X
        ])


class ImportanceEmbeddingVectorizer(object):
    '''
    Each document vector is a mean word vector of the top n important valid
    tokens found in the document, where each vector is weighted by its
    global importance factor

    Usage:
        If only keywords are required:
            Initialize object without word2vec
            Fit the vectorizer with a big corpus to learn word importance values
            Call the keywords function
        If document vectors are required:
            Initialize object with word2vec
            Fit the vectorizer with a big corpus to learn word importance values
            Transform the vectorizer with your corpus to get document vectors
    '''
    def __init__(self, word2vec=None):
        '''Initialize object. word2vec optional if only using for keywords.'''
        self.word2vec = None
        self.word2weight = None
        if word2vec is not None:
            self.add_word_vectors(word2vec)

    def add_word_vectors(self, word2vec):
        '''Adds a word2vec model for vectorization'''
        self.word2vec = word2vec
        self.dim = self.word2vec.vector_size

    def fit(self, X, y=None):
        '''Learn word importance values from the list of documents provided'''
        self.word2weight = Corpus(X)
        return self

    def transform(self, X, top_n=10):
        '''
        Use learnt importance values to scale the word vectors for the top_n
        important words in each document in X, producing a representative
        vector for each document in X
        '''
        if self.word2vec is None:
            raise AttributeError('Word vectors not initialized. Please pass a word vector model into add_word_vectors.')
            return None

        X = self.keywords(X, top_n=top_n)

        return np.array([
            np.mean([self.word2vec[w] * imp for (w, imp) in words], axis=0)
                for words in X
        ])

    def keywords(self, X, top_n=10, scores=True):
        '''
        Finds the top_n keywords for each document in X, as weighted by
        the importance factors learnt earlier by fitting
        Returns a list of keyword lists (one keyword list for each doc in X)
        If scores is True, each keyword list is a list of (word, score) tuples,
        otherwise, each keyword list is a list of words

        Note: If word2vec has been provided earlier, keywords only consist of
        words which are present in the word2vec model
        '''
        X = [preprocess(doc) for doc in X]
        X = [
                [ (w, self.word2weight.get_importance(w))
                    for w in set(words) if self.word2vec is None or w in self.word2vec ]
            for words in X
        ]
        X = [sorted(x, key=lambda p: p[1], reverse=True)[:top_n] for x in X]
        if not scores:
            X = [[p[0] for p in x] for x in X]
        return X


class NTFImportanceEmbeddingVectorizer(object):
    '''
    Each document vector is a mean word vector of the top n important valid
    tokens found in the document, where each vector is weighted by its
    (normalized term frequency in the document) * (global importance factor)

    Usage:
        If only keywords are required:
            Initialize object without word2vec
            Fit the vectorizer with a big corpus to learn word importance values
            Call the keywords function
        If document vectors are required:
            Initialize object with word2vec
            Fit the vectorizer with a big corpus to learn word importance values
            Transform the vectorizer with your corpus to get document vectors
    '''
    def __init__(self, word2vec=None):
        '''Initialize object. word2vec optional if only using for keywords.'''
        self.word2vec = None
        self.word2weight = None
        if word2vec is not None:
            self.add_word_vectors(word2vec)

    def add_word_vectors(self, word2vec):
        '''Adds a word2vec model for vectorization'''
        self.word2vec = word2vec
        self.dim = self.word2vec.vector_size

    def fit(self, X, y=None):
        '''Learn word importance values from the list of documents provided'''
        self.word2weight = Corpus(X)
        return self

    def transform(self, X, top_n=10):
        '''
        Use learnt importance values to scale the word vectors for the top_n
        important words in each document in X, producing a representative
        vector for each document in X
        '''
        if self.word2vec is None:
            raise AttributeError('Word vectors not initialized. Please pass a word vector model into add_word_vectors.')
            return None

        X = self.keywords(X, top_n=top_n)

        return np.array([
            np.mean([self.word2vec[w] * ntf_imp for (w, ntf_imp) in words], axis=0)
                for words in X
        ])

    def keywords(self, X, top_n=10, scores=True):
        '''
        Finds the top_n keywords for each document in X, as weighted by
        the importance factors learnt earlier by fitting
        Returns a list of keyword lists (one keyword list for each doc in X)
        If scores is True, each keyword list is a list of (word, score) tuples,
        otherwise, each keyword list is a list of words

        Note: If word2vec has been provided earlier, keywords only consist of
        words which are present in the word2vec model
        '''
        cp = Corpus(X)
        X = [preprocess(doc) for doc in X]
        X = [
                [ (w, self.word2weight.get_importance(w) * cp.get_ntf(i, w))
                    for w in set(words) if self.word2vec is None or w in self.word2vec ]
            for i, words in enumerate(X)
        ]
        X = [sorted(x, key=lambda p: p[1], reverse=True)[:top_n] for x in X]
        if not scores:
            X = [[p[0] for p in x] for x in X]
        return X
