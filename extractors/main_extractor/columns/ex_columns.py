
"""
    This module extracts metadata from samples deemed 'structured' by the file sampling module. One should be able to
    input any file and this module will return a bunch of structured metdata, including null inference* as a dictionary.  

    Authors: Paul Beckman and Tyler J. Skluzacek 
    Last Edited: 01/21/2018
"""
import sys

import os
import re
from StringIO import StringIO #TODO: Make work in Python3.

from decimal import Decimal
from heapq import nsmallest, nlargest
import pickle as pkl


class ExtractionFailed(Exception):
    """Basic error to throw when an extractor fails"""


class ExtractionPassed(Exception):
    """Indicator to throw when extractor passes for fast file classification"""

sys.path.insert(0, 'columns')

NULL_EPSILON = 1
container_run = '/src/columns/ni_model.pkl'
local_run = 'columns/ni_model.pkl'
pkl_path = "/src/columns/ni_model.pkl"

# Should if 'min', 'max', 'avg' should just return one value (or list of 3).
single_val = True

# load null inference model  # TODO: un-hardcode.


with open(container_run) as model_file:  # Local version
    ni_model = pkl.load(model_file)


# TODO: Fix the Null_Inference=True argument.
def extract_columnar_metadata(file_handle, pass_fail=False, lda_preamble=False, null_inference=False, nulls=None):
    """Get metadata from column-formatted file.
            :param file_handle: (file) open file
            :param pass_fail: (bool) whether to exit after ascertaining file class
            :param lda_preamble: (bool) whether to collect the free-text preamble at the start of the file
            :param null_inference: (bool) whether to use the null inference model to remove nulls
            :param nulls: (list(int)) list of null indices
            :returns: (dict) ascertained metadata
            :raises: (ExtractionFailed) if the file cannot be read as a columnar file"""

    try:
        return _extract_columnar_metadata(
            file_handle, ",",
            pass_fail=pass_fail, lda_preamble=lda_preamble, null_inference=null_inference, nulls=nulls
        )
    except ExtractionFailed:
        try:
            return _extract_columnar_metadata(
                file_handle, "\t",
                pass_fail=pass_fail, lda_preamble=lda_preamble, null_inference=null_inference, nulls=nulls
            )
        except ExtractionFailed:

            try:
                return _extract_columnar_metadata(
                    file_handle, " ",
                    pass_fail=pass_fail, lda_preamble=lda_preamble, null_inference=null_inference, nulls=nulls
                )

            except:
                pass


