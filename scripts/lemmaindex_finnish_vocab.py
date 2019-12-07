import json
import sys
from voikko import libvoikko


def main():
    voikko = libvoikko.Voikko('fi')

    adj_index = set()
    noun_index = set()
    propn_index = set()
    for line in sys.stdin:
        _, word = line.strip().split(' ', 1)
        for analysis in voikko.analyze(word):
            baseform = (analysis.get('BASEFORM')
                        .rsplit('-', 1)[-1]
                        .lower())

            if is_noun(analysis) and valid_noun(analysis):
                noun_index.add(baseform)
            elif is_propn(analysis):
                propn_index.add(baseform)
            elif is_adj(analysis):
                adj_index.add(baseform)

    index = {
        'adj': sorted(adj_index),
        'noun': sorted(noun_index),
        'num': num_words(),
        'propn': sorted(propn_index),
    }

    json.dump(index, fp=sys.stdout, indent=2, ensure_ascii=False)


def is_noun(analysis):
    basic_noun = (
        analysis.get('CLASS') == 'nimisana' and
        analysis.get('SIJAMUOTO') == 'nimento' and
        analysis.get('NUMBER') == 'singular')
    # minen_noun = (
    #     analysis.get('CLASS') == 'teonsana' and
    #     analysis.get('MOOD') == 'MINEN-infinitive' and
    #     analysis.get('SIJAMUOTO') == 'nimento' and
    #     analysis.get('NUMBER') == 'singular')

    return basic_noun


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
