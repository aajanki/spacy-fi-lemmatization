#!/bin/sh

set -eu

mkdir -p lookups
zcat data/joukahainen.xml.gz | python scripts/lemmaindex.py > lookups/fi_lemma_index.json