def _extract_columnar_metadata(file_handle, delimiter, pass_fail=False, lda_preamble=False,
                               null_inference=False, nulls=None):
    """helper method for extract_columnar_metadata that uses a specific delimiter."""

    reverse_reader = ReverseReader(file_handle, delimiter=delimiter)

    # base dictionary in which to store all the metadata
    metadata = {"cols": {}}

    # minimum number of rows to be considered an extractable table
    min_rows = 5
    # number of rows used to generate aggregates for the null inference model
    ni_rows = 100
    # number of rows to skip at the end of the file before reading
    end_rows = 5
    # size of extracted free-text preamble in characters
    preamble_size = 1000

    headers = []
    col_types = []
    col_aliases = []
    num_rows = 0
    # used to check if all rows are the same length, if not, this is not a valid columnar file
    row_length = 0
    is_first_row = True
    fully_parsed = True

    # save the last `end_rows` rows to try to parse them later
    # if there are less than `end_rows` rows, you must catch the StopIteration exception
    last_rows = []
    try:
        last_rows = [reverse_reader.next() for i in range(0, end_rows)]
    except StopIteration:
        pass

    # now we try to extract a table from the remaining n-`end_rows` rows
    for row in reverse_reader:
        # if row is not the same length as previous row, raise an error showing this is not a valid columnar file
        if not is_first_row and row_length != len(row):
            # tables are not worth extracting if under this row threshold
            if num_rows < min_rows:
                raise ExtractionFailed
            else:
                # show that extract failed before we reached the beginning of the file
                fully_parsed = False
                break
        # update row length for next check
        row_length = len(row)

        if is_first_row:
            # make column aliases so that we can create aggregates even for unlabelled columns
            col_aliases = ["__{}__".format(i) for i in range(0, row_length)]
            # type check the first row to decide which aggregates to use
            col_types = ["num" if is_number(field) else "str" for field in row]
            is_first_row = False

        # if the row is a header row, add all its fields to the headers list
        if is_header_row(row):
            # tables are likely not representative of the file if under this row threshold, don't extract metadata
            if num_rows < min_rows:
                raise ExtractionFailed
            # set the column aliases to the most recent header row if they are unique
            # we do this because the most accurate headers usually appear first in the file after the preamble
            if len(set(row)) == len(row):
                for i in range(0, len(row)):
                    metadata["cols"][row[i].lower()] = metadata["cols"].pop(col_aliases[i])
                col_aliases = [header.lower() for header in row]

            for header in row:
                if header != "":
                    headers.append(header.lower())

        else:  # is a row of values
            num_rows += 1
            if not pass_fail:
                add_row_to_aggregates(metadata, row, col_aliases, col_types, nulls=nulls)

        if pass_fail and num_rows >= min_rows:
            raise ExtractionPassed

        # we've taken enough rows to use aggregates for null inference
            #TODO: Add back null inference (1 of 2)
        if null_inference and num_rows >= ni_rows:
            add_final_aggregates(metadata, col_aliases, col_types, num_rows)
            return _extract_columnar_metadata(file_handle, delimiter, pass_fail=pass_fail,
                                              lda_preamble=lda_preamble,
                                              null_inference=False,
                                              nulls=inferred_nulls(metadata))

    # extraction passed but there are too few rows
    if num_rows < min_rows:
        raise ExtractionFailed

    # add the originally skipped rows into the aggregates
    for row in last_rows:
        if len(row) == row_length:
            add_row_to_aggregates(metadata, row, col_aliases, col_types, nulls=nulls)

    add_final_aggregates(metadata, col_aliases, col_types, num_rows)

    # add header list to metadata
    if len(headers) > 0:
        metadata["headers"] = list(set(headers))

    # we've parsed the whole table, now do null inference

    #TODO: Add back inferred nulls.
    if null_inference:
        try:
            return _extract_columnar_metadata(file_handle, delimiter, pass_fail=pass_fail,
                                              lda_preamble=lda_preamble,
                                              null_inference=False,
                                              nulls=inferred_nulls(metadata))
        except:
            return _extract_columnar_metadata(file_handle, delimiter, pass_fail=pass_fail,
                                              lda_preamble=lda_preamble,
                                              null_inference=False,
                                              nulls=None)

    # extract free-text preamble, which may contain headers
    if lda_preamble and not fully_parsed:
        # number of characters in file before last un-parse-able row
        file_handle.seek(reverse_reader.prev_position)
        remaining_chars = file_handle.tell() - 1
        # go to start of preamble
        if remaining_chars >= preamble_size:
            file_handle.seek(-preamble_size, 1)
        else:
            file_handle.seek(0)
        preamble = ""
        # do this `<=` method instead of passing a numerical length argument to read()
        # in order to avoid multi-byte character encoding difficulties
        while file_handle.tell() <= reverse_reader.prev_position:
            preamble += file_handle.read(1)
        # add preamble to the metadata
        if len(preamble) > 0:
            try:
                # convert the preamble string to a file handle to give to the topic extraction method
                preamble_file = StringIO.StringIO(preamble)
                #TODO: Return to Topic and uncomment this.
                #metadata.update(extract_topic(preamble_file, pass_fail=pass_fail))
            except (ExtractionPassed, ExtractionFailed):
                pass

    # remove empty string aggregates that were placeholders in null inference
    for key in metadata["cols"].keys():
        if metadata["cols"][key] == {}:
            metadata["cols"].pop(key)

    #print(metadata)
    return metadata

