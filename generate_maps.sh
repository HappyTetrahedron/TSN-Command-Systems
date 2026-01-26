#!/bin/bash
echo "Generating maps..."

python -m venv .venv
. .venv/bin/activate

pip install jinja2

IFS=''
for file in "XML Files/Legacy Maps/"*.xml
do
    PRINT=false
    START=true
    #echo "  " $file
    of="${file##*Legacy Maps/}"
    while read -r line ; do
        if $START
        then
            echo -n "{# "
            START=false 
        elif [[ $line == *"Coordinate X"* ]]
        then
            va="${line##*value=\"}"
            echo -n x="${va%%\"*} "
        elif [[ $line == *"Coordinate Y"* ]]
        then
            va="${line##*value=\"}"
            echo -n y="${va%%\"*} "
        elif [[ $line == *"Alignment"* ]]
        then
            va="${line##*value=\"}"
            echo -n alignment="${va%%\"*} "
        elif [[ $line == *"</start>"* ]]
        then
            echo "#}"
            PRINT=true
        elif [[ $line == *"</mission_data>"* ]]
        then
            echo "$file" 1>&2
        elif $PRINT
        then
            echo "$line"
        fi
    done < "$file"  > "XML Files/Generated Maps/$of"
done

cd "XML Files/Maps"
for file in *.xml
do
    echo "XML Files/Maps/$file"
    python Generator/parse_xml.py "$file"
done

cd ../../

git add "XML Files/Generated Maps/"*
