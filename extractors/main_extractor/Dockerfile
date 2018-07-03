FROM ubuntu:16.04

RUN \
  apt-get update && \
  apt-get install -y python python-dev python-pip python-virtualenv && \
  rm -rf /var/lib/apt/lists/*

# docker run -P -ti -v /<local-directory>:<local-directory> <name e.g., test1>

# Install app dependencies
RUN pip install --upgrade pip
RUN pip install scipy
RUN pip install sklearn
RUN pip install matplotlib
RUN pip install gensim
RUN pip install boto3
RUN pip install psycopg2
RUN pip install nltk


# Add emergency Docker-volume.
# NOTE: only used in case we can't get r/w permissions on host OS.
VOLUME ["/DataVolume1"]

# Bundle Structured Source
COPY /columns/ex_columns.py /src/columns/ex_columns.py
COPY /columns/ML_util.py /src/columns/ML_util.py
COPY /columns/ni_model.pkl /src/columns/ni_model.pkl
COPY /columns/null_inference.py /src/columns/null_inference.py
COPY /columns/skluma_file_editor.py /src/columns/skluma_file_editor.py

# Bundle Topic Source
COPY /topic/corpus.py /src/topic/corpus.py
COPY /topic/doc_vectors.py /src/topic/doc_vectors.py
COPY /topic/preprocessing.py /src/topic/preprocessing.py
COPY /topic/stop-words-en.txt /src/topic/stop-words-en.txt
COPY /topic/topic_main.py /src/topic/topic_main.py
COPY /topic/vectorizers.py /src/topic/vectorizers.py
COPY /topic/word_vectors.py /src/topic/word_vectors.py

# Bundle MAIN source
COPY /main.py /src/main.py
COPY /postgres_helper.py /src/postgres_helper.py


# Run the following command
CMD ["python", "/src/main.py"]
