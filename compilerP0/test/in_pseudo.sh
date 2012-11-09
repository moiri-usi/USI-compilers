#!/bin/bash
##
## Josafat Piraquive
## Simon Maurer
##
## testcases to test generated pseudo assembler code
## using the script x86interp.py

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

## negl
    "x=-1#-1"

## unaryAdd
    "x=+2#2"

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
)
