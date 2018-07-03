import numpy as np

from os.path import getsize
from feature import FeatureMaker
from random import randint

class RandBytes(FeatureMaker):

    def __init__(self, number_bytes=512):
    
        self.name = "rand"
        self.nfeatures = number_bytes

        self.class_table = {}

    def get_feature(self, open_file):

        size = getsize(open_file.name)

        if size == 0: # presumably we don't care about these
           raise FileNotFoundError()              
        else:
            rand_index = [randint(0,size-1) for _ in range(self.nfeatures)]

        # For files where size < nfeatures, this will oversample.
        # This may be something to look out for though. 
      
        rand_index.sort()
        sample_bytes = []

        for index in rand_index:

            open_file.seek(index)
            sample_bytes.append(open_file.read(1))

        return sample_bytes

    def translate(self, entry):

        x = [int.from_bytes(c, byteorder="big") for c in entry[2]]
        
        try:
            y = self.class_table[entry[-1]]
        except KeyError:
            self.class_table[entry[-1]] = len(self.class_table)+1
            y = self.class_table[entry[-1]]

        return np.array(x),y
