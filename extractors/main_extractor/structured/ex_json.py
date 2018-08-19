
import json
import xmltodict


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
            print(k)
            headers.append(k)
            columns.append({k: type(v)})

    return headers, columns


def get_json_metadata(filename):

    freetext_collection = []
    headers = []
    columns = []

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

    for col in columns:
        # TODO: Put this into the json_tree stuff.
        # TODO: Check to see if can be cast as numeric.
        # TODO: Get mean, median, and 3-mode.
        print("This is a column. ")

    print(depth)
    print(headers)
    print(columns)
    # print(columns)
    # print(json_data)

get_json_metadata("/home/skluzacek/Desktop/sample.xml")
get_json_metadata("/home/skluzacek/skluma_cfg.json")


