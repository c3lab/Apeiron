#!/bin/bash
# docker run --rm -it -p 1313:1313  -v $(pwd):/src klakegg/hugo:0.101.0-ext-alpine server --verbose
docker run --rm -it --net host  -v $(pwd):/src -w /src betterweb/hugo:extended-0.121.1-20-1 -c "hugo server --verbose -D"
