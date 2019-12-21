# coding: utf8
from __future__ import unicode_literals

import json
import re
from collections import OrderedDict
from itertools import chain

from spacy.lemmatizer import Lemmatizer
from spacy.lookups import Lookups
from spacy.symbols import NOUN, VERB, ADJ, PUNCT, PROPN, ADV, NUM
from voikko import libvoikko


class FinnishLemmatizer(Lemmatizer):
    compound_re = re.compile(r"\+(\w+)(?:\(\+?[\w=]+\))?")
    minen_re = re.compile(r"\b(\w+)\[Tn4\]mi")
    sti_re = re.compile(r"\b(\w+)\[Ssti\]sti")
    ny_re = re.compile(r"\[X\]\[\w+\]\[Ny\](\w+)")
    voikko_pos_to_upos = {
        "nimisana": "noun",
        "teonsana": "verb",
        "laatusana": "adj",
        "nimisana_laatusana": "adj",
        "seikkasana": "adv",
        "lukusana": "num",
        "nimi": "propn",
        "etunimi": "propn",
        "sukunimi": "propn",
        "paikannimi": "propn",
    }

    def __init__(self, lookups, *args, **kwargs):
        super(FinnishLemmatizer, self).__init__(lookups, *args, **kwargs)
        self.voikko = libvoikko.Voikko("fi")

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
        elif univ_pos in (PROPN, "PROPN", "propn"):
            univ_pos = "propn"
        elif univ_pos in (PUNCT, "PUNCT", "punct"):
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
            rules_table.get(univ_pos, {}),
            univ_pos,
        )
        return lemmas

    def lemmatize(self, string, index, exceptions, rules, univ_pos):
        orig = string
        oov_forms = []
        forms = []

        analyses = self.voikko.analyze(orig)
        base_and_pos = list(chain.from_iterable([self._baseform_and_pos(x) for x in analyses]))
        matching_pos = [x for x in base_and_pos if x[1] == univ_pos]
        if matching_pos:
            forms.extend(x[0] for x in matching_pos)
        elif analyses:
            oov_forms.extend(x[0] for x in base_and_pos)
        else:
            oov_forms.append(orig)

        forms = list(OrderedDict.fromkeys(forms))

        # Put exceptions at the front of the list, so they get priority.
        # This is a dodgy heuristic -- but it's the best we can do until we get
        # frequencies on this. We can at least prune out problematic exceptions,
        # if they shadow more frequent analyses.
        for exc in exceptions.get(orig, []):
            if exc not in forms:
                forms.insert(0, exc)
        if not forms:
            forms.extend(oov_forms)
        if not forms:
            forms.append(orig)
        return forms

    def _baseform_and_pos(self, analysis):
        baseform = analysis.get("BASEFORM")
        voikko_class = analysis.get("CLASS")

        if (voikko_class == "teonsana" and
            analysis.get("MOOD") == "MINEN-infinitive"
        ):
            # MINEN infinitive
            form = self._fst_form(analysis, self.minen_re, "minen")
            if form:
                return [(form, "noun")]
            else:
                return [(baseform, "verb")]
        elif (voikko_class == "laatusana" and
              analysis.get("PARTICIPLE") in ["past_active", "past_passive"] and
              analysis.get("SIJAMUOTO") == "nimento" and
              (baseform.endswith("nut") or
               baseform.endswith("nyt") or
               baseform.endswith("tu") or
               baseform.endswith("ty"))
        ):
            # NUT and TU participles
            return [
                (self._past_perfect_tense(analysis), "verb"),
                (baseform, "adj")
            ]
        elif (voikko_class in ["laatusana", "lukusana"] and
              analysis.get("SIJAMUOTO") == "kerrontosti"
        ):
            form = self._fst_form(analysis, self.sti_re, "sti")
            if form:
                return [(form, "adv")]
            else:
                return [(baseform, self.voikko_pos_to_upos[voikko_class])]
        elif voikko_class in self.voikko_pos_to_upos:
            return [(baseform, self.voikko_pos_to_upos[voikko_class])]
        else:
            return [(baseform, None)]

    def _fst_form(self, analysis, stem_re, suffix):
        fstoutput = analysis.get("FSTOUTPUT")
        ny_match = self.ny_re.search(fstoutput)
        if ny_match:
            return ny_match.group(1)

        fst_match = stem_re.search(fstoutput)
        if not fst_match:
            return None

        stem = fst_match.group(1)
        compounds = self.compound_re.findall(analysis.get("WORDBASES"))
        if len(compounds) > 1:
            return "".join(compounds[:-1]) + stem + suffix
        else:
            return stem + suffix

    def _past_perfect_tense(self, analysis):
        m = re.search(r"\((\w+)\)", analysis.get("WORDBASES"))
        if m:
            return m.group(1)
        else:
            return analysis.get("BASEFORM")


def create_lemmatizer():
    lookups = Lookups()
    return FinnishLemmatizer(lookups)
