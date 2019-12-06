import json
import sys
from itertools import chain


verb_exc_data = {
    'ei': ['en', 'et', 'ei', 'emme', 'ette', 'eivät'],
    'olla': [
        'olla', 'olen', 'olet', 'on', 'olemme', 'olette', 'ovat',
        'olin', 'olit', 'oli', 'olimme', 'olitte', 'olivat',
        'ollut', 'olleet',
        'lienen', 'lienet', 'lienee', 'lienemme', 'lienette', 'lienevät'
    ]
}

verb_exceptions = {
    form: [lemma] for lemma, form in chain.from_iterable(
        [(lemma, form) for form in forms]
        for lemma, forms in verb_exc_data.items()
    )
}

num_exc_data = {
    'yksi': ['ensimmäinen', 'yhden', 'yhtä', 'yhteen'],
    'kaksi': ['toinen', 'kahden', 'kahta', 'kahteen'],
    'kolme': ['kolmas', 'kolmen', 'kolmea', 'kolmeen'],
    'neljä': ['neljäs', 'neljän', 'neljää', 'neljään'],
    'viisi': ['viides', 'viiden', 'viittä', 'viiteen'],
    'kuusi': ['kuudes', 'kuuden', 'kuutta', 'kuuteen'],
    'seitsemän': ['seitsemäs', 'seitsemän', 'seitsemää', 'seitsemään'],
    'kahdeksan': ['kahdeksas', 'kahdeksaa', 'kahdeksaan'],
    'yhdeksän': ['yhdeksäs', 'yhdeksää', 'yhdeksään'],
    'kymmenen': ['kymmenes', 'kymmentä', 'kymmeneen'],
    'yksitoista': ['yhdestoista', 'yhdentoista', 'yhtätoista', 'yhteentoista'],
    'kaksitoista': ['kahdestoista', 'kahdentoista', 'kahtatoista', 'kahteentoista'],
    'kolmetoista': ['kolmastoista', 'kolmentoista', 'kolmeatoista', 'kolmeentoista'],
    'neljätoista': ['neljästoista', 'neljäntoista', 'neljäätoista', 'neljääntoista'],
    'viisitoista': ['viidestoista', 'viidentoista', 'viittätoista', 'viiteentoista'],
    'kuusitoista': ['kuudestoista', 'kuudentoista', 'kuuteentoista', 'kuuttatoista'],
    'seitsemäntoista': ['seitsemästoista', 'seitsemääntoista', 'seitsemäätoista'],
    'kahdeksantoista': ['kahdeksastoista', 'kahdeksaantoista', 'kahdeksaatoista'],
    'yhdeksäntoista': ['yhdeksästoista', 'yhdeksääntoista', 'yhdeksäätoista'],
    'sata': ['sadas', 'sadan', 'sataa', 'sataan'],
    'tuhat': ['tuhannes', 'tuhannen', 'tuhatta', 'tuhanteen'],
    'miljoona': ['miljoonas', 'miljoonan', 'miljoonaa', 'miljoonaan'],
}

num_exceptions = {
    form: [lemma] for lemma, form in chain.from_iterable(
        [(lemma, form) for form in forms]
        for lemma, forms in num_exc_data.items()
    )
}


exc = {
    'verb': verb_exceptions,
    'num': num_exceptions,
}

json.dump(exc, fp=sys.stdout, indent=2, ensure_ascii=False)
