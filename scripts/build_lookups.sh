#!/bin/sh

set -eu

mkdir -p lookups
zcat data/joukahainen.xml.gz | \
    python scripts/lemmaindex_joukahainen.py > \
    lookups/fi_lemma_index1.json
zcat data/finnish_vocab.txt.gz | \
    head -n 4000000 | \
    python scripts/lemmaindex_finnish_vocab.py > \
    lookups/fi_lemma_index2.json
python scripts/merge_lemma_indexes.py lookups/fi_lemma_index1.json lookups/fi_lemma_index2.json \
       > lookups/fi_lemma_index.json
rm lookups/fi_lemma_index1.json lookups/fi_lemma_index2.json

python scripts/lemmarules.py data/corevoikko/data/subst.aff data/corevoikko/data/verb.aff lookups/fi_lemma_rules.json
