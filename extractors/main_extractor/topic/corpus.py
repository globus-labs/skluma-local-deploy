import pickle
import math
from collections import Counter

from preprocessing import preprocess


class Corpus:
    '''
    Class to compute and store various bag-of-words statistics for
    a corpus of text documents.

    :doc_freqs: counter that counts number of docs a word occurs in
    :global_tf: counter for total occurrence of a word across corpus
    :doc_tfs: dictionay mapping doc indices to a counter for word
    frequencies within that doc
    :importance: dictionary mapping each word to an 'importance' or
    'information content' value
    :most_common_freq: dictionary mapping doc indices to the highest word
    frequency found in that doc (used for double-normalization of term freq)
    :docs: dictionary mapping doc_ids to original docs

    Note: importance(word) = log(global_tf[word]) / doc_freqs[word]
    '''

    def __init__(self, texts=None):
        ''':param texts: a corpus, i.e., an iterable of strings (documents)'''
        self.doc_freqs = Counter()
        self.global_tf = Counter()
        self.doc_tfs = dict()
        self.importance = dict()
        if not texts:
            self.docs = dict()
            return
        self.docs = dict(enumerate(texts))
        for i, text in self.docs.items():
            tokens = preprocess(text)
            self.global_tf.update(tokens)
            self.doc_tfs[i] = Counter(tokens)
            self.doc_freqs.update(set(tokens))

        # self.most_common_freq = {
            # i: ctr.most_common(1)[0][1]
            # for (i, ctr) in self.doc_tfs.items()
            # }
        self.compute_importance()

    def __get__(self, word):
        return self.get_importance(word)

    def compute_importance(self):
        '''Computes importance values for each word in dictionary'''
        for word, doc_freq in self.doc_freqs.items():
            word_freq = self.global_tf.get(word, 0)
            if word_freq > 0:
                word_freq = math.log(word_freq)
            self.importance[word] = float(word_freq) / doc_freq

    def get_importance(self, word):
        '''Returns the importance of word if it exists in the vocabulary'''
        if len(self.importance) == 0:
            self.compute_importance()
        return self.importance.get(word, 0)

    def get_global_tf(self, word):
        '''Returns the global count of word if it exists in the vocabulary'''
        return self.global_tf.get(word, 0)

    def get_tf(self, doc_id, word):
        '''
        Returns the count of word in the specified doc if the doc exists
        in the corpus and the word exists in the doc
        '''
        doc_tf_counter = self.doc_tfs.get(doc_id, None)
        return None if doc_tf_counter is None else doc_tf_counter.get(word, 0)

    def get_ntf(self, doc_id, word, k=0.4):
        '''Compute the double normalized term frequency of word in doc_id'''
        doc_tf = self.doc_tfs.get(doc_id, Counter())
        if not doc_tf:
            return 0
        highest_freq = max(doc_tf.values())
        if not highest_freq:
            return 0
        word_freq = doc_tf.get(word, 0)
        ntf = k + (1.0 - k) * word_freq / highest_freq
        return ntf

    def save_vocab(self, fname):
        '''Saves a pickle for the vocabulary set'''
        vocab = self.idf.keys()
        with open(fname, "wb") as f:
            pickle.dump(vocab, f)
