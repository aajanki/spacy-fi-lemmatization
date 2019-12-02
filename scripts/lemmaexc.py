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

exc = {
    'verb': verb_exceptions
}

json.dump(exc, fp=sys.stdout, indent=2, ensure_ascii=False)
