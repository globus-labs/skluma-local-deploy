import numpy as np

"""
abstract base class for building features from files
Each new set of features should subclass this
"""

class FeatureMaker:
    """
    Takes a open file, and produces features
    """
    def __init__(self):
        self._name = "test"
        self.nfeatures = 1
 
    def get_feature(self, open_file):
        #print(open_file.name)
        return open_file.name
   
    def translate(data_row):
        """
        translate feature from get_feature to 
        a numpy x and y
        """
        #print(data_row)
        #print(np.zeros(self.nfeatures),0.0)
        return np.zeros(self.nfeatures),0.0
