from fi.lemmatizer import create_lemmatizer
from itertools import chain


def check(cases, accept_less_common=True):
    lemmatizer = create_lemmatizer()
    expanded = list(chain.from_iterable(
        [(word, lemmas, pos) for word, lemmas in words]
        for pos, words in cases.items()
    ))
    
    errors = 0
    for (word, lemmas, univ_pos) in expanded:
        if not accept_less_common:
            lemms = lemmas[:1]
        lemmas = [x.lower() for x in lemmas]

        observed = lemmatizer(word, univ_pos)[0]
        if observed.lower() not in lemmas:
            errors += 1
            print(f'{word} ({univ_pos}): {observed} != {lemmas}')

    return errors/len(expanded)


testcases = {
    'noun': [
        ('tila', ['tila']),
        ('tilassa', ['tila']),
        ('tilakaan', ['tila']),
        ('tilassakaan', ['tila']),
        ('tilassammekaan', ['tila']),
        ('tilasi', ['tila']),
        ('tilamme', ['tila']),
        ('rakkaasi', ['rakas', 'rakka']),
        ('opettajiimme', ['opettaja']),
        ('marjaansa', ['marja']),
        ('marjaksemme', ['marja']),
        ('isäksesi', ['isä']),
        ('sahaansa', ['saha']),
        ('sahojensa', ['saha']),
        ('taloihinsa', ['talo']),
        ('hahmoaan', ['hahmo']),
        ('kukissaan', ['kukka']),
        ('öissä', ['yö']),
        ('ylitöissä', ['ylityö']),
        ('emäntien', ['emäntä', 'emäntie']),
        ('perusteluissa', ['perustelu']),
        ('esittelijä', ['esittelijä']),
        ('esittelijät', ['esittelijä']),
        ('tilanne', ['tilanne']),
        ('ensi-ilta', ['ensi-ilta']),
        ('elokuvan', ['elokuva']),
        ('tietoja', ['tieto']),
        ('aika', ['aika']),
        ('tuli', ['tuli']),
        ('löytäminen', ['löytäminen']),
        ('teitä', ['tie']),
        ('epäjärjestelmällisyydellä', ['epäjärjestelmällisyys']),
        ('epäjärjestelmällisyydelläänkäänköhän', ['epäjärjestelmällisyys']),
        ('koko', ['koko']),
        ('kokkoko', ['kokko']),
        ('yksikkö', ['yksikkö']),
        ('yksikkökö', ['yksikkö']),
        ('leipä', ['leipä']),
        ('vanhemmaksi', ['vanhempi']),
        ('vanhempana', ['vanhempi']),
        ('perheenne', ['perhe']),
        ('ruokaa', ['ruoka']),
        ('tulevaisuudessa', ['tulevaisuus']),
        ('ihminen', ['ihminen']),
        ('ajaminenkaan', ['ajaminen']),
        ('testaamisessa', ['testaaminen']),
        ('yksipuolistuminen', ['yksipuolistuminen']),
        ('sulautumiseen', ['sulautuminen']),

        # compound words
        ('1500-luvulla', ['1500-luku']),
        ('ääri-ilmiöissä', ['ääri-ilmiö', 'ääri-ilmiyö']),
        ('ampumahiihtäjä', ['ampumahiihtäjä']),
        ('ampumahiihtäjäksi', ['ampumahiihtäjä']),
        ('urheilu-ura', ['urheilu-ura']),
        ('puku', ['puku']),
        ('tonttupukuihin', ['tonttupuku']),
        ('kuopistaan', ['kuoppa']),
        ('maakuopistaan', ['maakuoppa']),
        ('johdolle', ['johto']),
        ('tietohallintajohdolle', ['tietohallintajohto']),
        ('työlupa', ['työlupa']),
        ('työlupakaan', ['työlupa']),
        ('markkinavalvonnalla', ['markkinavalvonta']),
        ('yökerhossa', ['yökerho']),
        ('lähtökohdiltaan', ['lähtökohta']),
        ('voimakeinoja', ['voimakeino']),
        ('keskiluokkaa', ['keskiluokka']),
        ('kirjoitusasulla', ['kirjoitusasu']),
        ('kansalaisuuskäsitteenä', ['kansalaisuuskäsite']),

        # gradation test cases
        # av1
        ('valikon', ['valikko']),
        ('maton', ['matto']),
        ('kaapin', ['kaappi']),
        ('ruukun', ['ruukku']),
        ('somman', ['sompa']),
        ('tavan', ['tapa']),
        ('kunnan', ['kunta']),
        ('killan', ['kilta']),
        ('kerran', ['kerta']),
        ('pöydän', ['pöytä']),
        ('hangon', ['hanko']),
        ('puvun', ['puku']),
        ('kyvyn', ['kyky']),
        # av2
        ('riitteen', ['riite']),
        ('oppaan', ['opas']),
        ('liikkeen', ['liike']),
        ('lumpeen', ['lumme']),
        ('tarpeen', ['tarve']),
        ('ranteen', ['ranne']),
        ('siveltimen', ['sivellin']),
        ('vartaan', ['varras']),
        ('sateen', ['sade']),
        ('kankaan', ['kangas']),
        # av3
        ('järjen', ['järki']),
        # av4
        ('palkeen', ['palje']),
        # av5
        ('vuoan', ['vuoka']),
        # av6
        ('säikeen', ['säie'])
    ],

    'verb': [
        # negation
        ('ei', ['ei']),
        ('en', ['ei']),
        ('emme', ['ei']),
        ('ettekö', ['ei']),
        ('älkää', ['ei']),

        # olla
        ('oli', ['olla']),
        ('olitte', ['olla']),
        ('ole', ['olla']),
        ('olisi', ['olla']),

        # person
        ('annan', ['antaa']),
        ('hukkaan', ['hukata']),
        ('lasket', ['laskea']),
        ('laskee', ['laskea']),
        ('punoo', ['punoa']),
        ('ampuu', ['ampua']),
        ('raahaa', ['raahata']),
        ('tulee', ['tulla']),
        ('häviätte', ['hävitä']),
        ('kitisevät', ['kitistä']),
        ('täytyy', ['täytyä']),
        ('grillailen', ['grillailla']),
        ('pyöritteli', ['pyöritellä']),

        # past tense
        ('kelluit', ['kellua']),
        ('tuli', ['tulla']),
        ('pinositte', ['pinota']),
        ('valaistuivat', ['valaistua']),
        ('jäi', ['jäädä']),
        ('friikahti', ['friikahtaa']),

        # conditional
        ('hakisi', ['hakea']),
        ('imartelisitte', ['imarrella']),
        ('karmisi', ['karmia']),

        # passive
        ('esitellään', ['esitellä']),

        # imperative
        ('järisyttäköön', ['järisyttää']),
        ('astukoon', ['astua']),
        ('nähdäkseen', ['nähdä']),

        # A-infinitive
        ('pelastua', ['pelastua']),
        ('pelastuimme', ['pelastua']),

        # NUT-participle
        ('kimpaantunut', ['kimpaantua']),
        ('pyytänyt', ['pyytää']),

        # enclitics
        ('pohdinko', ['pohtia']),
        ('lähdettehän', ['lähteä']),

        # gradation
        #av1
        ('ilkutte', ['ilkkua']),
        # av2
        ('lobbaatte', ['lobata']),
        ('diggaavat', ['digata']),
        # av3
        ('hyljit', ['hylkiä']),
        # av4
        ('ilkeät', ['iljetä']),
        # av5
        ('aion', ['aikoa']),
        # av6
        ('aukeat', ['aueta']),
    ],

    'adj': [
        ('lämmin', ['lämmin']),
        ('mielenkiintoinen', ['mielenkiintoinen']),
        ('normaaliin', ['normaali']),
        ('kimpaantunut', ['kimpaantunut']),
        ('maalaamatontakin', ['maalaamaton']),
        ('kultaiset', ['kultainen']),
        ('punaisten', ['punainen']),
        ('sujuvilla', ['sujuva']),
        ('ranskalaisemme', ['ranskalainen']),
        ('ihanan', ['ihana']),

        # komparatiivi
        ('lämpimämpi', ['lämmin']),
        ('surullisempi', ['surullinen']),
        ('voimakkaampi', ['voimakas']),
        ('uudempi', ['uusi']),
        ('parempi', ['hyvä']),

        # superlatiivi
        ('lämpimin', ['lämmin']),
        ('kaunein', ['kaunis']),
        ('nopein', ['nopea']),
        ('lyhyin', ['lyhyt']),
        ('paras', ['hyvä']),
    ],

    'propn': [
        ('Etelä-Afrikassa', ['Etelä-Afrikka']),
        ('Hangosta', ['Hanko']),
        ('Belgiakin', ['Belgia']),
        ('Tampereeltamme', ['Tampere']),
        ('Annan', ['Anna']),
    ],

    'adv': [
        ('vuoksi', ['vuoksi']),
        ('tänäänkin', ['tänään']),
        ('kohta', ['kohta']),
        ('piankin', ['pian']),
    ],

    'num': [
        ('nollakin', ['nolla']),
        ('neljäs', ['neljäs']),
        ('viiden', ['viisi']),
        ('viidenkin', ['viisi']),
        ('kymmentä', ['kymmenen']),
        ('kymmeniä', ['kymmenen']),
        ('kymmenes', ['kymmenes']),
        ('tuhannen', ['tuhat']),
        ('miljoonaa', ['miljoona']),
        ('kahdesta', ['kaksi']),
        ('yhtenä', ['yksi']),
    ],

    # 'pron': [
    #     ('sen', ['se']),
    #     ('siitä', ['se']),
    #     ('niiden', ['se']),
    #     ('hänet', ['hän']),
    #     ('jonkin', ['jonkin']),
    #     ('teitä', ['sinä']),
    # ],
}

failed_prop = check(testcases)

if failed_prop > 0:
    print(f'Failed: {failed_prop*100:.1f} % ')
