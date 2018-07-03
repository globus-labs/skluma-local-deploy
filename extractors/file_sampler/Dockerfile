FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y python python-dev python-pip python3-pip python-virtualenv && \
    rm -rf /var/lib/apt/lists/*

# Install app dependencies
RUN pip install --upgrade pip \
    && pip3 install scipy \
    && pip3 install sklearn \
    && pip3 install matplotlib \
    && pip3 install gensim \
    && pip3 install numpy

# Add emergency Docker-volume.
# NOTE: only used in case we can't get r/w permissions on host OS.
VOLUME ["/DataVolume1"]

# Bundle app source
COPY /run.py /src/run.py

# TODO: Switch to a single directory-ADD.
COPY /FTI_Models/classify.py /src/FTI_Models/classify.py
COPY /FTI_Models/extpredict.py /src/FTI_Models/extpredict.py
COPY /FTI_Models/feature.py /src/FTI_Models/feature.py
COPY /FTI_Models/headbytes.py /src/FTI_Models/headbytes.py
COPY /FTI_Models/main.py /src/FTI_Models/main.py
COPY /FTI_Models/ngram.py /src/FTI_Models/ngram.py
COPY /FTI_Models/randbytes.py /src/FTI_Models/randbytes.py
COPY /FTI_Models/randhead.py /src/FTI_Models/randhead.py
COPY /FTI_Models/randngram.py /src/FTI_Models/randngram.py
COPY /FTI_Models/training_test.pkl /src/FTI_Models/training_test.pkl
COPY /FTI_Models/naive_truth.csv /src/FTI_Models/naive_truth.csv



# Run the following command
CMD ["python", "/src/run.py"]