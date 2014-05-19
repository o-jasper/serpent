#!/bin/bash
# Just here because `make` has its own ideas or something.

for el in *.lsp; do
    make $1/$1_$(echo $el | head -c-5).png
done

echo > /dev/null # Otherwise it may say it failed.
