#!/bin/sh

jextract                                    \
    -t tinyjwl.wlroots.util                 \
    -l wlroots                              \
    --source                                \
    -d "src/main/java/"                     \
    "/usr/include/wlr/util/log.h"