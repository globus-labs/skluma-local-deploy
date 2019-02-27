import pandas as pd
from .struct_utils import is_header_row, fields
from ..topic.topic_main import extract_topic

from ..structured.ex_json import get_json_metadata
from ..structured.ex_nc import extract_netcdf_metadata

import csv
import math
from heapq import nlargest

MIN_ROWS = 5

"""
 TODO LIST: 
 5. Data sampling.
 6. Handle 2-line headers. ('/home/skluzacek/pub8/oceans/VOS_Natalie_Schulte_Lines/NS2010_09.csv').
"""


class NonUniformDelimiter(Exception):
    """When the file cannot be pushed into a delimiter. """


def extract_columnar_metadata(filename):
    """Get metadata from column-formatted file.
            :param data: (str) a path to an unopened file.
            :param pass_fail: (bool) whether to exit after ascertaining file class
            :param lda_preamble: (bool) whether to collect the free-text preamble at the start of the file
            :param null_inference: (bool) whether to use the null inference model to remove nulls
            :param nulls: (list(int)) list of null indices
            :returns: (dict) ascertained metadata
            :raises: (ExtractionFailed) if the file cannot be read as a columnar file"""

    # Need to have hard-coded catchings for following specialized formats:
    if filename.endswith(".nc"):

        with open(filename, 'rU') as g:
            metadata = extract_netcdf_metadata(g)
        return metadata
    elif filename.endswith(".xml") or filename.endswith(".json"):
        metadata = get_json_metadata(filename)
        return metadata



    with open(filename, 'rU') as data2:
        # Step 1. Quick scan for number of lines in file.

        line_count = 1
        for _ in data2:
            line_count += 1

        # Step 2. Determine the delimiter of the file.
        delimiter = get_delimiter(filename, line_count)

        # Step 3. Isolate the header data.
        header_info = get_header_info(data2, delim=delimiter)  # TODO: use max-fields of ',', ' ', or '\t'???
        freetext_offset = header_info[0]

        # Seek back to start of file.
        data2.seek(0)

        preamble_metadata = None
        if freetext_offset is None:
            freetext_offset = 0

        # Otherwise, get the preamble and its associated metadata!
        if freetext_offset > 1:
            preamble = [next(data2) for _ in range(freetext_offset)]
            preamble_metadata = extract_topic("subtext", str(preamble))


        header_col_labels = header_info[1]

        # Step 4. Extract content-based metadata.
        if header_col_labels != None:
            dataframes = get_dataframes(filename, header=None, delim=delimiter, skip_rows=freetext_offset + 1)
        else:
            dataframes = get_dataframes(filename, header=None, delim=delimiter, skip_rows=freetext_offset + 1)
    data2.close()

    # Iterate over each dataframe to extract values.
    df_metadata = []
    for df in dataframes:
        metadata = extract_dataframe_metadata(df, header_col_labels)
        df_metadata.append(metadata)

    grand_mdata = {"physical": {"linecount": line_count, "headers": header_col_labels, "delimiter": delimiter, "preamble_length": freetext_offset}, "numeric": {}, "nonnumeric": {}}

    g_means = {}
    g_three_max = {}
    g_three_min = {}
    g_num_rows = {}
    nonnumeric_counter = {}

    # Now REDUCE metadata by iterating over dataframes.
    for md_piece in df_metadata:

        # *** First, we want to aggregate our individual pieces of NUMERIC metadata *** #
        if "numeric" in md_piece:
            col_list = md_piece["numeric"]
            # For every column-level dict of numeric data...

            for col in col_list:
                # TODO: Create rolling update of mean, maxs, mins, row_counts.
                if col["col_id"] not in g_means:
                    g_means[col["col_id"]] = col["metadata"]["mean"]

                    g_three_max[col["col_id"]] = {}
                    g_three_max[col["col_id"]]["max_n"] = col["metadata"]["max_n"]

                    g_three_min[col["col_id"]] = {}
                    g_three_min[col["col_id"]]["min_n"] = col["metadata"]["min_n"]

                    g_num_rows[col["col_id"]] = {}
                    g_num_rows[col["col_id"]]["num_rows"] = col["metadata"]["num_rows"]

                else:
                    g_means[col["col_id"]] += col["metadata"]["mean"]
                    g_three_max[col["col_id"]]["max_n"].extend(col["metadata"]["max_n"])
                    g_three_min[col["col_id"]]["min_n"].extend(col["metadata"]["min_n"])
                    g_num_rows[col["col_id"]]["num_rows"] += col["metadata"]["num_rows"]

        if "nonnumeric" in md_piece:
            col_list = md_piece["nonnumeric"]

            # For every column-level dictionary.
            for col in col_list:

                if col["col_id"] not in nonnumeric_counter:

                    nonnumeric_counter[col["col_id"]] = {}

                # Count the items in the md_piece['metadata']['top_3_modes']
                for mode in col["metadata"]["top3_modes"]:

                    if mode not in nonnumeric_counter[col["col_id"]]:
                        nonnumeric_counter[col["col_id"]][mode] = col["metadata"]["top3_modes"][mode]

                    else:
                        nonnumeric_counter[col["col_id"]][mode] += col["metadata"]["top3_modes"][mode]

    # Just use the g_means key, because its keys must appear in all summary stats anyways.
    for col_key in g_means:

        grand_mdata["numeric"][col_key] = {}
        grand_mdata["numeric"][col_key]["mean"] = float(g_means[col_key] / g_num_rows[col_key]["num_rows"])
        grand_mdata["numeric"][col_key]["num_rows"] = g_num_rows[col_key]["num_rows"]

        sorted_max = sorted(g_three_max[col_key]["max_n"], reverse=True)
        sorted_min = sorted(g_three_min[col_key]["min_n"], reverse=False)

        grand_mdata["numeric"][col_key]["max_n"] = sorted_max[:3]
        grand_mdata["numeric"][col_key]["min_n"] = sorted_min[:3]

    nonnumeric_metadata = {}
    for col_key in nonnumeric_counter:

        my_dict = nonnumeric_counter[col_key]
        three_largest = nlargest(3, my_dict, key=my_dict.get)
        nonnumeric_metadata[col_key] = {"sampled_top3_modes": three_largest}

    grand_mdata["nonnumeric"] = nonnumeric_metadata
    grand_mdata["freetext_keywords"] = preamble_metadata

    return grand_mdata


