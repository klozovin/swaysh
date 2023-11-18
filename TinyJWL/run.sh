#!/bin/sh

java                                    \
    --enable-native-access=ALL-UNNAMED  \
    -Dforeign.restricted=permit         \
    --add-modules jdk.incubator.foreign \
    src/main/java/tinyjwl/Tiny.java

