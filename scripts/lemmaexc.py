import json
import sys
from itertools import chain


def expand(exc):
    return {
        form: [lemma] for lemma, form in chain.from_iterable(
            [(lemma, form) for form in forms]
            for lemma, forms in exc.items()
        )
    }


verb_exc_data = {
    'ei': [
        'en', 'et', 'ei', 'emme', 'ette', 'eivät',
        'älä', 'älköön', 'älkäämme', 'älkää', 'älkööt',
    ],
    'olla': [
        # present tense
        'olla', 'olen', 'olet', 'on', 'olemme', 'olette', 'ovat', 'ollut',
        # past tense
        'olin', 'olit', 'oli', 'olimme', 'olitte', 'olivat', 'oltu',
        'olleet',
        # conditional
        'olisin', 'olisit', 'olisi', 'olisimme', 'olisitte', 'olisivat',
        'oltaisiin', 'olisi',
        # imperative
        'ole', 'olkoon', 'olkaamme', 'olkaa', 'olkoot', 'olko',
        # potential
        'lienen', 'lienet', 'lienee', 'lienemme', 'lienette', 'lienevät',
        'liene',
    ],
    'tuntea': [
        # present tense
        'tunnen', 'tunnet', 'tuntee', 'tunnemme', 'tunnette', 'tuntevat',
        'tunnetaan', 'tunne', 'tunneta',
        # past tense
        'tunsin', 'tunsit', 'tunsi', 'tunsimme', 'tunsitte', 'tunsivat',
        'tunnettiin', 'tunnettu', 'tuntenut', 'tunteneet'
        # conditional
        'tuntisin', 'tuntisit', 'tuntisi', 'tuntisimme', 'tuntisitte',
        'tunnettaisiin', 'tunnettaisi',
        # imperative
        'tunne', 'tuntekoon', 'tuntekaamme', 'tuntekaa', 'tuntekoot', 'tunteko',
        # potential
        'tuntenen', 'tuntenet', 'tuntenee', 'tuntenemme', 'tuntenette',
        'tuntenevat', 'tuntene'
    ],
    'lähteä': [
        # present tense
        'lähden', 'lähdet', 'lähtee', 'lähdemme', 'lähdette', 'lähtevät',
        'lähdetään', 'lähde', 'lähdetä',
        # past tense
        'lähdin', 'lähdit', 'lähti', 'lähdimme', 'lähditte', 'lähtivät',
        'lähdettiin', 'lähtenyt', 'lähteneet',
        # conditional
        'lähtisin', 'lähtisit', 'lähtisi', 'lähtisimme', 'lähtisitte',
        'lähtisivät', 'lähdettäisiin', 'lähdettäisi',
        # imperative
        'lähde', 'lähtekööt', 'lähtekäämme', 'lähtekää', 'lähteköön', 'lähtekö',
        # potential
        'lähtenen', 'lähtenet', 'lähtenee', 'lähtenemme', 'lähtenet',
        'lähtenevät', 'lähdettäneen', 'lähtene'
    ],
}

noun_exc_data = {
    'poika': [
        'pojan', 'poikaa', 'pojiksi', 'poikana', 'pojissa', 'pojista',
        'poikaan', 'pojilla', 'pojilta', 'pojille', 'pojitta', 'pojat',
        'poikien', 'oikia', 'pojiksi', 'poikina', 'pojissa', 'pojista',
        'poikiin', 'pojilla', 'pojilta', 'pojille', 'pojitta', 'pojin'
    ],
    'mies': [
        'miehen', 'miestä', 'mieheksi', 'miehenä', 'miehessä', 'miehestä',
        'mieheen', 'miehellä', 'mieheltä', 'miehelle', 'miehettä', 'miehet',
        'miesten', 'miehiä', 'miehiksi', 'miehinä', 'miehissä', 'miehistä',
        'miehiin', 'miehillä', 'miehiltä', 'miehille', 'miehittä', 'miehin'
    ],
    'meri': [
        'meren', 'merta', 'mereksi', 'merenä', 'meressä', 'merestä', 'mereen',
        'merellä', 'mereltä', 'merelle', 'merettä', 'meret', 'merien', 'meriä',
        'meriksi', 'merinä', 'merissä', 'meristä', 'meriin', 'merillä',
        'meriltä', 'merille', 'merittä', 'merin'
    ],
    'veri': [
        'veren', 'verta', 'vereksi', 'verenä', 'veressä', 'verestä', 'vereen',
        'verellä', 'vereltä', 'verelle', 'verettä', 'veret', 'verien', 'veriä',
        'veriksi', 'verinä', 'verissä', 'veristä', 'veriin', 'verillä',
        'veriltä', 'verille', 'verittä', 'verin'
    ],
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

adj_exc_data = {
    'hyvä': ['parempi', 'paras']
}

exc = {
    'adj': expand(adj_exc_data),
    'verb': expand(verb_exc_data),
    'noun': expand(noun_exc_data),
    'num': expand(num_exc_data),
}


if __name__ == '__main__':
    json.dump(exc, fp=sys.stdout, indent=2, ensure_ascii=False)
