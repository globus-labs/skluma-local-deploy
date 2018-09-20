FROM ubuntu:16.04

RUN \
  apt-get update && \
  apt-get install -y python python-pip\
  && rm -rf /var/lib/apt/lists/*

RUN \
  pip install scipy \
  && pip install sklearn \
  && pip install gensim \
  && pip install nltk \
  && pip install xmltodict

RUN \
  pip install netCDF4 \
  && pip install statistics

# Add emergency Docker-volume.
# NOTE: only used in case we can't get r/w permissions on host OS.
VOLUME ["/DataVolume1"]

# Bundle Topic Source
ADD columns /src/columns
ADD topic /src/topic
ADD structured /src/structured

# Bundle MAIN source
COPY /main.py /src/main.py
COPY /sqlite_helper.py /src/sqlite_helper.py
COPY /file_type_extensions.py /src/file_type_extensions.py


# Run the following command
CMD ["python", "/src/main.py"]
