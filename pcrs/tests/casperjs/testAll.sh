#!/bin/sh

# Runs all the functional tests
casperjs test --includes=helper.js test*.js
exit $!

