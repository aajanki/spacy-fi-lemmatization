# Evaluate the lemmatizer on conllu data file printing mismatched lemmas

import sys
from fi.lemmatizer import create_lemmatizer


num_words = 0
errors = {}
lemmatizer = create_lemmatizer()
for line in sys.stdin:
    line = line.strip()
    if not line or line.startswith('#'):
        continue

    num_words += 1
    columns = line.split('\t')
    word = columns[1]
    expected = [
        columns[2].replace('#', '').lower(),
        columns[2].replace('#', '-').lower()
    ]
    upos = columns[3]
    if upos == 'AUX':
        upos = 'VERB'
    if upos in ['NOUN', 'VERB', 'ADJ', 'ADV', 'PROPN', 'ADP']:
        observed = lemmatizer(word.strip('-'), upos)

        if observed and observed[0].lower() not in expected:
            if upos not in errors:
                errors[upos] = 0
            errors[upos] += 1

            print(f'{word} ({upos}): {observed[0]} != {expected[0]}')

print()
print('Error counts by POS tag:')

for upos, count in sorted(errors.items(), key=lambda x: -x[1]):
    print(f'{upos}\t{count}')

total_errors = sum(errors.values())
print(f'Total\t{total_errors}, proportion: {total_errors/num_words*100:.1f} %')
