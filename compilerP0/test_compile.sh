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
generate(){ python ./compile.py ${1}.py > ./${1}.s || return 1; }
compile(){ gcc -m32 ./${1}.s ./runtime.c -o ./${1}.exe || return 1; }

execute()
{
    local tgt=$1
    local expected=$2
    ret="$(./${tgt}.exe)"
    [[ "${ret}" == "${expected}" ]] && return 0
    return 1
}

tst()
{
    local op="$1"
    local expect="$2"
    local res="OK"
    let NUM+=1
    local fnam="test${NUM}"
    [[ -f "./${fnam}.p0" ]] && die "file './${fnam}' already exists"
    echo "${op}" >> "./${fnam}.p0"
    echo "print x" >> "./${fnam}.p0"
    while [[ 1 ]]; do
        generate "${fnam}" || res="FAIL - generate" && break
        compile "${fnam}" || res="FAIL - compile" && break
        execute "${fnam}" "${expect}" || res="FAIL - execute" && break
        break
    done
    printf "${res}\t\t${op}\n"
    for item in "${fnam}.s" "${fnam}.exe" "${fnam}.p0"; do
        [[ -f "./${item}" ]] && rm "./${item}"
    done
}


##


lst=(
    "x=2+3#5"
    "x=2+3+4#9"

    "x=3-2#1"
    "x=7-2-2#3"

    "x=2*3#6"
    "x=2*3*4#24"

    "x=1&0#0"
    "x=1&1&1&1#1"
    "x=1&1&1&0#0"

    "x=1|0#1"
    "x=1|1|1|1#1"
    "x=0|0|1|1#1"

    
)

#set -x   
NUM=0
for testcase in "${lst[@]}"; do
    term=$(echo $testcase | sed -e 's/#/ /g' | awk '{print $1}' )
    expct=$(echo $testcase | sed -e 's/#/ /g' | awk '{print $2}' )
    tst $term $expct
done

echo "READY. - '$NUM'"
