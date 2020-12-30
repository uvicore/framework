import pytest
from uvicore.support import str
from uvicore.support.dumper import dump, dd

testing = [
    'AcmeApp',
    'acmeApp',
    'Acme_App',
    'Acme_app',
    'acme_App',
    'Acme-app',
    'Acme-App',
    'Acme App',
    'acme app',
    'Acme app',
    'acme App',
    'AcmeAppTwo',
    'acmeAppTwo',
    'Acme_App_Two',
    'Acme_app_two',
    'acme_App_Two',
    'Acme-app-two',
    'Acme-App-Two',
    'Acme App Two',
    'acme app two',
    'Acme app two',
    'acme App Two',
    "Hi don't 12 there! my$ name 'is' matthew reschke, what is your name please???",
]

# No need to test str.slug as I use it for snake and kebab also

def test_ucbreakup():
    after = []
    for t in testing:
        after.append(str.ucbreakup(t))

    assert after == [
        'Acme App',
        'Acme App',
        'Acme App',
        'Acme App',
        'Acme App',
        'Acme App',
        'Acme App',
        'Acme App',
        'Acme App',
        'Acme App',
        'Acme App',
        'Acme App Two',
        'Acme App Two',
        'Acme App Two',
        'Acme App Two',
        'Acme App Two',
        'Acme App Two',
        'Acme App Two',
        'Acme App Two',
        'Acme App Two',
        'Acme App Two',
        'Acme App Two',
        'Hi Dont 12 There My Name Is Matthew Reschke What Is Your Name Please'
    ]


def test_ucwords():
    assert str.ucwords('thiS iS a tEsT') == 'ThiS IS A TEsT'


def test_ucfirst():
    # Ucfirst is like .title() but it leaves the rest of the case alone
    assert str.ucfirst('thiS iS a tEsT') == 'ThiS iS a tEsT'


def test_title():
    # Like ucfirst but it sets all other case to lower
    assert str.title('thiS iS a tEsT') == 'This Is A Test'


def test_snake():
    after = []
    for t in testing:
        after.append(str.snake(t))

    assert after == [
        'acme_app',
        'acme_app',
        'acme_app',
        'acme_app',
        'acme_app',
        'acme_app',
        'acme_app',
        'acme_app',
        'acme_app',
        'acme_app',
        'acme_app',
        'acme_app_two',
        'acme_app_two',
        'acme_app_two',
        'acme_app_two',
        'acme_app_two',
        'acme_app_two',
        'acme_app_two',
        'acme_app_two',
        'acme_app_two',
        'acme_app_two',
        'acme_app_two',
        'hi_dont_12_there_my_name_is_matthew_reschke_what_is_your_name_please'
    ]


def test_kebab():
    after = []
    for t in testing:
        after.append(str.kebab(t))

    assert after == [
        'acme-app',
        'acme-app',
        'acme-app',
        'acme-app',
        'acme-app',
        'acme-app',
        'acme-app',
        'acme-app',
        'acme-app',
        'acme-app',
        'acme-app',
        'acme-app-two',
        'acme-app-two',
        'acme-app-two',
        'acme-app-two',
        'acme-app-two',
        'acme-app-two',
        'acme-app-two',
        'acme-app-two',
        'acme-app-two',
        'acme-app-two',
        'acme-app-two',
        'hi-dont-12-there-my-name-is-matthew-reschke-what-is-your-name-please'
    ]


def test_studly():
    after = []
    for t in testing:
        after.append(str.studly(t))

    after == [
        'AcmeApp',
        'AcmeApp',
        'AcmeApp',
        'AcmeApp',
        'AcmeApp',
        'AcmeApp',
        'AcmeApp',
        'AcmeApp',
        'AcmeApp',
        'AcmeApp',
        'AcmeApp',
        'AcmeAppTwo',
        'AcmeAppTwo',
        'AcmeAppTwo',
        'AcmeAppTwo',
        'AcmeAppTwo',
        'AcmeAppTwo',
        'AcmeAppTwo',
        'AcmeAppTwo',
        'AcmeAppTwo',
        'AcmeAppTwo',
        'AcmeAppTwo',
        'HiDont12ThereMyNameIsMatthewReschkeWhatIsYourNamePlease'
    ]


def test_camel():
    after = []
    for t in testing:
        after.append(str.camel(t))

    after == [
        'acmeApp',
        'acmeApp',
        'acmeApp',
        'acmeApp',
        'acmeApp',
        'acmeApp',
        'acmeApp',
        'acmeApp',
        'acmeApp',
        'acmeApp',
        'acmeApp',
        'acmeAppTwo',
        'acmeAppTwo',
        'acmeAppTwo',
        'acmeAppTwo',
        'acmeAppTwo',
        'acmeAppTwo',
        'acmeAppTwo',
        'acmeAppTwo',
        'acmeAppTwo',
        'acmeAppTwo',
        'acmeAppTwo',
        'hiDont12ThereMyNameIsMatthewReschkeWhatIsYourNamePlease'
    ]

def test_words():
    assert str.words('Hi there, this is a long sentence that I can truncate!', 3) == 'Hi there, this...'
    assert str.words('Hi there, this is a long sentence that I can truncate!', 4, '+++') == 'Hi there, this is+++'
