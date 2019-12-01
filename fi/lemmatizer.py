# coding: utf8
from __future__ import unicode_literals

import json
import re
from collections import OrderedDict

from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups


_enclitics = [
    'ko', 'kö', 'han', 'hän', 'pa', 'pä', 'kaan', 'kään', 'kin'
]
_enclitics_re = re.compile('|'.join(x + '$' for x in _enclitics))


class FinnishLemmatizer(Lemmatizer):
    def lemmatize(self, string, index, exceptions, rules):
        orig = string
        string = string.lower()

        forms = []
        oov_forms = []
        string = _enclitics_re.sub('', string)
        if string in index:
            forms.append(string)

        for old, new in rules:
            if string.endswith(old):
                form = string[: len(string) - len(old)] + new
                if not form:
                    pass
                elif form in index or not form.isalpha():
                    forms.append(form)
                else:
                    oov_forms.append(form)
        # Remove duplicates but preserve the ordering of applied "rules"
        forms = list(OrderedDict.fromkeys(forms))
        # Put exceptions at the front of the list, so they get priority.
        # This is a dodgy heuristic -- but it's the best we can do until we get
        # frequencies on this. We can at least prune out problematic exceptions,
        # if they shadow more frequent analyses.
        for form in exceptions.get(string, []):
            if form not in forms:
                forms.insert(0, form)
        if not forms:
            forms.extend(oov_forms)
        if not forms:
            forms.append(orig)
        return forms


def create_lemmatizer():
    lookups = Lookups()
    with open('lookups/fi_lemma_rules.json') as f:
        lookups.add_table('lemma_rules', json.load(f))
    with open('lookups/fi_lemma_index.json') as f2:
        lookups.add_table('lemma_index', json.load(f2))
    return FinnishLemmatizer(lookups)
