FROM ubuntu:16.04

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

# docker run -P -ti -v /<local-directory>:<local-directory> <name e.g., test1>

# Update
# RUN apt-get update python py-pip
RUN pip3 install globus-sdk

# Install app dependencies
# RUN pip install matplotlib

# Add emergency Docker-volume.
# NOTE: only used in case we can't get r/w permissions on host OS.
VOLUME ["/DataVolume1"]

# Bundle app source
COPY /main.py /src/main.py
COPY /posix_crawler.py /src/posix_crawler.py
COPY /utils.py /src/utils.py


#COPY /tmp/skluma-db3.db /src/tmp/skluma-db3.db

# Run the following command
CMD ["python", "/src/main.py"]
