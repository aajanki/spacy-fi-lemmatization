# Preparing Finnish lemmatization lookup for SpaCy

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

scripts/download_data.sh

# Evaluate lemmatizer
python scripts/eval_conllu.py < data/UD_Finnish-TDT/fi_tdt-ud-train.conllu
```
