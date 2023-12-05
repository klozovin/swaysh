#!/bin/sh

/opt/jextract-21/bin/jextract               \
    --target-package tinywl.wlroots         \
    --library wlroots                       \
    --source                                \
    --output "src/main/java/"               \
    "/usr/include/wlr/version.h"

/opt/jextract-21/bin/jextract               \
    --target-package tinywl.wlroots.util    \
    --library wlroots                       \
    --source                                \
    --output "src/main/java/"               \
    "/usr/include/wlr/util/log.h"

# /opt/jextract-21/bin/jextract               \
#     --target-package tinywl.wlroots.util    \
#     --library wlroots                       \
#     --source                                \
#     --output "src/main/java/"               \
#     "/usr/include/wlr/util/box.h"
