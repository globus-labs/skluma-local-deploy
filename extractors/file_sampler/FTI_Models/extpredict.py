#!/usr/local/bin/python3

"""
extpredict is a feature selection experiment. It takes a file system, reads in
all files, featurises them somehow and then tries to predict their file extension
(again somehow).
"""
import os
import csv


class FileReader(object):
    """ Takes a single file and turns it into features. """

    def __init__(self, filename, feature_maker):
        """
        top_dir - the starting directory, a string
        feature_maker - an instance of the FileFeature class, where feature
                        extraction logic is located

        """
        if not os.path.isfile(filename):
            raise FileNotFoundError("%s is not a valid directory" % filename)

        self.filename = filename
        self.feature = feature_maker
        self.data = []

    def handle_file(self, filename):

        """put a single file's features into the pot """
        # at some point we may want to parallelize fs traversal, to do that
        # we could make this a standalone function and use pool.map

        try:
            with open(filename, "rb") as open_file:
                extension = get_extension(filename)
                features = self.feature.get_feature(open_file)
                #print("Features are: " + str(features))
                return (['/home/skluzacek', 'newfile.csv', features, extension])

        except (FileNotFoundError, PermissionError):
            pass



    def run(self):
        self.data = self.handle_file(self.filename)



class SystemReader(object):
    """
    Traverses fs, and produces initial dataset for prediction
    """

    def __init__(self, top_dir, feature_maker):
        """
        top_dir - the starting directory, a string
        feature_maker - an instance of the FileFeature class, where feature
                        extraction logic is located

        """
        if not os.path.isdir(top_dir):
            raise NotADirectoryError("%s is not a valid directory" % top_dir)

        self.dirname = top_dir
        self.feature = feature_maker
        self.data = []
        self.next_dirs = []

    def handle_file(self, filename, current_dir):

        """put a single file's features into the pot """
        # at some point we may want to parallelize fs traversal, to do that
        # we could make this a standalone function and use pool.map

        try:
            with open(os.path.join(current_dir, filename), "rb") as open_file:

                extension = get_extension(filename)
                features = self.feature.get_feature(open_file)
                self.data.append([current_dir, filename, features, extension])

        except (FileNotFoundError, PermissionError):
            pass


    def parse_dir(self, dirname):
        """
        parse a directory with path dirname, add subdirs to the list
        to be processed, and add files to feature destination
        """
        files = []

        for name in os.listdir(dirname):
            if name[0] == ".":
                continue  # exclude hidden files and dirs for time being
            if os.path.isfile(os.path.join(dirname, name)):
                files.append(name)
            elif os.path.isdir(os.path.join(dirname, name)):
                self.next_dirs.append(os.path.join(dirname, name))

        for filename in files:
            self.handle_file(filename, dirname)

    def run(self):
        """ run extraction on top_dir"""
        self.next_dirs = [self.dirname]

        while self.next_dirs:
            dirname = self.next_dirs.pop(0)
            self.parse_dir(dirname)


class NaiveTruthReader(object):
    """
    Traverses fs, and produces initial dataset for prediction
    """

    def __init__(self, feature_maker, labelfile="naivetruth.csv"):
        """
        top_dir - the starting directory, a string
        feature_maker - an instance of the FileFeature class, where feature
                        extraction logic is located
        """

        self.feature = feature_maker
        self.data = []
        self.labelfile = labelfile
        self.labeldict = {}

    def run(self):

        with open(self.labelfile, "r") as labelf:

            reader = csv.DictReader(labelf)

            for row in reader:
                try:
                    with open(row["path"], "rb") as open_file:
                        features = self.feature.get_feature(open_file)
                        #print("Features are: " + str(features))
                        append_list = [os.path.dirname(row["path"]), os.path.basename(row["path"]),
                             features, row["file_label"]]


                        self.data.append(append_list)
                except (FileNotFoundError, PermissionError):
                    print("Could not open %s" % row["path"])


def get_extension(filename):
    """
    get the file extension, separate function bc we may want to be smarter about it
    at some point
    """
    if "." not in filename:
        return "None"
    return filename[filename.rfind("."):]
