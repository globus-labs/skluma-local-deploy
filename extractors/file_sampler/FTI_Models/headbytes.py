import os
import subprocess

import numpy as np
from feature import FeatureMaker

class HeadBytes(FeatureMaker):
    def __init__(self, head_size=512):

        self.name = "head"
        self.head_size = head_size
        self.nfeatures = head_size

        # for feature translation, hopefully putting all featurization
        # logic here is a good decision
       
        self.class_table = {}
 
    def get_feature(self, open_file):
        
        byte = open_file.read(1) 
        read = 1  
        head = [] 

        while byte and read < self.head_size:

            head.append(byte)
            read += 1
            byte = open_file.read(1)

        if len(head) < self.head_size:
            head.extend([b'' for i in range(self.head_size - len(head))])
        assert len(head) == self.head_size
        return head

    def translate(self, entry):
        x = [int.from_bytes(c, byteorder="big") for c in entry[2]]
        try:
            y = self.class_table[entry[-1]]
            #print(y)
        except KeyError:
            self.class_table[entry[-1]] = len(self.class_table)+1
            y = self.class_table[entry[-1]]
        os.environ["CLASS_TABLE"] = str(self.class_table) # TODO: Why won't environ vars work?
        # class_table = """export CLASS_TABLE={0}""".format(str(self.class_table))

        # processes = [subprocess.Popen(class_table, shell=True)]
        # for p in processes: p.wait()

        return np.array(x),y
