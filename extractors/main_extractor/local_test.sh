#!/usr/bin/env bash

echo Building main container...
sudo docker build -t main-container .

echo Running main container...
sudo docker run -v /home/skluzacek/:/home/skluzacek/ main-container

