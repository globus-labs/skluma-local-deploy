from decimal import Decimal

# container_run = '/src/columns/ni_model.pkl'
# local_run = 'ni_model.pkl'
# pkl_path = "/src/columns/ni_model.pkl"
#
# # load null inference model  # TODO: un-hardcode.
# with open(os.path.abspath(pkl_path)) as model_file:  # Local version
#     # with open(os.path.abspath(local_run)) as model_file:  # Docker version.
#     ni_model = pkl.load(model_file)

def fields(line, delim):
    # if space-delimited, do not keep whitespace fields, otherwise do
    fields = [field.strip(' \n\r\t') for field in line.split(delim)]
    return fields


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
    return max([abs(Decimal(str(num)).as_tuple().exponent) for num in nums])


# def inferred_nulls(metadata):
#     """Infer the null value of each column given aggregates.
#         :param metadata: (dict) metadata dictionary containing aggregates
#         :returns: (list(num)) a list containing the null value for each column"""
#
#     return ni_model.predict(ni_data(metadata))

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
        is_first_row = col_alias not in metadata["columns"].keys()

        if col_type == "num":
            # start off the metadata if this is the first row of values
            if is_first_row:
                metadata["columns"][col_alias] = {
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

            # add row data to existing aggregates #TODO: This in pandas.
            mins = list(set(metadata["columns"][col_alias]["min"] + [value]))
            maxes = list(set(metadata["columns"][col_alias]["max"] + [value]))
            metadata["columns"][col_alias]["min"] = nsmallest(3, mins)
            metadata["columns"][col_alias]["max"] = nlargest(3, maxes)
            metadata["columns"][col_alias]["total"] += value

        elif col_type == "str":
            if is_first_row:
                metadata["columns"][col_alias] = {}
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
            metadata["columns"][col_alias]["max"] = [val for val in metadata["columns"][col_alias]["max"]
                                                     if val is not None]
            metadata["columns"][col_alias]["min"] = [val for val in metadata["columns"][col_alias]["min"]
                                                     if val != float("inf")]

            metadata["columns"][col_alias]["avg"] = round(
                float(metadata["columns"][col_alias]["total"]) / num_rows,
                max_precision(metadata["columns"][col_alias]["min"] + metadata["columns"][col_alias]["max"])
            ) if len(metadata["columns"][col_alias]["min"]) > 0 else None
            metadata["columns"][col_alias].pop("total")