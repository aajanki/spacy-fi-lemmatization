import copy
import json
import re
import voikkoinfl
import voikkoutils
import plac
from collections import OrderedDict
from itertools import takewhile
from pathlib import Path


@plac.annotations(
    noun_affix_file=('Path to the noun affix file', 'positional'),
    verb_affix_file=('Path to the verb affix file', 'positional'),
    destdir=('Output directory', 'positional', None, Path),
)
def main(noun_affix_file, verb_affix_file, destdir):
    inflection_rules = OrderedDict([
        ('noun', rules_from_affix_file(noun_affix_file)),
        ('verb', verb_rules(verb_affix_file)),
    ])

    # rules = combine_rules(
    #     combine_rules(enclitics_rules(), possessive_suffix_rules()),
    #     inflection_rules
    # )
    rules = combine_rules(possessive_suffix_rules(), inflection_rules, vowel_match=True)

    for pos, rs in rules.items():
        print(f'{len(rs)} {pos} rules')

    with open(destdir / 'fi_lemma_rules.json', 'w', encoding='utf-8') as fp:
        json.dump(rules, fp=fp, indent=2, ensure_ascii=False)

    # For debugging, won't be included in the final model
    with open(destdir / 'inflection_rules.json', 'w', encoding='utf-8') as fp:
        json.dump(inflection_rules, fp=fp, indent=2, ensure_ascii=False)


def rules_from_affix_file(affix_file):
    rulelist = []
    for t in voikkoinfl.readInflectionTypes(affix_file):
        # irregular words will be handled in the exceptions
        if t.matchWord not in ['poika', 'mies', '[vm]eri', 'tuntea', 'lähteä']:
            for rule in t.inflectionRules:
                for old, new in expand(t, rule.delSuffix, rule.addSuffix, rule.gradation):
                    rulelist.append((old, new))

    rulelist = list(OrderedDict.fromkeys(rulelist))
    return rulelist


def verb_rules(affix_file):
    rulelist = []
    for t in voikkoinfl.readInflectionTypes(affix_file):
        # irregular words will be handled in the exceptions
        if t.matchWord not in ['tuntea', 'lähteä']:
            for rule in t.inflectionRules:
                # person inflections
                if rule.name == 'infinitiivi_1':
                    continue

                if rule.name == 'preesens_yks_1':
                    suffix = rule.addSuffix

                    assert suffix.endswith('n')

                    third_person = []
                    if len(suffix) >= 2 and is_vowel(suffix[-2]):
                        third_person = [suffix[:-1] + suffix[-2]]
                    elif len(t.rmsfx) == 0:
                        x = t.matchWord[-1]
                        if x in 'aeiouA':
                            third_person = [x.lower()]
                        else:
                            print(f'FIXME: {t.joukahainenClasses[0]} third person')
                    elif len(t.matchWord) > len(t.rmsfx):
                        x = t.matchWord[:-len(t.rmsfx)][-1]
                        if x in 'aeiouA':
                            third_person = [x.lower()]
                        elif x == 'V':
                            third_person = ['e', 'i', 'o', 'u']
                        else:
                            print(f'FIXME: {t.joukahainenClasses[0]} third person')
                    else:
                        print(f'FIXME: {t.joukahainenClasses[0]} third person')

                    add_suffixes = [
                        suffix, suffix[:-1] + 't',
                        suffix[:-1] + 'mme', suffix[:-1] + 'tte', suffix[:-1] + 'vat'
                    ] + third_person
                elif rule.name in ['imperfekti_yks_3', 'kondit_yks_3']:
                    suffix = rule.addSuffix
                    add_suffixes = [
                        suffix + 'n', suffix + 't', suffix,
                        suffix + 'mme', suffix + 'tte', suffix + 'vat'
                    ]
                else:
                    add_suffixes = [rule.addSuffix]

                for add_suffix in add_suffixes:
                    for old, new in expand(t, rule.delSuffix, add_suffix, rule.gradation):
                        rulelist.append((old, new))

    rulelist = list(OrderedDict.fromkeys(rulelist))
    return rulelist


def expand(inflection_type, del_suffix, add_suffix, gradation):
    match_letters_m = re.search('[a-zäö]+$', inflection_type.matchWord)
    match_letters = match_letters_m.group() if match_letters_m else ''

    if match_letters:
        assert inflection_type.rmsfx == '', 'TODO: rmsfx + matchWord'

        if del_suffix == '':
            common = match_letters
        else:
            # special case: gradation in the suffix
            if match_letters == 'mpi' and gradation == voikkoutils.GRAD_WEAK:
                match_letters = 'mmi'

            i = sum(1 for _ in takewhile(
                lambda x: x[0] == x[1],
                zip(
                    reversed(match_letters),
                    reversed(del_suffix)
                )
            ))
            common = match_letters[:-i]

        del_suffix = common + del_suffix
        add_suffix = common + add_suffix

    for remove, add, _ in voikkoinfl.__regex_to_hunspell(del_suffix, add_suffix):
        if remove == '0':
            remove = ''
        if add == '0':
            add = ''
        remove = remove.strip("'")
        remove = remove + inflection_type.rmsfx
        add = add.strip("'")

        if remove or add:
            for remove_literal in expand_pattern(remove):
                if add != remove_literal:
                    yield (add, remove_literal)


