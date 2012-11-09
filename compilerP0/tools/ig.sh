#!/bin/bash
##
## usage: ./ig.sh FILE

mkdir graph
./../compile.py -ig $1 > graph/ig.gv
./../compile.py -ig-color $1 > graph/ig-color.gv
dot -Tpng graph/ig.gv -o graph/ig.png
dot -Tpng graph/ig-color.gv -o graph/ig-color.png

gthumb graph/ig.png
rm -r graph
