import json
import sys
from voikko import libvoikko


def main():
    voikko = libvoikko.Voikko('fi')

    adj_index = set()
    noun_index = set()
    propn_index = set()
    verb_index = set()
    for line in sys.stdin:
        _, word = line.strip().split(' ', 1)
        for baseform, wtype in analyse(word, voikko):
            if wtype == 'noun':
                noun_index.add(baseform)
            elif wtype == 'propn':
                propn_index.add(baseform)
            elif wtype == 'adj':
                adj_index.add(baseform)
            elif wtype == 'verb':
                verb_index.add(baseform)

    index = {
        'adj': sorted(adj_index),
        'noun': sorted(noun_index),
        'num': num_words(),
        'propn': sorted(propn_index),
        'verb': sorted(verb_index),
    }

    json.dump(index, fp=sys.stdout, indent=2, ensure_ascii=False)


def analyse(word, voikko):
    res = []
    for analysis in voikko.analyze(word):
        baseform = (analysis.get('BASEFORM')
                    .rsplit('-', 1)[-1]
                    .lower())

        if is_noun(analysis):
            if valid_noun(analysis):
                res.append((baseform, 'noun'))
        elif is_minen_noun(analysis):
            res.append((word, 'noun'))
        elif is_propn(analysis):
            res.append((baseform, 'propn'))
        elif is_adj(analysis):
            res.append((baseform, 'adj'))
        elif is_verb(analysis):
            res.append((baseform, 'verb'))

    return res


def is_noun(analysis):
    return (analysis.get('CLASS') == 'nimisana' and
            analysis.get('SIJAMUOTO') == 'nimento' and
            analysis.get('NUMBER') == 'singular')


def is_minen_noun(analysis):
    return (analysis.get('CLASS') == 'teonsana' and
            analysis.get('MOOD') == 'MINEN-infinitive' and
            analysis.get('SIJAMUOTO') == 'nimento' and
            analysis.get('NUMBER') == 'singular')


def valid_noun(analysis):
    # Ignore forms like aurinkoamme, avioliittoamme
    return (not analysis.get('BASEFORM').endswith('mme')
            or (analysis.get('BASEFORM') in ['amme', 'lumme']))


def is_propn(analysis):
    return (analysis.get('CLASS') in ['etunimi', 'sukunimi', 'paikannimi'] and
            analysis.get('SIJAMUOTO') == 'nimento' and
            analysis.get('NUMBER') == 'singular')


def is_adj(analysis):
    return (analysis.get('CLASS') in ['laatusana', 'nimisana_laatusana'] and
            analysis.get('SIJAMUOTO') == 'nimento' and
            analysis.get('NUMBER') == 'singular' and
            analysis.get('COMPARISON') == 'positive')


def is_verb(analysis):
    return (analysis.get('CLASS') == 'teonsana' and
            analysis.get('MOOD') == 'A-infinitive')


def num_words():
    return [
        "nolla",
        "yksi",
        "kaksi",
        "kolme",
        "neljä",
        "viisi",
        "kuusi",
        "seitsemän",
        "kahdeksan",
        "yhdeksän",
        "kymmenen",
        "yksitoista",
        "kaksitoista",
        "kolmetoista",
        "neljätoista",
        "viisitoista",
        "kuusitoista",
        "seitsemäntoista",
        "kahdeksantoista",
        "yhdeksäntoista",
        "kaksikymmentä",
        "kolmekymmentä",
        "neljäkymmentä",
        "viisikymmentä",
        "kuusikymmentä",
        "seitsemänkymmentä",
        "kahdeksankymmentä",
        "yhdeksänkymmentä",
        "sata",
        "tuhat",
        "miljoona",
        "miljardi",
        "triljoona",
    ]


if __name__ == '__main__':
    main()
