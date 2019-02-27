
import json
import xmltodict
import statistics as s


# Set a depth limit so we don't spend all of our time scouring through an
# infinitely deep file.
depth_limiter = 5


def xml_to_json(xml_file):
    with open(xml_file, 'r') as f:
        xml_string = f.read()
    json_string = json.dumps(xmltodict.parse(xml_string), indent=4)
    return json_string


def get_depth(d, level=1):
    if not isinstance(d, dict) or not d:
        return level
    return max(get_depth(d[k], level + 1) for k in d)


def json_tree_data(d, headers, columns):
    for k, v in d.items():
        if isinstance(v, dict):
            headers.append(k)
            json_tree_data(v, headers, columns)
        else:
            headers.append(k)
            columns[k] = [type(v)]

            if type(v) == list:
                # Step 1: Get the first value.
                presumed_type = type(v[0])
                uniform = all(isinstance(n, type(v[0])) for n in v)

                if presumed_type in [int, float]:
                    meanval = s.mean(v)
                    modeval = s.mode(v)

                    columns[k].append({"mean": meanval, "mode": modeval})

            else:
                print("ADD BACK THE FREETEXT SEARCH FOR STRINGS.")

    return headers, columns


def get_json_metadata(filename):

    freetext_collection = []
    headers = []
    columns = {}

    # Load the data as the json type.
    if filename.endswith(".xml"):
        json_data = json.loads(xml_to_json(filename))
    else:
        with open(filename, 'r') as f:
            json_data = json.load(f)

    # Get depth of json.
    depth = get_depth(json_data)

    # Get type of each level.
    json_tree = json_tree_data(json_data, headers, columns)
    headers = json_tree[0]
    columns = json_tree[1]

    metadata = {"maxdepth": depth, "headers": headers, "columns": columns}
    return metadata
