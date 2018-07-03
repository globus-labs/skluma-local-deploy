import numpy as np
from feature import FeatureMaker
from itertools import product

class Ngram(FeatureMaker):

    def __init__(self, n):
        """
        n is an int specifying the length of the chains
        """

        self.name = "ngram"
        self.nfeatures = 257 ** n
        self.n = n
        self.class_table = {}

        self.sequence_table = {}

        for seq in product([a.to_bytes(1, "big") for a in range(256)]+[b''], repeat=n):
            self.sequence_table[seq] = len(self.sequence_table)
        assert len(self.sequence_table) == self.nfeatures

    def get_feature(self, open_file):

        feature = [0 for _ in self.sequence_table.items()]

        seq = tuple([open_file.read(1) for _ in range(self.n)])
        
        while seq[0]:

            # problem is empty byte string
            feature[self.sequence_table[seq]] += 1
            new_seq = [b for b in seq[1:]]
            new_seq.append(open_file.read(1))
           
            seq = tuple(new_seq)

        return feature

    def translate(self, entry):

        try:
            y = self.class_table[entry[-1]]
        except KeyError:

            self.class_table[entry[-1]] = len(self.class_table)+1
            y = self.class_table[entry[-1]]
 
        return np.array(entry[2]),y