def add_row_to_aggregates(metadata, row, col_aliases, col_types, nulls=None):
    """Adds row data to aggregates.
        :param metadata: (dict) metadata dictionary to add to
        :param row: (list(str)) row of strings to add
        :param col_aliases: (list(str)) list of headers
        :param nulls: (list(num)) list giving the null value to avoid for each column
        :param col_types: (list("num" | "str")) list of header types"""

    for i in range(0, len(row)):
        value = row[i]
        col_alias = col_aliases[i]
        col_type = col_types[i]
        is_first_row = col_alias not in metadata["cols"].keys()

        if col_type == "num":
            # start off the metadata if this is the first row of values
            if is_first_row:
                metadata["cols"][col_alias] = {
                    "min": [float("inf"), float("inf"), float("inf")],
                    "max": [None, None, None],
                    "total": 0
                }
            # cast the field to a number to do numerical aggregates
            # the try except is used to pass over textual and blank space nulls on which type coercion will fail
            try:
                value = float(value)
                if float(value) == int(value):
                    value = int(value)
            except ValueError:
                # skips adding to aggregates
                continue

            if nulls is not None:
                null = nulls[i]
                # if value is (close enough to) null, don't add it to the aggregates
                # 0 is returned by the model if there is no null value
                if null != 0 and abs(value - null) < NULL_EPSILON:
                    continue

            # add row data to existing aggregates
            mins = list(set(metadata["cols"][col_alias]["min"] + [value]))
            maxes = list(set(metadata["cols"][col_alias]["max"] + [value]))
            metadata["cols"][col_alias]["min"] = nsmallest(3, mins)
            metadata["cols"][col_alias]["max"] = nlargest(3, maxes)
            metadata["cols"][col_alias]["total"] += value

        elif col_type == "str":
            if is_first_row:
                metadata["cols"][col_alias] = {}
            # TODO: add string-specific field aggregates?
            pass

def add_final_aggregates(metadata, col_aliases, col_types, num_rows):
    """Adds row data to aggregates.
        :param metadata: (dict) metadata dictionary to add to
        :param col_aliases: (list(str)) list of headers
        :param col_types: (list("num" | "str")) list of header types
        :param num_rows: (int) number of value rows"""

    # calculate averages for numerical columns
    for i in range(0, len(col_aliases)):
        col_alias = col_aliases[i]

        if col_types[i] == "num":
            #TODO: Uncomment to keep 3 mins and maxes
            # metadata["cols"][col_alias]["max"] = [val for val in metadata["cols"][col_alias]["max"]
            #                                          if val is not None]
            # metadata["cols"][col_alias]["min"] = [val for val in metadata["cols"][col_alias]["min"]
            #                                          if val != float("inf")]

            #print(max(metadata["cols"][col_alias]["min"]))
            metadata["cols"][col_alias]["min"] = str(min(metadata["cols"][col_alias]["min"]))
            metadata["cols"][col_alias]["max"] = str(max(metadata["cols"][col_alias]["max"]))
            ###########

            metadata["cols"][col_alias]["avg"] = str(round(
                float(metadata["cols"][col_alias]["total"]) / num_rows,
                max_precision(float(metadata["cols"][col_alias]["min"]) + float(metadata["cols"][col_alias]["max"]))
            )) #if len(metadata["cols"][col_alias]["min"]) > 0 else None
            #metadata["cols"][col_alias].pop("total")
            metadata["cols"][col_alias]["type"] = str(type(metadata["cols"][col_alias]["max"])).replace('\'', '')

class ReverseReader:
    """Reads column-formatted files in reverse as lists of fields.
        :param file_handle: (file) open file
        :param delimiter: (string) delimiting character """

    def __init__(self, file_handle, delimiter=","):
        self.fh = file_handle
        self.fh.seek(0, os.SEEK_END)
        self.delimiter = delimiter
        self.position = self.fh.tell()
        self.prev_position = self.fh.tell()

    @staticmethod
    def fields(line, delim):
        # if space-delimited, do not keep whitespace fields, otherwise do
        fields = [field.strip() for field in re.split(delim if delim != " " else "\\s", line)]
        if delim in [" ", "\t", "\n"]:
            fields = filter(lambda f: f != "", fields)
        return fields

    def next(self):
        line = ''
        if self.position <= 0:
            raise StopIteration
        self.prev_position = self.position
        while self.position >= 0:
            self.fh.seek(self.position)
            next_char = self.fh.read(1)
            if next_char in ['\n', '\r']:
                self.position -= 1
                if len(line) > 1:
                    return self.fields(line[::-1], self.delimiter)
            else:
                line += next_char
                self.position -= 1
        return self.fields(line[::-1], self.delimiter)

    def __iter__(self):
        return self

