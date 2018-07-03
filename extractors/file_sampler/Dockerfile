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


ADD /FTI_Models /src/FTI_Models
COPY /FTI_Models/CLASS_TABLE.json /src/CLASS_TABLE.json


# Run the following command
CMD ["python", "/src/run.py"]