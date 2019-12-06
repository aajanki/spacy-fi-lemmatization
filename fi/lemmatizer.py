# coding: utf8
from __future__ import unicode_literals

import json
import re
from collections import OrderedDict

from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups
from spacy.symbols import NOUN, VERB, ADJ, PUNCT, PROPN, ADV, NUM


# http://scripta.kotus.fi/visk/sisallys.php?p=126
_enclitics = [
    'ko', 'kö', 'han', 'hän', 'pa', 'pä', 'kaan', 'kään', 'kin',
    # Most common merged enclitics:
    'kohan', 'köhän', 'pahan', 'pähän', 'kaankohan', 'käänköhän'
    # TODO: Enclitics with restricted uses: -kA on the negative verb,
    # -s on interrogatives
]
_enclitics_re = re.compile('(?:' + '|'.join(_enclitics) + ')$')

# http://scripta.kotus.fi/visk/sisallys.php?p=95
# TODO: move to lookups
possessive_suffix_rules = {
    "noun": [
        ["ni", ""],
        ["ni", "n"],
        ["kseni", "ksi"],
        ["si", ""],
        ["si", "n"],
        ["ksesi", "ksi"],
        ["mme", ""],
        ["mme", "n"],
        ["ksemme", "ksi"],
        ["nne", ""],
        ["nne", "n"],
        ["ksenne", "ksi"],
        ["nsa", ""],
        ["nsa", "n"],
        ["ksensa", "ksi"],
        ["nsä", ""],
        ["nsä", "n"],
        ["ksensä", "ksi"],
        ["an", ""],
        ["en", ""],
        ["in", ""],
        ["on", ""],
        ["un", ""],
        ["yn", ""],
        ["än", ""],
        ["ön", ""],
    ]
}

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
            forms.append(m.group(1) + gradations[gname][m.group(2)] + m.group(3))

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
        elif univ_pos in (VERB, "VERB", "verb"):
            univ_pos = "verb"
        elif univ_pos in (ADJ, "ADJ", "adj"):
            univ_pos = "adj"
        elif univ_pos in (ADV, "ADV", "adv"):
            univ_pos = "adv"
        elif univ_pos in (NUM, "NUM", "num"):
            univ_pos = "num"
        elif univ_pos in (PUNCT, "PUNCT", "punct"):
            univ_pos = "punct"
        elif univ_pos in (PROPN, "PROPN"):
            return [string]
        else:
            return [string.lower()]

        index_table = self.lookups.get_table("lemma_index", {})
        exc_table = self.lookups.get_table("lemma_exc", {})
        rules_table = self.lookups.get_table("lemma_rules", {})
        lemmas = self.lemmatize(
            string,
            index_table.get(univ_pos, {}),
            exc_table.get(univ_pos, {}),
            rules_table.get(univ_pos, []),
            possessive_suffix_rules.get(univ_pos, []),
            gradation_reversal.get(univ_pos, lambda x: []),
        )
        return lemmas

    def lemmatize(self, string, index, exceptions, rules, possessive_suffix_rules, reverse_gradation):
        orig = string
        string = string.lower()

        if string in index:
            return [string]
        
        forms = []
        oov_forms = []
        string = _enclitics_re.sub('', string)
        if len(string) > 2 and string in index:
            return [string]
        else:
            oov_forms.append(string)

        reduced_forms = [string]
        for old, new in possessive_suffix_rules:
            if string.endswith(old):
                form = string[: len(string) - len(old)] + new
                if not form:
                    pass
                elif form in index or not form.isalpha():
                    return [form]
                else:
                    reduced_forms.append(form)

        for s in reduced_forms:
            for old, new in rules:
                if s.endswith(old):
                    rule_result = s[: len(s) - len(old)] + new
                    for form in reverse_gradation(rule_result) + [rule_result]:
                        if form and (form in index or not form.isalpha()):
                            forms.append(form)
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
    with open('lookups/fi_lemma_exc.json') as f3:
        lookups.add_table('lemma_exc', json.load(f3))
    return FinnishLemmatizer(lookups)
