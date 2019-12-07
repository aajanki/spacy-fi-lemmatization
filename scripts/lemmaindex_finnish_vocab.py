import json
import sys
from voikko import libvoikko


def main():
    voikko = libvoikko.Voikko('fi')

    noun_index = set()
    propn_index = set()
    for line in sys.stdin:
        _, word = line.strip().split(' ', 1)
        analyses = [
            x for x in voikko.analyze(word)
            if (is_noun(x) and valid_noun(x)) or is_propn(x)
        ]

        if analyses:
            idx = propn_index if is_propn(analyses[0]) else noun_index
            baseform = (analyses[0].get('BASEFORM')
                        .rsplit('-', 1)[-1]
                        .lower())
            if baseform:
                idx.add(baseform)

    noun_index = sorted(noun_index)
    propn_index = sorted(propn_index)

    index = {
        'noun': noun_index,
        'num': num_words(),
        'propn': propn_index,
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
