#!/bin/bash

. venv/bin/activate

cd "XML Files"
python render.py

cd ..
xmllint MISS_TSN-Command.xml > ~/programs/Artemis_TSN/dat/Missions/MISS_TSN-Command/MISS_TSN-Command.xml 
