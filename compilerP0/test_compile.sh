#!/bin/bash
##
## Lothar Rubusch
## Simon Maurer
## Josafat Piraquive
##
##
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
#    printf "${ret}\t\t"   
    if [[ "${ret}" == "${expected}" ]]; then
        return
    fi
    RES=1 # failed
}

tst()
{
    local op="$1"
    local expect="$2"
    local res="IitZ.ok! "
    let NUM+=1
    local fnam="test${NUM}"
    [[ -f "./${fnam}.p0" ]] && die "file './${fnam}.p0' already exists"
    echo "${op}" >> "./${fnam}.p0"
    echo "print x" >> "./${fnam}.p0"
    while [[ 1 ]]; do
        generate "${fnam}"
        if [[ "${RES}" -eq 1 ]]; then
            res="KAPUTT - generate"
            break
        fi

        compile "${fnam}"
        if [[ "${RES}" -eq 1 ]]; then
            res="KAPUTT - compile"
            break
        fi

        execute "${fnam}" "${expect}" || res="KAPUTT - execute"
        if [[ "${RES}" -eq 1 ]]; then
            res="KAPUTT - execute"
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
    "x=0+0#0"
    "x=2+0#2"
    "x=2+3#5"
    "x=2+3+4#9"
    "x=2+3+4+5#14"

## sub
    "x=0-0#0"
    "x=3-0#3"
    "x=3-2#1"
    "x=7-2-2#3"
    "x=7-2-3-4#-2"

## mul
    "x=0*0#0"
    "x=1*0#0"
    "x=2*3#6"
    "x=2*3*4#24"
    "x=2*3*4*5#120"

## bitand
    "x=0&0#0"
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

## bitxor
    "x=1^0#1"
    "x=1^1#0"
    "x=1^1^1#1"
    "x=1^1^1^1#0"
    "x=1^1^1^0#1"

## leftshift
    "x=16<<2#64"
    "x=7<<3#56"
    "x=123<<7#15744"
    "x=0<<5#0"
    "x=1<<16#65536"

## rightshift
    "x=64>>2#16"
    "x=64>>0#64"
    "x=123>>7#0"
    "x=123>>2#30"
    "x=65536>>16#1"
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
echo "Ok. DATAZAAAD cannot OkuR! - WhAaaaaaaiIIYYY??!!!"
echo
