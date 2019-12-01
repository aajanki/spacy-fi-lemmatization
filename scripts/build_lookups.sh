#!/bin/sh

set -eu

mkdir -p lookups
zcat data/joukahainen.xml.gz | python scripts/lemmaindex.py > lookups/fi_lemma_index.json

python scripts/lemmarules.py data/corevoikko/data/subst.aff data/corevoikko/data/verb.aff lookups/fi_lemma_rules.json
