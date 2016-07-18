#!/bin/sh

# Runs all the functional tests

EXIT_STATUS=0

for f in "test*.js"
do
    casperjs test --includes=helper.js $f || EXIT_STATUS=1
done

exit $EXIT_STATUS

