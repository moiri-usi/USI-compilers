#/bin/sh

function help() {
    echo usage: $(basename $0) [options] file1.py file2.py ...
    echo "  options:"
    echo "    --dir <dir>          output directory"
    echo "    --ccopts <options>   options to pass to gcc (default: -m32)"
    echo "    --runtime <file>     runtime library (default: runtime.c)"
    echo "    --help               this message"
    exit 0
}

runtime=runtime.c
ccopts=-m32
dir=.

state=''

for arg in "$@"; do
  case "$state" in
    '')
      case "$arg" in
        --runtime) state=$arg
          ;;
        --ccopts) state=$arg
          ;;
        --dir) state=$arg
          ;;
        --help)
          help
          exit 0
          ;;
        -*)
          help
          exit 1
          ;;
        *)
          break
          ;;
      esac
      ;;
    --runtime)
      runtime="$arg"
      state=''
      ;;
    --ccopts)
      ccopts="$arg"
      state=''
      ;;
    --dir)
      dir="$arg"
      state=''
      ;;
    *)
      break
      ;;
  esac
done

if [ $# -eq 0 ]; then
  help
  exit 1
fi

mkdir -p "$dir" 2> /dev/null

if [ ! -d "$dir" ]; then
  echo "$dir" not found
  exit 1
fi

gcc $ccopts -c $runtime -o "$dir/runtime.o"

for testpy in "$@"; do
  (
    cd "$dir"

    test=${testpy%%.py}

    in="$test.in"
    if [ ! -f "$in" ]; then
      in=/dev/null
    fi

    out="$test.out"
    if [ ! -f "$out" ]; then
      out=/dev/null
    fi

    # compile to .s
    python compile.py "$test.py" > "$test.s"
    gcc $ccopts "$test.s" runtime.o -o "$test"

    "./$test" < "$in" > "$test.test"

    if diff "$out" "$test.test" > /dev/null 2>&1; then
      echo "$test" ok
    else
      echo "$test" failed
    fi
  )
done
