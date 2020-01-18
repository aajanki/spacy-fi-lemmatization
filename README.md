# Experimental Finnish lemmatizer for SpaCy

**NOTE**: This is obsolete. See the updated version of the lemmatizer in the [spacy-fi](https://github.com/aajanki/spacy-fi) repository.

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

scripts/download_data.sh

# Evaluate lemmatizer
python scripts/eval_conllu.py < data/UD_Finnish-TDT/fi_tdt-ud-train.conllu
```

## License

GPL v3
