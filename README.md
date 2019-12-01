# Preparing Finnish lemmatization lookup for SpaCy

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

scripts/download_data.sh

scripts/build_lookups.sh
```
