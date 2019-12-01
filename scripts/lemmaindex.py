import json
import sys
from lxml import etree

tags = {
    'adjective': 'ADJ',
    'adverb': 'ADV',
    'noun': 'NOUN',
    'pnoun_firstname': 'PROPN',
    'pnoun_lastname': 'PROPN',
    'pnoun_misc': 'PROPN',
    'pnoun_place': 'PROPN',
    'verb': 'VERB'
}

index = {}
root = etree.parse(sys.stdin)
for wclass, upos in tags.items():
    forms = root.xpath(f"/wordlist/word[./classes/wclass = '{wclass}']/forms/form/text()")
    forms = (w.replace('=', '') for w in forms)
    index.setdefault(upos, []).extend(forms)

index = {upos: sorted(forms) for upos, forms in index.items()}
    
json.dump(index, fp=sys.stdout, indent=2, ensure_ascii=False)
