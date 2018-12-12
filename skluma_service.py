
import os
import sys
from flask import Flask, request, jsonify, Response



sys.path.insert(0, os.getcwd())  # lets us call sub-packages.

import universal

app = Flask(__name__)

@app.route('/<filename>', methods=['GET'])
def extract_metadata(filename):
    return filename

if __name__ == '__main__':
    app.run(debug=True)