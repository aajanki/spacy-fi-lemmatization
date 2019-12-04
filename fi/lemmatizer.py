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
        ["si", ""],
        ["si", "n"],
        ["mme", ""],
        ["mme", "n"],
        ["nne", ""],
        ["nne", "n"],
        ["nsa", ""],
        ["nsa", "n"],
        ["nsä", ""],
        ["nsä", "n"],
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
        )
        return lemmas

    def lemmatize(self, string, index, exceptions, rules, possessive_suffix_rules):
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
                    form = s[: len(s) - len(old)] + new
                    if not form:
                        pass
                    elif form in index or not form.isalpha():
                        forms.append(form)
        # Remove duplicates but preserve the ordering of applied "rules"
        forms = list(OrderedDict.fromkeys(forms))
        # Put exceptions at the front of the list, so they get priority.
        # This is a dodgy heuristic -- but it's the best we can do until we get
        # frequencies on this. We can at least prune out problematic exceptions,
        # if they shadow more frequent analyses.
        for form in exceptions.get(orig.lower(), []):
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
