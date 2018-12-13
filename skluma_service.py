
import os
import json
import sys

from flask import Flask, request, jsonify, Response

sys.path.insert(0, os.getcwd() + '/extractors/universal')  # lets us call sub-packages.

import universal

FILE_STAGING_LOCATION = "/home/tskluzac/Downloads/"

app = Flask(__name__)

@app.route('/<filename>', methods=['GET'])
def extract_metadata(filename):

    metadata = universal.get_metadata(filename, FILE_STAGING_LOCATION)

    json_meta = json.dumps(metadata)
    return json_meta

if __name__ == '__main__':
    app.run(debug=True)