def extract_dataframe_metadata(df, header):
    # Get only the numeric columns in data frame.
    ndf = df._get_numeric_data()

    # Get only the string columns in data frame.
    sdf = df.select_dtypes(include=[object])

    ndf_tuples = []

    for col in ndf:

        largest = df.nlargest(3, columns=col, keep='first')  # Output dataframe ordered by col.
        smallest = df.nsmallest(3, columns=col, keep='first')
        the_mean = ndf[col].mean()

        # Use GROUP_BY and then MEAN.
        col_maxs = largest[col]
        col_mins = smallest[col]

        maxn = []
        minn = []
        for maxnum in col_maxs:
            maxn.append(maxnum)

        for minnum in col_mins:
            minn.append(minnum)

        # (header_name (or index), [max1, max2, max3], [min1, min2, min3], avg)
        if header is not None:
            ndf_tuple = {"col_id": header[col],
                         "metadata": {"num_rows": len(ndf), "min_n": minn, "max_n": maxn, "mean": the_mean}}
        else:
            ndf_tuple = {"col_id": "__{}__".format(col),
                         "metadata": {"num_rows": len(ndf), "min_n": minn, "max_n": maxn, "mean": the_mean}}
        ndf_tuples.append(ndf_tuple)

    # TODO: Repeated column names? They would just overwrite.
    nonnumeric_metadata = []

    # Now get the nonnumeric data tags.
    for col in sdf:
        # Mode tags represent the three most prevalent values from each paged dataframe.
        nonnumeric_top_3_df = sdf[col].value_counts().head(3)

        nonnum_col = {}

        col_modes = {}
        for row in nonnumeric_top_3_df.iteritems():
            col_modes[row[0]] = row[1]

        if header is not None:
            nonnum_col["col_id"] = header[col]
            nonnum_col["metadata"] = {"top3_modes": col_modes}

        else:
            nonnum_col["col_id"] = "__{}__".format(col)
            nonnum_col["metadata"] = {"top3_modes": col_modes}

        nonnumeric_metadata.append(nonnum_col)

    df_metadata = {"numeric": ndf_tuples, "nonnumeric": nonnumeric_metadata}

    return df_metadata


