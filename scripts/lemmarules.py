import copy
import json
import re
import voikkoinfl
import voikkoutils
import plac
from collections import OrderedDict
from itertools import takewhile
from pathlib import Path


GRAD_NONE = 0
GRAD_SW = 1
GRAD_WS = 2
GRAD_WEAK = 3
GRAD_STRONG = 4

@plac.annotations(
    noun_affix_file=('Path to the noun affix file', 'positional'),
    verb_affix_file=('Path to the verb affix file', 'positional'),
    destdir=('Output directory', 'positional', None, Path),
)
def main(noun_affix_file, verb_affix_file, destdir):
    inflection_rules = OrderedDict([
        ('noun', subst_rules(noun_affix_file)),
        ('verb', verb_rules(verb_affix_file)),
    ])

    # rules = combine_rules(
    #     combine_rules(enclitics_rules(), possessive_suffix_rules()),
    #     inflection_rules
    # )
    rules = combine_rules(possessive_suffix_rules(), inflection_rules, vowel_match=True)
    rules = extend_front_vowel_rules(rules)

    for pos, rs in rules.items():
        print(f'{len(rs)} {pos} rules')

    with open(destdir / 'fi_lemma_rules.json', 'w', encoding='utf-8') as fp:
        json.dump(rules, fp=fp, indent=2, ensure_ascii=False)

    # For debugging, won't be included in the final model
    with open(destdir / 'inflection_rules.json', 'w', encoding='utf-8') as fp:
        json.dump(inflection_rules, fp=fp, indent=2, ensure_ascii=False)


def choose_gradation(inflection_type, rule):
    if inflection_type.gradation == GRAD_SW and rule.gradation == GRAD_WEAK:
        return 'w' # unapply av1, av3, av5
    elif inflection_type.gradation == GRAD_WS and rule.gradation == GRAD_STRONG:
        return 's' # unapply av2, av4, av6
    else:
        return '-'


def subst_rules(affix_file):
    rulelist = []
    for t in voikkoinfl.readInflectionTypes(affix_file):
        # irregular words will be handled in the exceptions
        if t.matchWord not in ['poika', 'mies', '[vm]eri']:
            for rule in t.inflectionRules:
                for old, new in expand(t, rule.delSuffix, rule.addSuffix, rule.gradation):
                    g = choose_gradation(t, rule)
                    rulelist.append((old, new, g))

    # FIXME: The following should be applied only to adjectives
    # comparative
    rulelist.append(('mpi', '', 's'))
    rulelist.append(('ampi', 's', 's'))
    rulelist.append(('ampi', 'n', 's'))
    rulelist.append(('mampi', 'n', 's'))
    rulelist.append(('sempi', 'nen', 's'))
    rulelist.append(('dempi', 'si', 's'))
    # superlative
    rulelist.append(('in', 'a', '-'))
    rulelist.append(('in', 't', '-'))
    rulelist.append(('ein', 'a', '-'))
    rulelist.append(('ein', 'is', '-'))
    rulelist.append(('min', 'n', '-'))

    return list(OrderedDict.fromkeys(rulelist))


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
                    # present tense
                    suffix = rule.addSuffix

                    assert suffix.endswith('n')

                    third_singular = []
                    if len(suffix) >= 2 and is_vowel(suffix[-2]):
                        third_singular = [suffix[:-1] + suffix[-2]]
                    elif len(t.rmsfx) == 0:
                        x = t.matchWord[-1]
                        if x in 'aeiouA':
                            third_singular = [x.lower()]
                        else:
                            print(f'FIXME: {t.joukahainenClasses[0]} third person')
                    elif len(t.matchWord) > len(t.rmsfx):
                        x = t.matchWord[:-len(t.rmsfx)][-1]
                        if x in 'aeiouA':
                            third_singular = [x.lower()]
                        elif x == 'V':
                            third_singular = ['e', 'i', 'o', 'u']
                        else:
                            print(f'FIXME: {t.joukahainenClasses[0]} third person')
                    else:
                        print(f'FIXME: {t.joukahainenClasses[0]} third person')

                    add_suffixes = [
                        # singular (1st and 2nd person)
                        suffix, suffix[:-1] + 't',
                        # plural
                        suffix[:-1] + 'mme', suffix[:-1] + 'tte', suffix[:-1] + 'vat',
                        # imperative second person singular
                        suffix[:-1],
                    ] + third_singular

                elif rule.name in ['imperfekti_yks_3', 'kondit_yks_3']:
                    # past test and conditional
                    suffix = rule.addSuffix
                    add_suffixes = [
                        suffix + 'n', suffix + 't', suffix,
                        suffix + 'mme', suffix + 'tte', suffix + 'vat'
                    ]

                elif rule.name == 'imperfekti_pass':
                    # passive
                    suffix = rule.addSuffix
                    assert suffix.endswith('iin')

                    add_suffixes = [
                        suffix[:-3] + 'aan', # present
                        suffix, # past
                        suffix[:-3] + 'u', # negation
                    ]

                elif rule.name == 'imperatiivi_yks_3':
                    # imperative
                    # (the 2nd person singular is handled at the
                    # preesens_yks_1 branch)
                    suffix = rule.addSuffix
                    assert suffix.endswith('koon')

                    add_suffixes = [
                        suffix, # 3rd person singular
                        suffix[:-3] + 'aamme', # 1st person plural
                        suffix[:-3] + 'aa', # 2nd person plural
                        suffix[:-1] + 't', # 3rd person plural
                        suffix[:-2], # negative plural
                    ]

                else:
                    add_suffixes = [rule.addSuffix]

                for add_suffix in add_suffixes:
                    for old, new in expand(t, rule.delSuffix, add_suffix, rule.gradation):
                        g = choose_gradation(t, rule)
                        rulelist.append((old, new, g))

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
        remove = remove.replace('ä', 'a').replace('ö', 'o')
        add = add.strip("'")

        if remove or add:
            for remove_literal in expand_pattern(remove):
                if add != remove_literal:
                    yield (add, remove_literal)


