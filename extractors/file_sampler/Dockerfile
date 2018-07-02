FROM ubuntu:16.04
# Note: 16.04 ships w/ both Py2 and Py3 installed :)

RUN \
  apt-get update && \
  apt-get install -y python python-dev python-pip python3-pip python-virtualenv && \
  rm -rf /var/lib/apt/lists/*


# docker run -P -ti -v /<local-directory>:<local-directory> <name e.g., test1>


# Install app dependencies
RUN pip install --upgrade pip
RUN pip3 install scipy
RUN pip3 install sklearn
RUN pip3 install matplotlib
RUN pip3 install gensim
RUN pip3 install boto3
RUN pip3 install psycopg2
RUN pip3 install numpy


# Add emergency Docker-volume.
# NOTE: only used in case we can't get r/w permissions on host OS.
VOLUME ["/DataVolume1"]


# Bundle app source
COPY /run.py /src/run.py
COPY /naivetruth.csv /src/naivetruth.csv

COPY /FTI_Models/classify.py /src/FTI_Models/classify.py
COPY /FTI_Models/extpredict.py /src/FTI_Models/extpredict.py
COPY /FTI_Models/feature.py /src/FTI_Models/feature.py
COPY /FTI_Models/headbytes.py /src/FTI_Models/headbytes.py
COPY /FTI_Models/main.py /src/FTI_Models/main.py
COPY /FTI_Models/ngram.py /src/FTI_Models/ngram.py
COPY /FTI_Models/randbytes.py /src/FTI_Models/randbytes.py
COPY /FTI_Models/randhead.py /src/FTI_Models/randhead.py
COPY /FTI_Models/randngram.py /src/FTI_Models/randngram.py


# Run the following command
CMD ["python", "/src/run.py"]