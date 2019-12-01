import json
import re
import voikkoinfl
import plac
from collections import OrderedDict


@plac.annotations(
    noun_affix_file=('Path to the noun affix file', 'positional'),
    verb_affix_file=('Path to the verb affix file', 'positional'),
    output=('Output file path', 'positional'),
)
def main(noun_affix_file, verb_affix_file, output):
    rule_types = {
        'noun': noun_affix_file,
        'verb': verb_affix_file
    }

    rules = {}
    for upos, file in rule_types.items():
        rulelist = []
        for t in voikkoinfl.readInflectionTypes(file):
            for rule in t.inflectionRules:
                for old, new in expand(t, rule):
                    rulelist.append((old, new))

        rulelist = list(OrderedDict.fromkeys(rulelist))
        rules[upos] = rulelist

    with open(output, 'w', encoding='utf-8') as fp:
        json.dump(rules, fp=fp, indent=2, ensure_ascii=False)


def expand(inflection_type, rule):
    for remove, add, _ in voikkoinfl.__regex_to_hunspell(rule.delSuffix, rule.addSuffix):
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
        'C': ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q',
              'r', 's', 't', 'v', 'w', 'x', 'z', 'š', 'ž'],
        'V': ['a', 'e', 'i', 'o', 'u', 'y', 'ä', 'ö', 'é', 'è', 'á', 'ó', 'â'],
        'A': ['a', 'ä'],
        'O': ['o', 'ö'],
        'U': ['u', 'y'],
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
