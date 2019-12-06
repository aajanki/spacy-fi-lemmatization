import json
import sys
from voikko import libvoikko


voikko = libvoikko.Voikko('fi')

noun_index = set()
for line in sys.stdin:
    _, word = line.strip().split(' ', 1)
    analyses = (
        x for x in voikko.analyze(word)
        if x.get('CLASS') == 'nimisana' and
        x.get('SIJAMUOTO') == 'nimento' and
        x.get('NUMBER') == 'singular'
    )

    # Ignore forms like aurinkoamme, avioliittoamme
    analyses = [
        a for a in analyses
        if (not a.get('BASEFORM').endswith('mme')
            or (a.get('BASEFORM') in ['amme', 'lumme']))
    ]

    if analyses:
        baseform = (analyses[0].get('BASEFORM')
                    .rsplit('-', 1)[-1]
                    .lower())
        noun_index.add(baseform)

noun_index = sorted(noun_index)

index = {
    'noun': noun_index
}

json.dump(index, fp=sys.stdout, indent=2, ensure_ascii=False)
