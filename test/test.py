from fi.lemmatizer import create_lemmatizer
from itertools import chain


def check(lemmatizer, cases):
    expanded = list(chain.from_iterable(
        [(word, lemma, pos) for word, lemma in words]
        for pos, words in cases.items()
    ))
    
    errors = 0
    for (word, lemma, univ_pos) in expanded:
        observed = lemmatizer(word, univ_pos)[0]
        if observed.lower() != lemma.lower():
            errors += 1
            print(f'{word} ({univ_pos}): {observed} != {lemma}')

    return errors/len(expanded)


testcases = {
    'noun': [
        ('tila', 'tila'),
        ('tilassa', 'tila'),
        ('tilakaan', 'tila'),
        ('tilassakaan', 'tila'),
        ('tilassammekaan', 'tila'),
        ('tilasi', 'tila'),
        ('tilamme', 'tila'),
        ('rakkaasi', 'rakas'),
        ('opettajiimme', 'opettaja'),
        ('marjaansa', 'marja'),
        ('marjaksemme', 'marja'),
        ('isäksesi', 'isä'),
        ('sahaansa', 'saha'),
        ('sahojensa', 'saha'),
        ('taloihinsa', 'talo'),
        ('hahmoaan', 'hahmo'),
        ('kukissaan', 'kukka'),
        ('öissä', 'yö'),
        ('ylitöissä', 'ylityö'),
        ('ääri-ilmiöissä', 'ääri-ilmiö'),
        ('emäntien', 'emäntä'),
        ('perusteluissa', 'perustelu'),
        ('esittelijä', 'esittelijä'),
        ('esittelijät', 'esittelijä'),
        ('ampumahiihtäjä', 'ampumahiihtäjä'),
        ('ampumahiihtäjäksi', 'ampumahiihtäjä'),
        ('urheilu-ura', 'urheilu-ura'),
        ('tilanne', 'tilanne'),
        ('ensi-ilta', 'ensi-ilta'),
        ('elokuvan', 'elokuva'),
        ('tietoja', 'tieto'),
        ('aika', 'aika'),
        ('tuli', 'tuli'),
        ('löytäminen', 'löytäminen'),
        ('teitä', 'tie'),
        ('puku', 'puku'),
        ('tonttupukuihin', 'tonttupuku'),
        ('kuopistaan', 'kuoppa'),
        ('maakuopistaan', 'maakuoppa'),
        ('johdolle', 'johto'),
        ('tietohallintajohdolle', 'tietohallintajohto'),
        ('epäjärjestelmällisyydellä', 'epäjärjestelmällisyys'),
        ('epäjärjestelmällisyydelläänkäänköhän', 'epäjärjestelmällisyys'),
        ('sanottavansa', 'sanottava'),
        ('1500-luvulla', '1500-luku'),
        ('kokkoko', 'kokko'),
        ('yksikkö', 'yksikkö'),
        ('yksikkökö', 'yksikkö'),
        ('leipä', 'leipä'),
        ('työlupa', 'työlupa'),
        ('työlupakaan', 'työlupa'),

        # gradation test cases
        # av1
        ('valikon', 'valikko'),
        ('maton', 'matto'),
        ('kaapin', 'kaappi'),
        ('ruukun', 'ruukku'),
        ('somman', 'sompa'),
        ('tavan', 'tapa'),
        ('kunnan', 'kunta'),
        ('killan', 'kilta'),
        ('kerran', 'kerta'),
        ('pöydän', 'pöytä'),
        ('hangon', 'hanko'),
        ('puvun', 'puku'),
        ('kyvyn', 'kyky'),
        # av2
        ('riitteen', 'riite'),
        ('oppaan', 'opas'),
        ('liikkeen', 'liike'),
        ('lumpeen', 'lumme'),
        ('tarpeen', 'tarve'),
        ('ranteen', 'ranne'),
        ('siveltimen', 'sivellin'),
        ('vartaan', 'varras'),
        ('sateen', 'sade'),
        ('kankaan', 'kangas'),
        # av3
        ('järjen', 'järki'),
        # av4
        ('palkeen', 'palje'),
        # av5
        ('vuoan', 'vuoka'),
        # av6
        ('säikeen', 'säie')
    ],

    'verb': [
        ('ei', 'ei'),
        ('en', 'ei'),
        ('emme', 'ei'),
        ('ettekö', 'ei'),
        ('oli', 'olla'),
        ('olitte', 'olla'),
        ('raahaa', 'raahata'),
        ('annan', 'antaa'),
        ('kimpaantunut', 'kimpaantua'),
        ('pyytänyt', 'pyytää'),
        ('tuli', 'tulla'),
        ('tulee', 'tulla'),
        ('pelastuimme', 'pelastua'),
        ('hukkaan', 'hukkaan'),

        # gradation, av2
        ('lobbaan', 'lobata'),
        ('diggaan', 'digata'),
    ],

    'adj': [
        ('normaaliin', 'normaali'),
        ('kimpaantunut', 'kimpaantunut'),
        ('lämmin', 'lämmin'),
        ('maalaamatontakin', 'maalaamaton'),
    ],

    'propn': [
        ('Etelä-Afrikassa', 'Etelä-Afrikka'),
        ('Hangossa', 'Hanko'),
        ('Belgiakin', 'Belgia'),
        ('Tampereeltamme', 'Tampere'),
        ('Annan', 'Anna'),
    ],

    'adv': [
        ('vuoksi', 'vuoksi'),
        ('tänäänkin', 'tänään'),
        ('kohta', 'kohta'),
        ('piankin', 'pian'),
    ],

    'num': [
        ('nollakin', 'nolla'),
        ('neljäs', 'neljä'),
        ('viiden', 'viisi'),
        ('viidenkin', 'viisi'),
        ('kymmentä', 'kymmenen'),
        ('kymmeniä', 'kymmenen'),
        ('kymmenes', 'kymmenen'),
        ('tuhannen', 'tuhat'),
        ('miljoonaa', 'miljoona'),
    ],

    # 'pron': [
    #     ('sen', 'se'),
    #     ('siitä', 'se'),
    #     ('niiden', 'se'),
    #     ('hänet', 'hän'),
    #     ('jonkin', 'jonkin'),
    #     ('teitä', 'sinä'),
    # ],
}

lemmatizer = create_lemmatizer()
failed_prop = check(lemmatizer, testcases)

if failed_prop > 0:
    print(f'Failed: {failed_prop*100:.1f} % ')
