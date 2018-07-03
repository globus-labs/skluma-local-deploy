#!/usr/local/bin/python3

"""
This main script handles both the training and prediction tasks of the
file forensic byte-level predictor.This is constructed to run in a Python3
Docker container, but can be easily adapted otherwise.

    Authors: Galen Harrison and Tyler Skluzacek (skluzacek@uchicago.edu)
    Last Edited: 07/03/2018
"""

import argparse
import json
import os
import pickle
import time

import numpy as np
import sqlite3

from headbytes import HeadBytes
from extpredict import NaiveTruthReader
from extpredict import FileReader
from classify import ClassifierBuilder
from randbytes import RandBytes
from randhead import RandHead
from ngram import Ngram
from randngram import RandNgram
from sklearn import preprocessing

DB_PATH = os.environ["DB_PATH"]

with open('/src/CLASS_TABLE.json', 'r') as f:
    label_map = json.load(f)
    f.close()


def main():

    # TODO: Make these customizable eventually.
    classifier = "rf"
    feature = "head"

    if classifier not in ["svc", "logit", "rf"]:
        print("Invalid classifier option %s" % classifier)
        return

    if feature == "head":
        features = HeadBytes(head_size=512)
    else:
        raise ValueError("Invalid feature type -- only HEAD supported now.")

    reader = NaiveTruthReader(features)
    experiment(reader, classifier, "outfile", 1, split=0.5)


# Leave this with blank arguments to facilitate re-addition of live-training.
def experiment(reader, classifier_name, outfile, trials, split, debug=False):
    """
    :param reader - System reader with feature already set
    :param classifier_name - a string specifying the classifier type (svc, logit, etc.)
    :param outfile - string with filename of output file
    :param trials - number of randomized trials we run on train/test.
    :param split - n% of data in training set. 100-n% is used for testing.
    :param debug - set to True if debugging the models (for train/test)
    """

    # Get the files on which we need to operate (BATCH-LIST)
    files = get_files()

    # For each file, get the associated sample_estimate.
    trained_classifer = open_model()

    for the_file in files:

        try:
            prediction = predict_single_file(the_file, trained_classifer)

            postgres_update(the_file, prediction)  # TODO: Add time taken once fleshed out.

        except Exception as e:
            # TODO: Multiple possible exceptions in here. Explore further.
            pass


def open_model():
    with open('/src/FTI_Models/training_test.pkl', 'rb') as tr:
        trained_classifier = pickle.load(tr)
        print("Successfully opened trained classifier!")
        return trained_classifier


def predict_single_file(filename, trained_classifier):  # TODO: DO this with names PULLED DOWN from db. :)
    """ Input a single file, featurizes it, and predicts the type based on the trained model. """

    feature_environ = "head"

    if feature_environ == "head":
        features = HeadBytes()
    elif feature_environ == "randhead":
        features = RandHead()
    elif feature_environ == "rand":
        features = RandBytes
    else:
        raise Exception("Not a valid feature set. ")

    reader = FileReader(feature_maker=features, filename=filename)

    reader.run()

    data = [line for line in reader.data][2]

    le = preprocessing.LabelEncoder()  # TODO: Check efficacy. Don't use encoder when training...

    x = np.array(data)
    x = le.fit_transform(x)
    x = [x]

    prediction = trained_classifier.predict(x)

    #  Now convert the label into English :)

    label = (list(label_map.keys())[list(label_map.values()).index(int(prediction[0]))])
    return label


def get_files():

    #TODO: Edit this to make it cleaner.
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query = """SELECT path FROM files WHERE last_extractor = 'init'; """

    cur.execute(query)
    conn.commit()
    results = cur.fetchall()

    unsampled_files = []
    for hit in results:  # TODO: this path correction only called in DEBUG context.
        path = hit[0].replace('/home/ubuntu/', '/home/skluzacek/Downloads/')
        unsampled_files.append(path)

    return unsampled_files


def postgres_update(filename, prediction):  # TODO: Database optimization.
    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()
    query = """UPDATE files SET last_extractor = {0}, done='t' where path = {1};"""
    query = query.format(get_postgres_str(prediction), get_postgres_str(filename))

    cur.execute(query)
    conn.commit()
    conn.close()


def get_postgres_str(obj):
    """ Short helper method to add the apostrophes that postgres wants. Also casts to str. """
    string = "'" + str(obj) + "'"
    return string


if __name__ == '__main__':
    t0 = time.time()
    main()
    t1 = time.time()

    print("Total file sample time: " + str(t1-t0))
    exit()
