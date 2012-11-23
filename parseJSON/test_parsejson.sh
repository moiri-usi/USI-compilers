#!/bin/bash
ifolder="ilegal_test"
ifile="ilegal_test_json_"
lfolder="legal_test"
lfile="input_legal_json_"
icnt=$(ls $ifolder/ | wc -l)
lcnt=$(ls $lfolder/ | wc -l)

for (( i=1; i<=$lcnt; i++ ));
do
    file_name="$lfolder/$lfile$i"
    python -mjson.tool < $file_name > out1
    python parsejson.py < $file_name > out2
    DIFF=$(diff out1 out2 )
    if [[ $DIFF = "" ]]; then
        echo "$i: LEGAL OK!"
    else
        echo "$i: LEGAL NOOOOO, WHAYYYY!?"
        echo $DIFF
    fi
done

for (( i=1; i<=$icnt; i++ ));
do
    file_name="$ifolder/$ifile$i"
    python -mjson.tool < $file_name 2> out1
    python parsejson.py < $file_name 2> out2
    STR1=$(cat out1 )
    STR2=$(cat out2 )
    if [[ (-n $STR1) && (-n $STR2) ]]; then
        echo "$i: ILEGAL OK!"
    else
        echo "$i: ILEGAL NOOOOO, WHAYYYY!?"
    fi
done

rm out1 out2
