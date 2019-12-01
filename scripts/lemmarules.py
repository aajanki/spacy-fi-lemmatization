import json
import voikkoinfl
import plac
from collections import OrderedDict


@plac.annotations(
    noun_affix_file=('Path to the noun affix file', 'positional'),
    verb_affix_file=('Path to the verb affix file', 'positional'),
    output=('Output file path', 'positional'),
)
def main(noun_affix_file, verb_affix_file, output):
    rules = []
    noun_types = voikkoinfl.readInflectionTypes(noun_affix_file)
    for t in noun_types:
        for rule in t.inflectionRules:
            for old, new in expand(rule):
                rules.append((old, new))

    rules = list(OrderedDict.fromkeys(rules))

    with open(output, 'w', encoding='utf-8') as fp:
        json.dump(rules, fp=fp, indent=2, ensure_ascii=False)


def expand(rule):
    for a, b, _ in voikkoinfl.__regex_to_hunspell(rule.delSuffix, rule.addSuffix):
        if a == '0':
            a = ''
        if b == '0':
            b = ''
        a = a.strip("'")
        b = b.strip("'")

        if a or b:
            yield (b, a)

            a_front_vow = voikkoinfl.__convert_tv_ev(a)
            b_front_vow = voikkoinfl.__convert_tv_ev(b)
            if a != a_front_vow or b != b_front_vow:
                yield (b_front_vow, a_front_vow)


if __name__ == '__main__':
    plac.call(main)
