FROM ubuntu:16.04

RUN \
  apt-get update && \
  apt-get install -y python python-dev python-pip python-virtualenv && \
  rm -rf /var/lib/apt/lists/* \
  && pip install --upgrade pip \
  && pip install scipy \
  && pip install sklearn \
  && pip install matplotlib \
  && pip install gensim \
  && pip install boto3 \
  && pip install psycopg2 \
  && pip install nltk


# Add emergency Docker-volume.
# NOTE: only used in case we can't get r/w permissions on host OS.
VOLUME ["/DataVolume1"]

# Bundle Topic Source
ADD columns /src/columns
ADD topic /src/topic

# Bundle MAIN source
COPY /main.py /src/main.py
COPY /sqlite_helper.py /src/sqlite_helper.py
COPY /file_type_extensions.py /src/file_type_extensions.py


# Run the following command
CMD ["python", "/src/main.py"]