def vowel_harmony(word1, word2):
    harmony1 = vowel_harmony_type(word1)
    harmony2 = vowel_harmony_type(word2)
    return not ((harmony1 == 'back' and harmony2 == 'front') or
                (harmony1 == 'front' and harmony2 == 'back'))


def vowel_harmony_type(word):
    back = 'aou'
    front = 'äöy'

    last_back = max(word.rfind(x) for x in back)
    last_front = max(word.rfind(x) for x in front)

    if last_back > last_front:
        return 'back'
    elif last_back < last_front:
        return 'front'
    else:
        return 'indefinite'


def expand_pattern(pattern):
    expand_capital = {
        'C': 'bcdfghjklmnpqrstvwxzšž',
        'V': 'aeiouyäöéèáóâ',
        'A': 'aä',
        'O': 'oö',
        'U': 'uy',
    }

    capitals = '[' + ''.join(expand_capital.keys()) + ']'
    matches = list(re.finditer(capitals, pattern))
    assert len(matches) <= 1, 'TODO: multiple capitals'

    if matches:
        letter = matches[0].group(0)
        return [
            pattern.replace(letter, repl) for repl in expand_capital[letter]
        ]
    else:
        return [pattern]


def combine_rules(rules1, rules2, vowel_match=False):
    """Build a combined ruleset

    Either rules1 are applied alone, rules2 are applied alone or
    rules1 is applied followed by rules2.

    If vowel_match is True, combine rules only if both have the same
    vowel at the seam or one has a consonant.
    """

    keys = sorted(set(rules1.keys()) | set(rules2.keys()))
    combined = {}
    for pos in keys:
        r1 = rules1.get(pos, [])
        r2 = rules2.get(pos, [])

        if not r1:
            combined[pos] = copy.copy(r2)
        else:
            rulelist = copy.copy(r1) + copy.copy(r2)
            for old1, new1 in r1:
                for old2, new2 in r2:
                    if vowel_harmony(old1, old2):
                        if new1 == '':
                            if not vowel_match or vowel_compatible(old2, old1):
                                if old1 and old2 and old2[-1] == 'n' and old1[0] == 'm':
                                    old2 = old2[:-1]

                                rulelist.append((old2 + old1, new2))
                        elif old2.endswith(new1):
                            a = old2[:-len(new1)]
                            b = old1

                            if not vowel_match or vowel_compatible(a, b):
                                if a and b and a[-1] == 'n' and b[0] == 'm':
                                    a = a[:-1]

                                rulelist.append((a + b, new2))

            combined[pos] = list(OrderedDict.fromkeys(rulelist))

    return combined


def vowel_compatible(a, b):
    if not a or not b:
        return True
    else:
        return ((is_vowel(a[-1]) and (a[-1] == b[0])) or
                not is_vowel(a[-1]) or
                not is_vowel(b[0]))


def is_vowel(x):
    return x in 'aeiouyäöåéèáóâ'


def enclitics_rules():
    # http://scripta.kotus.fi/visk/sisallys.php?p=126

    common_enclitics = [
        ('ko', ''),
        ('kö', ''),
        ('han', ''),
        ('hän', ''),
        ('pa', ''),
        ('pä', ''),
        ('kaan', ''),
        ('kään', ''),
        ('kin', ''),

        # The most common merged enclitics:
        ('kohan', ''),
        ('köhän', ''),
        ('pahan', ''),
        ('pähän', ''),
        ('kaankohan', ''),
        ('käänköhän', ''),
    ]

    # TODO: Enclitics with restricted uses: -kA on the negative verb,
    # -s on interrogatives
    return {
        'adj': common_enclitics,
        'adv': common_enclitics,
        'noun': common_enclitics,
        'num': common_enclitics,
        'propn': common_enclitics,
        'verb': common_enclitics,
    }


def possessive_suffix_rules():
    # http://scripta.kotus.fi/visk/sisallys.php?p=95

    return {
        'noun': [
            ('ni', ''),
            ('ni', 'n'),
            ('kseni', 'ksi'),
            ('si', ''),
            ('si', 'n'),
            ('ksesi', 'ksi'),
            ('mme', ''),
            ('mme', 'n'),
            ('ksemme', 'ksi'),
            ('nne', ''),
            ('nne', 'n'),
            ('ksenne', 'ksi'),
            ('nsa', ''),
            ('nsa', 'n'),
            ('ksensa', 'ksi'),
            ('an', ''),
            ('en', ''),
            ('in', ''),
            ('on', ''),
            ('un', ''),
            ('yn', ''),
        ]
    }


if __name__ == '__main__':
    plac.call(main)
