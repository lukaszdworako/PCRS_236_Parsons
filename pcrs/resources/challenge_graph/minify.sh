#!/bin/bash
rm graph.min.js
for f in $(find ./js -name '*.js'); do uglifyjs $f >> graph.min.js; done;