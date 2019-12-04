import json
import sys
import plac
from collections import OrderedDict


@plac.annotations(
    file1=('One lemma index file', 'positional'),
    file2=('Another lemma index file', 'positional'),
)
def main(file1, file2):
    with open(file1) as f1, open(file2) as f2:
        index1 = json.load(f1)
        index2 = json.load(f2)

        keys = set(index1.keys())
        keys.update(set(index2.keys()))

        merged = OrderedDict()
        for pos in sorted(keys):
            words = set(index1.get(pos, []))
            words.update(index2.get(pos, []))
            merged[pos] = sorted(words)

    json.dump(merged, fp=sys.stdout, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    plac.call(main)
