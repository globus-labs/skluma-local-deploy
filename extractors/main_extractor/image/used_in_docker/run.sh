#!/usr/bin/env bash

#cd files_to_container
docker build -t test files_to_container
docker run -v /Users/skluzacek@ibm.com/Desktop/used_in_docker/images:/test/images -v /Users/skluzacek@ibm.com/Desktop/used_in_docker/model:/test/model -v /Users/skluzacek@ibm.com/Desktop/used_in_docker/prediction:/test/prediction -v /Users/skluzacek@ibm.com/Desktop/used_in_docker/src:/test/src test bash run_inside_container.sh