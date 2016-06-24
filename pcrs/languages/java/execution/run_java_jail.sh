#!/bin/sh
# To test this, run `cat JavaJail/doc/testfiles/test-input.json | ./run_java_jail.sh`

cd JavaJail

: ${JAVA_HOME="./java"}
export JAVA_HOME

if [ ! -e ./build ]
then
    echo You must pull and configure the JavaJail git submodule.
    exit 1
fi

export CLASSPATH="./build/:./jar/javax.json-1.0.jar:$JAVA_HOME/lib/tools.jar"
# Forward STDIN directly into the jail
cat | $JAVA_HOME/bin/java traceprinter.InMemory

