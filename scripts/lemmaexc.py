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
    'yksi': [
        'yhden', 'yhtä', 'yhtenä', 'yhdeksi', 'yhdessä', 'yhdestä',
        'yhteen', 'yhdellä', 'yhdeltä', 'yhdelle',
        'yhdet', 'yksien', 'yksiä', 'yksinä', 'yksiksi', 'yksissä',
        'yksistä', 'yksiin', 'yksillä', 'yksiltä', 'yksille',
    ],
    'kaksi': [
        'kahden', 'kahta', 'kahtena', 'kahdeksi', 'kahdessa', 'kahdesta',
        'kahteen', 'kahdella', 'kahdelta', 'kahdelle',
        'kahdet', 'kaksien', 'kaksia', 'kaksina', 'kaksiksi', 'kaksissa',
        'kaksista', 'kaksiin', 'kaksilla', 'kaksilta', 'kaksille',
    ],
    'kolme': [
        'kolmen', 'kolmea', 'kolmena', 'kolmeksi', 'kolmessa', 'kolmesta',
        'kolmeen', 'kolmella', 'kolmelta', 'kolmelle',
        'kolmet', 'kolmien', 'kolmia', 'kolmina', 'kolmiksi', 'kolmissa',
        'kolmista', 'kolmiin', 'kolmilla', 'kolmilta', 'kolmille',
    ],
    'neljä': [
        'neljän', 'neljää', 'neljänä', 'neljäksi', 'neljässä', 'neljästä',
        'neljään', 'neljällä', 'neljältä', 'neljälle',
        'neljät', 'neljien', 'neljiä', 'neljinä', 'neljiksi', 'neljissä',
        'neljistä', 'neljiin', 'neljillä', 'neljiltä', 'neljille',
    ],
    'viisi': [
        'viiden', 'viittä', 'viitenä', 'viideksi', 'viidessä', 'viidestä',
        'viiteen', 'viidellä', 'viideltä', 'viidelle',
        'viidet', 'viisien', 'viisiä', 'viisinä', 'viisiksi', 'viisissä',
        'viisistä', 'viisiin', 'viisillä', 'viisiltä', 'viisille',
    ],
    'kuusi': [
        'kuuden', 'kuutta', 'kuutena', 'kuudeksi', 'kuudessa', 'kuudesta',
        'kuuteen', 'kuudella', 'kuudelta', 'kuudelle',
        'kuudet', 'kuusien', 'kuusia', 'kuusina', 'kuusiksi', 'kuusissa',
        'kuusista', 'kuusiin' 'kuusilla', 'kuusilta', 'kuusille',
    ],
    'seitsemän': [
        'seitsemää', 'seitsemänä', 'seitsemäksi', 'seitsemässä', 'seitsemästä',
        'seitsemään', 'seitsemällä', 'seitsemältä', 'seitsemälle',
        'seitsemät', 'seitsemien', 'seitsemiä', 'seitseminä', 'seitsemiksi',
        'seitsemissä', 'seitsemistä', 'seitsemiin', 'seitsemillä',
        'seitsemiltä', 'seitsemille',
    ],
    'kahdeksan': [
        'kahdeksaa', 'kadeksana', 'kahdeksaksi', 'kahdeksassa', 'kahdeksasta',
        'kahdeksaan', 'kahdeksalla', 'kahdeksalta', 'kahdeksalle',
        'kahdeksat', 'kahdeksien', 'kahdeksia', 'kahdeksina', 'kahdeksiksi',
        'kahdeksissa', 'kahdeksista', 'kahdeksiin', 'kahdeksilla',
        'kahdeksilta', 'kahdeksille',
    ],
    'yhdeksän': [
        'yhdeksää', 'yhdeksänä', 'yhdeksäksi', 'yhdeksässä', 'yhdeksästä',
        'yhdeksään', 'yhdeksällä', 'yhdeksältä', 'yhdeksälle',
        'yhdeksät', 'yhdeksien', 'yhdeksiä', 'yhdeksinä', 'yhdeksiksi',
        'yhdeksissä', 'yhdeksistä', 'yhdeksiin', 'yhdeksillä', 'yhdeksiltä',
        'yhdeksille',
    ],
    'kymmenen': [
        'kymmentä', 'kymmenenä', 'kymmeneksi', 'kymmenessä', 'kymmenestä',
        'kymmeneen', 'kymmenellä', 'kymmeneltä', 'kymmenelle',
        'kymmenet', 'kymmenien', 'kymmeniä', 'kymmeninä', 'kymmeniksi',
        'kymmenissä', 'kymmenistä', 'kymmeniin', 'kymmenillä', 'kymmeniltä',
        'kymmenille',
    ],
    'tuhat': [
        'tuhannen', 'tuhatta', 'tuhantena', 'tuhanneksi', 'tuhannessa',
        'tuhannesta', 'tuhanteen', 'tuhannella', 'tuhannelta', 'tuhannelle',
        'tuhannet', 'tuhansien', 'tuhansia', 'tuhansina', 'tuhansiksi',
        'tuhansissa', 'tuhansiksi', 'tuhansissa', 'tuhansista', 'tuhansiin',
        'tuhansilla', 'tuhansilta', 'tuhansille',
    ],
    # sata, miljoona and miljardi have regular inflections
}

for num in [
        'yksi', 'kaksi', 'kolme', 'neljä', 'viisi', 'kuusi',
        'seitsemän', 'kahdeksan', 'yhdeksän'
]:
    num_exc_data[num + 'toista'] = [
        form + 'toista' for form in num_exc_data[num]
    ]

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
