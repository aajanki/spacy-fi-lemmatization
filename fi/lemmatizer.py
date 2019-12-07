# coding: utf8
from __future__ import unicode_literals

import json
import re
from collections import OrderedDict

from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups
from spacy.symbols import NOUN, VERB, ADJ, PUNCT, PROPN, ADV, NUM

_enclitics = [
    'ko', 'kö', 'han', 'hän', 'pa', 'pä', 'kaan', 'kään', 'kin',
    # Most common merged enclitics:
    'kohan', 'köhän', 'pahan', 'pähän', 'kaankohan', 'käänköhän'
    # TODO: Enclitics with restricted uses: -kA on the negative verb,
    # -s on interrogatives
]
_enclitics_re = re.compile('(?:' + '|'.join(_enclitics) + ')$')

gradations = {
    "av1": {
        "mm": "mp",
        "nn": "nt",
        "ll": "lt",
        "rr": "rt",
        "ng": "nk",
        "t": "tt",
        "p": "pp",
        "k": "kk",
        "v": "p",
        "d": "t",
        "uvu": "uku",
        "yvy": "yky",
    },
    "av2": {
        "tt": "t",
        "pp": "p",
        "kk": "k",
        "mp": "mm",
        "nt": "nn",
        "lt": "ll",
        "rt": "rr",
        "nk": "ng",
        "p": "v",
        "t": "d",
    },
    "av3": {
        "j": "k",
    },
    "av4": {
        "k": "j"
    },
    "av5": {
        "": "k",
    },
    "av6": {
        "k": "",
    }
}

gradation_patterns = [
    ("av1", re.compile(r"^(.+?)(uvu|yvy)()$")),
    ("av1", re.compile(r"^(.+?)(mm|nn|ll|rr|ng|t|p|k|v|d)([aeiouyäö][bcdfghjklmnpqrstvwxz]?)$")),
    ("av2", re.compile(r"^(.+?)(tt|pp|kk|mp|nt|lt|rt|nk|p|t)([aeiouyäö][bcdfghjklmnpqrstvwxz]?)$"),),
    ("av3", re.compile(r"^(.+?)(j)([aeiouyäö])$")),
    ("av4", re.compile(r"^(.+?)(k)([aeiouyäö])$")),
    ("av5", re.compile(r"^(.+?[aeiouyäö][aeiouyäö])()([aeiouyäö])$")),
    ("av6", re.compile(r"^(.+?[aeiouyäö][aeiouyäö])(k)([aeiouyäö])$"))
]

def reverse_gradation_noun(word):
    forms = []
    for gname, gpat in gradation_patterns:
        m = gpat.match(word)
        if m:
            prefix = m.group(1)
            infix = gradations[gname][m.group(2)]
            suffix = m.group(3)

            if (not (prefix and infix and (prefix[-1] == infix[0])) and
                not (infix and suffix and (infix[-1] == suffix[0]))):
                forms.append(prefix + infix + suffix)

    if forms:
        return forms
    else:
        return [word]

gradation_reversal = {
    "noun": reverse_gradation_noun
}


class FinnishLemmatizer(Lemmatizer):
    def __call__(self, string, univ_pos, morphology=None):
        """Lemmatize a string.

        string (unicode): The string to lemmatize, e.g. the token text.
        univ_pos (unicode / int): The token's universal part-of-speech tag.
        morphology (dict): The token's morphological features following the
            Universal Dependencies scheme.
        RETURNS (list): The available lemmas for the string.
        """
        if univ_pos in (NOUN, "NOUN", "noun"):
            univ_pos = "noun"
            rules_class = univ_pos
        elif univ_pos in (VERB, "VERB", "verb"):
            univ_pos = "verb"
            rules_class = univ_pos
        elif univ_pos in (ADJ, "ADJ", "adj"):
            univ_pos = "adj"
            rules_class = univ_pos
        elif univ_pos in (ADV, "ADV", "adv"):
            univ_pos = "adv"
            rules_class = univ_pos
        elif univ_pos in (NUM, "NUM", "num"):
            univ_pos = "num"
            rules_class = univ_pos
        elif univ_pos in (PUNCT, "PUNCT", "punct"):
            univ_pos = "punct"
            rules_class = univ_pos
        elif univ_pos in (PROPN, "PROPN", "propn"):
            univ_pos = "propn"
            rules_class = "noun"
        else:
            return [string.lower()]

        index_table = self.lookups.get_table("lemma_index", {})
        exc_table = self.lookups.get_table("lemma_exc", {})
        rules_table = self.lookups.get_table("lemma_rules", {})
        valid_lemma = self._valid_noun_lemma if univ_pos == "noun" else self._valid_index_lemma
        lemmas = self.lemmatize(
            string,
            index_table.get(univ_pos, {}),
            exc_table.get(univ_pos, {}),
            rules_table.get(rules_class, []),
            gradation_reversal.get(rules_class, lambda x: []),
            valid_lemma,
        )
        return lemmas

    def lemmatize(self, string, index, exceptions, rules, reverse_gradation, valid_lemma):
        parts = string.rsplit("-", 1)
        lemmas = self._lemmatize_one_word(parts[-1], index, exceptions, rules, reverse_gradation, valid_lemma)

        if len(parts) == 1:
            return lemmas
        else:
            return ["{}-{}".format(parts[0], x) for x in lemmas]

    def _lemmatize_one_word(self, string, index, exceptions, rules, reverse_gradation, valid_lemma):
        orig = string
        string = string.lower()

        oov_forms = []
        enclitic_forms = self._remove_enclitics(string)
        for s in enclitic_forms:
            if valid_lemma(s, index):
                return [s]
            else:
                oov_forms.append(s)

        forms = []
        for s in enclitic_forms:
            for old, new in rules:
                if s.endswith(old):
                    rule_result = s[: len(s) - len(old)] + new
                    for form in reverse_gradation(rule_result) + [rule_result]:
                        if valid_lemma(form, index):
                            forms.append(form)

                    if new == '':
                        for exc in exceptions.get(rule_result, []):
                            forms.insert(0, exc)
        # Remove duplicates but preserve the ordering of applied "rules"
        forms = list(OrderedDict.fromkeys(forms))
        # Put exceptions at the front of the list, so they get priority.
        # This is a dodgy heuristic -- but it's the best we can do until we get
        # frequencies on this. We can at least prune out problematic exceptions,
        # if they shadow more frequent analyses.
        for form in enclitic_forms:
            for exc in exceptions.get(form, []):
                if exc not in forms:
                    forms.insert(0, exc)
        if not forms:
            forms.extend(oov_forms)
        if not forms:
            forms.append(orig)
        return forms

    def _remove_enclitics(self, string):
        form = _enclitics_re.sub('', string)
        if form and form != string:
            return [form, string]
        else:
            return [string]

    def _valid_index_lemma(self, string, index):
        return string and (string in index or not string.isalpha())

    def _valid_noun_lemma(self, string, index):
        # Either lemma in index or a -minen infinitive
        return string and (string in index or
                           string.endswith('minen') or
                           not string.isalpha())


def create_lemmatizer():
    lookups = Lookups()
    with open('lookups/fi_lemma_rules.json') as f:
        lookups.add_table('lemma_rules', json.load(f))
    with open('lookups/fi_lemma_index.json') as f2:
        lookups.add_table('lemma_index', json.load(f2))
    with open('lookups/fi_lemma_exc.json') as f3:
        lookups.add_table('lemma_exc', json.load(f3))
    return FinnishLemmatizer(lookups)
