
import numpy as np
import pickle as pkl
from random import shuffle

from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import boto

class ClassifierBuilder(object):

    """
    Classifier builder takes a system reader, and uses that
    to build a cross-validated classifier. We use the feature
    makers' to_np method to convert the list rows to an acceptable
    numpy array based format
    """

    def __init__(self, reader, classifier="svc",split=0.8):
        """
        reader - the system reader object, must have data already
                 loaded into it (though we could change later)
        classifier - the classifier type to be used, options are 
                        "svc" - support vector classifier
                        "logit" - logistic regression
                        "rf" - random forest 
        split - a decimal between 0 and 1 which indicates how much
                of the data should be used as training. The rest is used
                as a testing set.
        """
        self.classifier_type = classifier
        self.model = None
        self.split = split

        # randomly partition data, add method to shuffle w/in classifier
        # so we don't need to translate multiple times after this.

        data = [line for line in reader.data]
        shuffle(data)

        split_index = int(split*len(data))

        train_data = data[:split_index]
        test_data = data[split_index:]

        self.X_train = np.zeros((len(train_data), reader.feature.nfeatures))
        self.Y_train = np.zeros(len(train_data))

        self.X_test = np.zeros((len(test_data), reader.feature.nfeatures))
        self.Y_test = np.zeros(len(test_data))

        groups = [[train_data, self.X_train, self.Y_train],
                  [test_data, self.X_test, self.Y_test]]

        #train and test
        for group in groups:
            raw_data,X,Y = group
            #print(raw_data, X,Y)
            for i in range(len(raw_data)):
                #1print("Raw_Data[i] is " + str(raw_data[i]))
                #2print("Raw_Data is of length: " + str(len(raw_data[i])))
                x,y = reader.feature.translate(raw_data[i])
                #3print("X value is: " + str(x) + " of length " + str(len(x)))
                X[i] = x
                Y[i] = y

    def train(self):

        # TODO: as we fiddle with these, should add options to adjust classifier parameters

        if self.classifier_type == "svc":
            self.model = SVC()
        elif self.classifier_type == "logit":
            self.model = LogisticRegression()
        elif self.classifier_type == "rf":
            #self.model = RandomForestClassifier()
            self.model = RandomForestClassifier(n_estimators=15,
                                                max_depth = 4000, #Shouldn't overfit with only few trees
                                                min_samples_split=3
                                                #oob_score=true, # will be slower
                                                )

        self.model.fit(self.X_train, self.Y_train)

        train_and_save(self.model, self.X_train, self.Y_train, "training_test2.pkl")

    def test(self):
       
        """
        evaluate the model on the testing set
        """

        return self.model.score(self.X_test, self.Y_test)

    def shuffle(self, split=None):

        if split is None:
            split = self.split
   
        old_X = np.concatenate((self.X_train, self.X_test), axis=0)
        old_Y = np.concatenate((self.Y_train, self.Y_test), axis=0)
        
        perm = np.random.permutation(old_Y.shape[0])

        X = old_X[perm]
        Y = old_Y[perm]

        split_index = int(split*X.shape[0])

        self.X_train = X[:split_index]
        self.Y_train = Y[:split_index]

        self.X_test = X[split_index:]
        self.Y_test = Y[split_index:]



def train_and_save(model, X, y, file_name):
    """Train the model on the input data and save it for use in the pipeline.
        :param model: (sklearn.model) model to test
        :param X: (np.array) data matrix
        :param y: (np.array) true value column vector
        :param file_name: (string) file name of model"""

    model.fit(X, y)
    with open(file_name, "wb") as f:
        pkl.dump(model, f)
