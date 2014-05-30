#!/bin/bash

TEST_RESULTS=.test_results

mkdir -p $TEST_RESULTS

run()
{
    if which python2 > /dev/null; then
        python2 runtests.py
    else
        python runtests.py
    fi
}

get_commit()
{
    git log --skip "$1" -n 1 |head -n 1 |cut -f 2 -d' '
}

TO="$TEST_RESULTS/$(get_commit 0)"
if [ "$(git diff --stat)" != "" ]; then  # Annotate there there were changes.
    TO="$TO"_
fi

if [ ! -e "$TO" ]; then
    run > "$TO"
fi

if [ -e "$1" ]; then
    diff "$TO" "$1"
elif [ -e $TEST_RESULTS/compare_to ]; then
    diff "$TO" "$TEST_RESULTS/compare_to"
else
    I=2
    while true; do  # See if a previous run knows.
        WHICH=$TEST_RESULTS/"$(get_commit $I)"
        if [ -e "$WHICH" ]; then
            diff "$TO" "$WHICH"
            exit
        elif [ -e "$WHICH"_ ]; then
            diff "$TO" "$WHICH"_
            exit
        fi
        I=$(expr $I + 1)
    done
fi
