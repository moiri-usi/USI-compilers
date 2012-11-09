#!/bin/bash
##
## usage: ./ig.sh FILE
path=$1
if [[ $path == "" ]]; then
    path="../input/input.p0"
fi
mkdir graph
./../compile.py -ig $path > graph/ig.gv
./../compile.py -ig-color $path > graph/ig-color.gv
dot -Tpng graph/ig.gv -o graph/ig.png
dot -Tpng graph/ig-color.gv -o graph/ig-color.png

gthumb graph/ig.png
rm -r graph
