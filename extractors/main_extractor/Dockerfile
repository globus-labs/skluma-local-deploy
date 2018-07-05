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



# Bundle Topic Source
ADD columns /src/columns
ADD topic /src/topic

# Bundle MAIN source
COPY /main.py /src/main.py
COPY /sqlite_helper.py /src/sqlite_helper.py


# Run the following command
CMD ["python", "/src/main.py"]
