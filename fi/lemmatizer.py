# coding: utf8
from __future__ import unicode_literals

import json
import re
from collections import OrderedDict

from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups
from spacy.symbols import NOUN, VERB, ADJ, PUNCT, PROPN, ADV, NUM
from spacy.strings import get_string_id
from .trie import Trie


# http://scripta.kotus.fi/visk/sisallys.php?p=126
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
        "bb": "b",
        "gg": "g",
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

gradation_patterns_noun = {
    "w": [
        ("av1", re.compile(r"^(.+?)(uvu|yvy)()$")),
        ("av1", re.compile(r"^(.+?)(mm|nn|ll|rr|ng|t|p|k|v|d)([aeiouyäö][bcdfghjklmnpqrstvwxz]?)$")),
        ("av3", re.compile(r"^(.+?)(j)([aeiouyäö])$")),
        ("av5", re.compile(r"^(.+?[aeiouyäö][aeiouyäö])()([aeiouyäö])$")),
    ],
    "s": [
        ("av2", re.compile(r"^(.+?)(tt|pp|kk|mp|nt|lt|rt|nk|p|t)([aeiouyäö][bcdfghjklmnpqrstvwxz]?)$")),
        ("av4", re.compile(r"^(.+?)(k)([aeiouyäö])$")),
        ("av6", re.compile(r"^(.+?[aeiouyäö][aeiouyäö])(k)([aeiouyäö])$")),
    ]
}

gradation_patterns_verb = {
    "w": [
        ("av1", re.compile(r"^(.+?)(mm|nn|ll|rr|ng|t|p|k|v|d)(.+)$")),
        ("av3", re.compile(r"^(.+?)(j)([aeiouyäö].*)$")),
        ("av5", re.compile(r"^(.+?[aeiouyäö])()([aeiouyäö].*)$")),
    ],
    "s": [
        ("av2", re.compile(r"^(.+?)(tt|pp|kk|mp|nt|lt|rt|nk|bb|gg|p|t)(.+)$")),
        ("av4", re.compile(r"^(.+?)(k)([aeiouyäö].*)$")),
        ("av6", re.compile(r"^(.+?[aeiouyäö])(k)([aeiouyäö].*)$")),
    ]
}

def create_gradation_transformer(patterns):
    def f(word, pattern_key):
        forms = [word]
        for gname, gpat in patterns.get(pattern_key, []):
            m = gpat.match(word)
            if m:
                prefix = m.group(1)
                infix = gradations[gname][m.group(2)]
                suffix = m.group(3)

                if (not (prefix and infix and (prefix[-1] == infix[0])) and
                    not (infix and suffix and (infix[-1] == suffix[0]))):
                    form = prefix + infix + suffix
                    if form not in forms:
                        forms.append(form)
        return forms
    return f


gradation_reversal = {
    "noun": create_gradation_transformer(gradation_patterns_noun),
    "verb": create_gradation_transformer(gradation_patterns_verb),
}


class SuffixTransformation(object):
    def __init__(self, del_len, add, gradation):
        self.del_len = del_len
        self.add = add
        self.gradation_rule = gradation

    def __call__(self, word, reverse_gradation):
        if self.del_len >= len(word):
            form = self.add
        else:
            form = word[:len(word) - self.del_len] + self.add

        return reverse_gradation(form, self.gradation_rule)


class FinnishLemmatizer(Lemmatizer):
    def __init__(self, lookups, *args, **kwargs):
        super(FinnishLemmatizer, self).__init__(lookups, *args, **kwargs)
        rules_table = self.lookups.get_table("lemma_rules", {})
        self.rules_trie = self._build_trie(rules_table)

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
            rules_class = "noun"
        elif univ_pos in (ADV, "ADV", "adv"):
            univ_pos = "adv"
            rules_class = univ_pos
        elif univ_pos in (NUM, "NUM", "num"):
            univ_pos = "num"
            rules_class = "noun"
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
        valid_lemma = self._valid_noun_lemma if univ_pos == "noun" else self._valid_index_lemma
        lemmas = self.lemmatize(
            string,
            index_table.get(univ_pos, {}),
            exc_table.get(univ_pos, {}),
            self.rules_trie.get(get_string_id(rules_class), Trie()),
            gradation_reversal.get(rules_class, lambda x, y: []),
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
            harmony1 = self._vowel_harmony_type(s)
            for transformation in rules.find(reversed(s)):
                harmony2 = self._vowel_harmony_type(transformation.add)
                if self._incompatible_vowels(harmony1, harmony2):
                    continue

                for form in transformation(s, reverse_gradation):
                    if valid_lemma(form, index):
                        forms.append(form)

                    for exc in exceptions.get(form, []):
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

    def _vowel_harmony_type(self, string):
        last_front = max(string.rfind(x) for x in "äöy")
        last_back = max(string.rfind(x) for x in "aou")
        if last_front > last_back:
            return 'front'
        elif last_front < last_back:
            return 'back'
        else:
            return 'indefinite'

    def _incompatible_vowels(self, harmony_type1, harmony_type2):
        return ((harmony_type1 == 'front' and harmony_type2 == 'back') or
                (harmony_type1 == 'back' and harmony_type2 == 'front'))

    def _build_trie(self, rules_table):
        rules_trie = {}
        for pos, rules in rules_table.items():
            trie = Trie()
            for old, new, gradation in rules:
                transformation = SuffixTransformation(len(old), new, gradation)
                trie.insert(reversed(old), transformation)
            rules_trie[pos] = trie
        return rules_trie


def create_lemmatizer():
    lookups = Lookups()
    with open('lookups/fi_lemma_rules.json') as f:
        lookups.add_table('lemma_rules', json.load(f))
    with open('lookups/fi_lemma_index.json') as f2:
        lookups.add_table('lemma_index', json.load(f2))
    with open('lookups/fi_lemma_exc.json') as f3:
        lookups.add_table('lemma_exc', json.load(f3))
    return FinnishLemmatizer(lookups)
