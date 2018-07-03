FROM ubuntu:16.04

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python

# Add emergency Docker-volume.
# NOTE: only used in case we can't get r/w permissions on host OS.
VOLUME ["/DataVolume1"]

# Bundle app source
COPY /main.py /src/main.py
COPY /posix_crawler.py /src/posix_crawler.py
COPY /utils.py /src/utils.py

# Run the following command
CMD ["python", "/src/main.py"]