def is_header_row(row):
    """Determine if row is a header row by checking that it contains no fields that are
    only numeric.
        :param row: (list(str)) list of fields in row
        :returns: (bool) whether row is a header row"""

    for field in row:
        if is_number(field):
            return False
    return True


def is_number(field):
    """Determine if a string is a number by attempting to cast to it a float.
        :param field: (str) field
        :returns: (bool) whether field can be cast to a number"""

    try:
        float(field)
        return True
    except ValueError:
        return False

def max_precision(nums):
    """Determine the maximum precision of a list of floating point numbers.
        :param nums: (list(float)) list of numbers
        :return: (int) number of decimal places precision"""
    return abs(Decimal(str(nums)).as_tuple().exponent)

def inferred_nulls(metadata):
    """Infer the null value of each column given aggregates.
        :param metadata: (dict) metadata dictionary containing aggregates
        :returns: (list(num)) a list containing the null value for each column"""

    return ni_model.predict(ni_data(metadata))
    #except:
        #print("Null fail")
        #return 0

def ni_data(metadata):
    """Format metadata into a 2D array so that it can be input to the null inference model.
    Columns are:
    [
        "min_1", "min_diff_1", "min_2", "min_diff_1", "min_3",
        "max_1", "max_diff_1", "max_2", "max_diff_1", "max_3",
        "avg"
    ]
        :param metadata: (dict) metadata dictionary containing aggregates
        :returns: (list(list(num))) a 2D array of data"""

    data = [
        [
            col_agg["min"][0] if "min" in col_agg.keys() and len(col_agg["min"]) > 0 else 0,
            col_agg["min"][1] - col_agg["min"][0] if "min" in col_agg.keys() and len(col_agg["min"]) > 1 else 0,
            col_agg["min"][1] if "min" in col_agg.keys() and len(col_agg["min"]) > 1 else 0,
            col_agg["min"][2] - col_agg["min"][1] if "min" in col_agg.keys() and len(col_agg["min"]) > 2 else 0,
            col_agg["min"][2] if "min" in col_agg.keys() and len(col_agg["min"]) > 2 else 0,

            col_agg["max"][0] if "max" in col_agg.keys() and len(col_agg["max"]) > 0 else 0,
            col_agg["max"][0] - col_agg["max"][1] if "max" in col_agg.keys() and len(col_agg["max"]) > 1 else 0,
            col_agg["max"][1] if "max" in col_agg.keys() and len(col_agg["max"]) > 1 else 0,
            col_agg["max"][1] - col_agg["max"][2] if "max" in col_agg.keys() and len(col_agg["max"]) > 2 else 0,
            col_agg["max"][2] if "max" in col_agg.keys() and len(col_agg["max"]) > 2 else 0  #,

            # col_agg["avg"] if "avg" in col_agg.keys() else 0,
        ]
        for col_alias, col_agg in metadata["cols"].iteritems()]


def process_structured_file(full_file_path):
    ''' Little method to open the file path, unpack structured metadata, and return both metadata and any
        freetext found in the file.
        :param str full_file_path path to the file on the system to be extracted. '''

    with open(full_file_path, 'rU') as file_handle:
        metadata = extract_columnar_metadata(file_handle)

        print(metadata)
        sub_extr_data, sub_extr = None, None  # Todo: this would be where we notice freetext in the document.


    return (metadata, sub_extr_data, sub_extr)


# process_structured_file('/home/skluzacek/pub8/examples/58GS20090528.exc.csv')
