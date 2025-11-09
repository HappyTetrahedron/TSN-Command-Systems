#!/bin/bash

./generate_maps.sh

. .venv/bin/activate

cd "XML Files"
python render.py

cd ..

if [ -d ~/programs/Artemis_TSN/dat/Missions ]
then
  mkdir -p ~/programs/Artemis_TSN/dat/Missions/MISS_TSN-Command/
  xmllint MISS_TSN-Command.xml > ~/programs/Artemis_TSN/dat/Missions/MISS_TSN-Command/MISS_TSN-Command.xml 
else
  # let's still check that the XML is valid
  xmllint MISS_TSN-Command.xml > /dev/null
fi