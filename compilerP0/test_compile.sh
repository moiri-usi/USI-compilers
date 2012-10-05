#!/bin/bash
##
## needs "printnl()" running
## no "input()" test
## all needs to be assigned to 'x='
##
## generates .s
## compiles .s to .exe
## executes .exe

die(){ echo $@ && exit 1; }
generate(){
    RES=0
    python ./compile.py "./${1}.p0" > "./${1}.s" || RES=1
}

compile(){
    RES=0
    gcc -m32 ./${1}.s ./runtime.c -o ./${1}.exe || RES=1
}

execute()
{
    local tgt=$1
    local expected=$2
    RES=0
    ret="$(./${tgt}.exe)"
    printf "${ret}\t\t"   
    if [[ "${ret}" == "${expected}" ]]; then
        return
    fi
    RES=1 # failed
}

tst()
{
    local op="$1"
    local expect="$2"
    local res="iiTZOK! "
    let NUM+=1
    local fnam="test${NUM}"
    [[ -f "./${fnam}.p0" ]] && die "file './${fnam}.p0' already exists"
    echo "${op}" >> "./${fnam}.p0"
    echo "print x" >> "./${fnam}.p0"
    while [[ 1 ]]; do
        generate "${fnam}"
        if [[ "${RES}" -eq 1 ]]; then
            res="FAIL - generate"
            break
        fi

        compile "${fnam}"
        if [[ "${RES}" -eq 1 ]]; then
            res="FAIL - compile"
            break
        fi

        execute "${fnam}" "${expect}" || res="FAIL - execute"
        if [[ "${RES}" -eq 1 ]]; then
            res="FAIL - execute"
            break
        fi
        break
    done
    printf "${res}\t\t${op}\n"
    for item in "${fnam}.s" "${fnam}.exe" "${fnam}.p0"; do
        [[ -f "./${item}" ]] && rm "./${item}"
    done
}


##


lst=(
## add
    "x=2+3#5"
    "x=2+3+4#9"

## sub
    "x=3-2#1"
    "x=7-2-2#3"

## mul
    "x=2*3#6"
    "x=2*3*4#24"

## bitand
    "x=1&0#0"
    "x=1&1&0#0"
    "x=1&1&1&0#0"
    "x=1&1&1&1#1"

    "x=1&0&1#0"
    "x=1&0&1&1#0"

## bitor
    "x=1|0#1"
    "x=1|1|0#1"
    "x=1|1|1|0#1"
    "x=0|0|0|0#0"

    "x=0|1#1"
    "x=0|0|1#1"
    "x=0|0|0|1#1"

    "x=7|5|0|1#7"

## bitxor
    "x=1^0#1"
    "x=1^1#0"
    "x=1^1^1#1"
    "x=1^1^1^1#0"
    "x=1^1^1^0#1"

## leftshift
    "x=16<<2#64"

## rightshift
    "x=64>>2#16"
)

#set -x   
NUM=0
RES=0
for testcase in "${lst[@]}"; do
    term=$(echo $testcase | sed -e 's/#/ /g' | awk '{print $1}' )
    expct=$(echo $testcase | sed -e 's/#/ /g' | awk '{print $2}' )
    tst $term $expct
done

echo
echo
echo "DATAZAAAD CANNOT OkuR - WAaaaaaaiiiIIYYY!!!!"
echo