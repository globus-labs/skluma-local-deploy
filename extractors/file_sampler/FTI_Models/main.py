#!/usr/local/bin/python3

"""
This main script handles both the training and prediction tasks of the
file forensic byte-level predictor.This is constructed to run in a Python3
Docker container, but can be easily adapted otherwise.

    Authors: Galen Harrison and Tyler Skluzacek (skluzacek@uchicago.edu)
    Last Edited: 02/03/2018
"""

import argparse
import json
import os
import pickle
import time

import numpy as np
#import psycopg2
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


def main():
    # Uncomment to train model.
    parser = argparse.ArgumentParser(description='Run file classification experiments')

    parser.add_argument("dirname", type=str)
    parser.add_argument("--n", type=int, default=1, help="number of trials", dest="n")  # TODO: set to 10 for train/test
    parser.add_argument("classifier", type=str,
                        help="classifier to use, (svc|logit|rf)")
    parser.add_argument("feature", type=str,
                        help="feature to use, (head|rand|randhead|ngram|randngram)")
    parser.add_argument("--split", type=float, default=0.8, help="test/train split ratio", dest="split")
    parser.add_argument("--out", type=str, default="out.csv", dest="outfile",
                        help="file to write out results to")
    parser.add_argument("--head-bytes", type=int, default=512, dest="head_bytes",
                        help="size of file head in bytes, default 512, used for head and randhead")
    parser.add_argument("--rand-bytes", type=int, default=512, dest="rand_bytes",
                        help="number of random bytes, default 512, used in rand, randhead, and randngram")
    parser.add_argument("--ngram", type=int, dest="ngram", default=1, help="n for the ngram")

    args = parser.parse_args()

    if args.classifier not in ["svc", "logit", "rf"]:
        print("Invalid classifier option %s" % args.classifier)
        return

    if args.feature == "head":
        features = HeadBytes(head_size=args.head_bytes)
    elif args.feature == "rand":
        features = RandBytes(number_bytes=args.rand_bytes)
    elif args.feature == "randhead":
        features = RandHead(head_size=args.head_bytes, rand_size=args.rand_bytes)
    elif args.feature == "ngram":
        features = Ngram(args.ngram)
    elif args.feature == "randngram":
        features = RandNgram(args.ngram, args.rand_bytes)
    else:
        print("Invalid feature option %s" % args.feature)
        return

    reader = NaiveTruthReader(features)
    # reader = SystemReader(args.dirname, features)
    experiment(reader, args.classifier, args.outfile, args.n, split=args.split)
    # get_files()
    #TODO: Predict a whole bunch of files here???


def experiment(reader, classifier_name, outfile, trials, split, debug=False):
    """
    :param reader - System reader with feature already set
    :param classifier_name - a string specifying the classifier type (svc, logit, etc.)
    :param outfile - string with filename of output file
    :param trials - number of randomized trials we run on train/test.
    :param split - n% of data in training set. 100-n% is used for testing.
    :param debug - set to True if debugging the models (for train/test)
    """

    read_start_time = time.time()
    reader.run()
    read_time = time.time() - read_start_time

    classifier = ClassifierBuilder(reader, classifier=classifier_name, split=split)
    classifier.train()

    if debug:
        # Debug=True to run the experiments. Won't need to call 'classifier.train()' above. :)
        for i in range(trials):
            print("Running", i, "/", trials, "th trial")

            classifier_start = time.time()
            classifier.train()
            accuracy = classifier.test()
            classifier_time = time.time() - classifier_start

            with open(outfile, "a") as data_file:
                data_file.write(str(accuracy) + "," + str(read_time) + "," + str(classifier_time) +
                                "," + reader.feature.name + "," + classifier_name + "\n")

            if i != trials - 1:
                classifier.shuffle()

    # Get the files on which we need to operate (BATCH-LIST)
    files = get_files()

    # For each file, get the associated sample_estimate.
    trained_classifer = open_model()

    for the_file in files:

        try:
            t1 = time.time()
            prediction = predict_single_file(the_file, trained_classifer)
            t2 = time.time()

            postgres_update(the_file, prediction)  # TODO: Add time taken once fleshed out.
            print("Prediction Time: " + str(t2-t1))

        except:  # TODO: Too broad exception clause.
            pass


def open_model():
    with open('training_test.pkl', 'rb') as tr:
        trained_classifier = pickle.load(tr)
        print("Successfully opened trained classifier!")
        return trained_classifier


def predict_single_file(filename, trained_classifier):  # TODO: DO this with names PULLED DOWN from db. :)
    """ Input a single file, featurizes it, and predicts the type based on the trained model. """

    #feature_environ = os.environ["FEATURES"] #TODO: Make general
    feature_environ = "head"

    if feature_environ == "head":
        features = HeadBytes()
    elif feature_environ == "randhead":
        features = RandHead()
    elif feature_environ == "rand":
        features = RandBytes
    else:
        raise Exception("Not a valid feature set. ")

    # features = RandHead()
    reader = FileReader(feature_maker=features, filename=filename)

    reader.run()

    data = [line for line in reader.data][2]

    le = preprocessing.LabelEncoder()  # TODO: Check efficacy. Don't use encoder when training...

    x = np.array(data)
    x = le.fit_transform(x)
    x = [x]

    prediction = trained_classifier.predict(x)

    #  Now convert the label into English :)
    label_map = os.environ["CLASS_TABLE"].replace("'", "\"")
    label_map = json.loads(label_map)
    label = (list(label_map.keys())[list(label_map.values()).index(int(prediction[0]))])
    print(label)

    return label


def get_files():

    #TODO: ADD SQLITE3 FUNCTIONALITY.
    conn = sqlite3.connect()
    cur = conn.cursor()
    query = """SELECT path FROM files2 WHERE last_extractor = 'sampler'; """

    cur.execute(query)
    conn.commit()
    results = cur.fetchall()

    unsampled_files = []
    for hit in results:  # TODO: Get rid of the path issue here.
        path = hit[0].replace('/home/ubuntu/', '/home/skluzacek/Downloads/')
        unsampled_files.append(path)

    return unsampled_files


def postgres_update(filename, prediction):  # TODO: Database optimization.
    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()  # TODO: Add sampler to extractor list :)
    query = """UPDATE files2 SET last_extractor = {0}, done='t' where path = {1};"""
    query = query.format(get_postgres_str(prediction), get_postgres_str(filename))

    cur.execute(query)
    conn.commit()
    conn.close()


def get_postgres_str(obj):
    """ Short helper method to add the apostrophes that postgres wants. Also casts to str. """
    string = "'" + str(obj) + "'"
    return string


if __name__ == '__main__':
    while True:
        main()
