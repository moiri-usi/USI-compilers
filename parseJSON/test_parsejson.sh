#!/bin/bash

for (( i=1; i<2; i++ ));
do
    file_name="input_$i"
    python -mjson.tool < $file_name > out1
    python parsejson.py < $file_name > out2
    DIFF=$(diff out1 out2 )
    if [[ $DIFF = "" ]]; then
        echo "$i: OK!"
    else
        echo "$i: NOOOOO, WHAYYYY!?"
    fi
done