def get_delimiter(filename, numlines):
    # Step 1: Load last min_lines into dataframe.  Just to ensure it can be done.
    pd.read_csv(filename, skiprows=numlines - MIN_ROWS, error_bad_lines=False)

    # Step 2: Get the delimiter of the last n lines.
    s = csv.Sniffer()
    with open(filename, 'r') as fil:
        i = 1
        delims = []
        for line in fil:
            if i > numlines - MIN_ROWS and ('=' not in line):
                delims.append(s.sniff(line).delimiter)
            i += 1

        if delims.count(delims[0]) == len(delims):
            return delims[0]
        else:
            raise NonUniformDelimiter("Error in get_delimiter")


def get_dataframes(filename, header, delim, skip_rows=0, dataframe_size=1000):
    iter_csv = pd.read_csv(filename, sep=delim, chunksize=10000, header=None, skiprows=skip_rows,
                           error_bad_lines=False, iterator=True)

    return iter_csv


def count_fields(dataframe):
    return dataframe.shape[1]


# Currently assuming short freetext headers.
def get_header_info(data, delim):
    data.seek(0)
    # Get the line count.
    line_count = 0
    for _ in data:
        line_count += 1

    # Figure out the length of file via binary search (in"seek_preamble")
    if line_count >= 5:  # set arbitrary min value or bin-search not useful.
        # A. Get the length of the preamble.
        preamble_length = _get_preamble(data, delim)

        # B. Determine whether the next line is a freetext header
        data.seek(0)

        header = None
        for i, line in enumerate(data):

            if preamble_length == None:
                header = None
                break
            if i == preamble_length:  # +1 since that's one after the preamble.

                has_header = is_header_row(fields(line, delim))
                if has_header:  # == True
                    header = fields(line, delim)
                else:
                    header = None

            elif i > preamble_length:
                break

        return preamble_length, header


def _get_preamble(data, delim):
    data.seek(0)
    max_nonzero_row = None
    max_nonzero_line_count = None
    last_preamble_line_num = None

    # *** Get number of delimited columns in last nonempty row (and row number) *** #
    delim_counts = {}
    for i, line in enumerate(data):
        cur_line_field_count = len(line.split(delim))

        if cur_line_field_count != 0:
            delim_counts[i] = cur_line_field_count
            max_nonzero_row = i
            max_nonzero_line_count = cur_line_field_count

    # [Weed out complicated cases] Now if the last three values are all the same...
    if delim_counts[max_nonzero_row] == delim_counts[max_nonzero_row - 1] == delim_counts[max_nonzero_row - 2]:
        # Now binary-search from the end to find the last row with that number of columns.
        starting_row = math.floor(max_nonzero_row - 2) / 2  # Start in middle of file for sanity.
        last_preamble_line_num = _last_preamble_line_bin_search(delim_counts, max_nonzero_line_count, starting_row,
                                                                upper_bd=0, lower_bd=max_nonzero_row - 2)

    return last_preamble_line_num


def _last_preamble_line_bin_search(field_cnt_dict, target_field_num, cur_row, upper_bd=None, lower_bd=None):
    # Check current row and next two to see if they are all the target value.
    cur_row = math.floor(cur_row)

    # If so, then we want to move up in the file.
    if field_cnt_dict[cur_row] == field_cnt_dict[cur_row + 1] == field_cnt_dict[cur_row + 2] == target_field_num:

        new_cur_row = cur_row - math.floor((cur_row - upper_bd) / 2)

        # If we're in the first row, we should return here.
        if cur_row == 1 and field_cnt_dict[cur_row - 1] == field_cnt_dict[cur_row] == target_field_num:
            return 0

        elif cur_row == 1 and field_cnt_dict[cur_row - 1] != target_field_num:
            return 1

        else:
            recurse = _last_preamble_line_bin_search(field_cnt_dict, target_field_num, new_cur_row,
                                                     upper_bd=upper_bd, lower_bd=cur_row)
            return recurse

    elif field_cnt_dict[cur_row] == field_cnt_dict[cur_row + 1] == target_field_num:
        return cur_row + 1

    # If not, then we want to move down in the file.
    else:
        new_cur_row = cur_row + math.floor((lower_bd - cur_row) / 2)

        if cur_row == new_cur_row:
            return cur_row + 1

        recurse = _last_preamble_line_bin_search(field_cnt_dict, target_field_num, new_cur_row,
                                                 upper_bd=cur_row, lower_bd=lower_bd)
        return recurse
