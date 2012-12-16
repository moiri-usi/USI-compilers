#!/bin/bash
##
## Josafat Piraquive
## Simon Maurer
## (Lothar Rubusch) contributer for prior steps of the project
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
##
## usage: ./test_compile.sh [-pseudo]
##  no param:   run testbench with x86 assembler
##              - use in_x86.sh
##  -pseudo:    run testbench with pseudo assembler
##              - uses script x86interp.py and in_pseude.sh
##  -alloc:     run testbench with allocation assembler
##              - use in_x86.sh
runtime_dir=../runtime/
PSEUDO=0
ALLOC=0
STACK=0
SRC=in_x86.sh
if [[ $1 == "-pseudo" ]]; then
    PSEUDO=1
    SRC=in_pseudo.sh
    echo "PSEUDO-code"
elif [[ $1 == "-alloc" ]]; then
    ALLOC=1
    echo "ALLOC-code"
else
    STACK=1
    echo "STACK-code"
fi

source $SRC

die(){ echo $@ && exit 1; }
generate(){
    RES=0
    if [[ $PSEUDO -eq 1 ]]; then
        echo main: > "./${1}.s"
        python ./../compile.py -pseudo "./${1}.p0" >> "./${1}.s" || RES=1
    elif [[ $ALLOC -eq 1 ]]; then
        python ./../compile.py -alloc "./${1}.p0" > "./${1}.s" || RES=1
    elif [[ $STACK -eq 1 ]]; then
        python ./../compile.py -stack "./${1}.p0" > "./${1}.s" || RES=1
    else
        python ./../compile.py "./${1}.p0" > "./${1}.s" || RES=1
    fi
}

compile(){
    RES=0
    gcc -m32 "${1}.s" $runtime_dir/hashtable.o $runtime_dir/hashtable_itr.o $runtime_dir/hashtable_utility.o $runtime_dir/runtime.o -lm -o "${1}.exe" || RES=1
##    gcc -m32 ./${1}.s ./runtime.c -o ./${1}.exe || RES=1
}

execute()
{
    local tgt=$1
    local expected=$2
    RES=0
    if [[ $PSEUDO -eq 1 ]]; then
        ret="$(./x86interp.py ${tgt}.s)"
    else
        ret="$(./${tgt}.exe)"
    fi
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

        if [[ $PSEUDO -ne 1 ]]; then
            compile "${fnam}"
            if [[ "${RES}" -eq 1 ]]; then
                res="KAPUTT - compile"
                break
            fi
        fi

        execute "${fnam}" "${expect}" || res="KAPUTT - execute"
        if [[ "${RES}" -eq 1 ]]; then
            res="(${ret}/${expect}) KAPUTT - execute"
            break
        fi
        break
    done
    printf "${res}\t\t${op}\n"
    for item in "${fnam}.s" "${fnam}.exe" "${fnam}.p0"; do
        [[ -f "./${item}" ]] && rm "./${item}"
    done
}

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