def front_vowel_rules(rules):
    new_rules = []
    for old, new, g in rules:
        if has_back_vowels(old) or has_back_vowels(new):
            old_front = back_to_front_vowels(old)
            new_front = back_to_front_vowels(new)
            new_rules.append((old_front, new_front, g))
    return new_rules


def extend_front_vowel_rules(rules_dict):
    res = {}
    for pos, rules in rules_dict.items():
        res[pos] = rules + front_vowel_rules(rules)
    return res


def vowel_harmony(word1, word2):
    harmony1 = vowel_harmony_type(word1)
    harmony2 = vowel_harmony_type(word2)
    return not ((harmony1 == 'back' and harmony2 == 'front') or
                (harmony1 == 'front' and harmony2 == 'back'))


def vowel_harmony_type(word):
    last_back = max(word.rfind(x) for x in 'aou')
    last_front = max(word.rfind(x) for x in 'äöy')

    if last_back > last_front:
        return 'back'
    elif last_back < last_front:
        return 'front'
    else:
        return 'indefinite'


def has_back_vowels(word):
    return any(x in word for x in 'aou')


def back_to_front_vowels(string):
    return string.replace('a', 'ä').replace('o', 'ö').replace('u', 'y')


def expand_pattern(pattern):
    expand_capital = {
        'C': 'bcdfghjklmnpqrstvwxzšž',
        'V': 'aeiou',
        'A': 'a',
        'O': 'o',
        'U': 'u',
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

        rulelist = copy.copy(r1) + copy.copy(r2)
        for old1, new1, grad1 in r1:
            for old2, new2, grad2 in r2:
                assert not (grad1 != '-' and grad2 != '-' and grad1 != grad2)

                if vowel_harmony(old1, old2):
                    if new1 == '':
                        a, b = make_compatible(old2, old1, vowel_match)
                        if a is not None and b is not None:
                            rulelist.append((a + b, new2, grad2))
                    elif old2.endswith(new1):
                        a, b = make_compatible(old2[:-len(new1)], old1, vowel_match)
                        if a is not None and b is not None:
                            rulelist.append((a + b, new2, grad2))

        combined[pos] = list(OrderedDict.fromkeys(rulelist))

    return combined


def make_compatible(a, b, vowel_match):
    if vowel_match and not vowel_compatible(a, b):
        return (None, None)
    elif a and b and a[-1] == 'n' and b[0] in 'mn':
        return (a[:-1], b)
    else:
        return (a, b)


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
            ('ni', '', '-'),
            ('kseni', 'ksi', '-'),
            ('si', '', '-'),
            ('ksesi', 'ksi', '-'),
            ('mme', '', '-'),
            ('ksemme', 'ksi', '-'),
            ('nne', '', '-'),
            ('ksenne', 'ksi', '-'),
            ('nsa', '', '-'),
            ('ksensa', 'ksi', '-'),
            ('aan', 'a', '-'),
            ('een', 'e', '-'),
            ('iin', 'i', '-'),
            ('oon', 'o', '-'),
            ('uun', 'u', '-'),
        ]
    }


if __name__ == '__main__':
    plac.call(main)
