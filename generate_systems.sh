#!/bin/bash
echo "Generating systems..."
IFS=''
for file in "XML Files/Star Systems/"*.xml
do
    PRINT=false
    START=true
    echo "  " $file
    of="${file##*Star Systems/}"
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
    done < "$file"  > "XML Files/Systems (Generated)/$of"
done

git add "XML Files/Systems (Generated)/"*
