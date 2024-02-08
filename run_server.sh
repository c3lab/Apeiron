#!/bin/bash
docker run --rm -it -p 1313:1313  -v $(pwd):/src klakegg/hugo:0.101.0-ext-alpine server
