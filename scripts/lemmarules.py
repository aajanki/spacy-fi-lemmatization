import json
import re
import voikkoinfl
import voikkoutils
import plac
from collections import OrderedDict
from itertools import takewhile


@plac.annotations(
    noun_affix_file=('Path to the noun affix file', 'positional'),
    verb_affix_file=('Path to the verb affix file', 'positional'),
    output=('Output file path', 'positional'),
)
def main(noun_affix_file, verb_affix_file, output):
    rules = OrderedDict([
        ('noun', rules_from_affix_file(noun_affix_file)),
        ('verb', rules_from_affix_file(verb_affix_file)),
    ])

    for pos, rs in rules.items():
        print(f'{len(rs)} {pos} rules')

    with open(output, 'w', encoding='utf-8') as fp:
        json.dump(rules, fp=fp, indent=2, ensure_ascii=False)


def rules_from_affix_file(affix_file):
    rulelist = []
    for t in voikkoinfl.readInflectionTypes(affix_file):
        # irregular words handled as exceptions
        if t.matchWord not in ['poika', 'mies', '[vm]eri', 'tuntea', 'lähteä']:
            for rule in t.inflectionRules:
                for old, new in expand(t, rule):
                    rulelist.append((old, new))

    rulelist = list(OrderedDict.fromkeys(rulelist))
    return rulelist


def expand(inflection_type, rule):
    match_letters_m = re.search('[a-zäö]+$', inflection_type.matchWord)
    match_letters = match_letters_m.group() if match_letters_m else ''

    del_suffix = rule.delSuffix
    add_suffix = rule.addSuffix
    if match_letters:
        assert inflection_type.rmsfx == '', 'TODO: rmsfx + matchWord'

        if del_suffix == '':
            common = match_letters
        else:
            # special case: gradation in the suffix
            if match_letters == 'mpi' and rule.gradation == voikkoutils.GRAD_WEAK:
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
        remove = inflection_type.rmsfx + remove
        add = add.strip("'")

        if remove or add:
            for remove_literal in expand_pattern(remove):
                if add != remove_literal:
                    yield (add, remove_literal)

                remove_front_vow = voikkoinfl.__convert_tv_ev(remove_literal)
                add_front_vow = voikkoinfl.__convert_tv_ev(add)
                if ((remove_literal != remove_front_vow or add != add_front_vow) and
                    (add_front_vow != remove_front_vow)
                ):
                    yield (add_front_vow, remove_front_vow)


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


if __name__ == '__main__':
    plac.call(main)
