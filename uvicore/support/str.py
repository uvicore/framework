import re


def ucbreakup(value: str):
    """Breakup words with by - _ or camel and uppercase first letter of each word stripping non alphanumeric"""
    #dashes = re.compile('_|-')
    delimiter = '_'
    uppers = re.compile(r'(?<!^)(?=[A-Z])')
    nonalphanumeric = re.compile('[^0-9a-zA-Z\ _-]+')
    dashes = re.compile('\ |_|-')

    #value = dashes.sub(delimiter, value)
    value = uppers.sub(' ', value)
    value = nonalphanumeric.sub('', value)

    value = dashes.sub(' ', value)
    value = ucwords(value)
    #value = value.replace(' ', '')
    #value = uppers.sub(' ', value)
    return value


def ucwords(value: str):
    """Uppercase first letter of each word but leaves rest of the word alone (keeps existing case)"""
    words = []
    for word in value.split(' '):
        if word: words.append(word[0].upper() + word[1:])
    return ' '.join(words)


def ucfirst(value: str):
    """Uppercase first letter in sentence and leaves rest alone"""
    return value[0].upper() + value[1:]


def title(value: str):
    """Uppsercase first letter of each word and forces lowercase on the rest of the word"""
    return value.title()


def snake(value: str, delimiter: str = '_'):
    """Convert string to snake case foo_bar"""
    return slug(value, '_')


def kebab(value: str):
    """Convert string to kebab case foo-bar"""
    #return snake(value, '-')
    return slug(value, '-')


def studly(value: str):
    """Convert string to studly/pascal case FooBar"""
    value = ucbreakup(value)
    return value.replace(' ', '')


def camel(value: str):
    """Convert string to camel case fooBar"""
    value = studly(value)
    #value = ucbreakup(value)
    value = value[0].lower() + value[1:]
    return value


def slug(value: str, delimiter: str = '-'):
    """Slugify a string"""
    value = ucbreakup(value)
    return value.replace(' ', delimiter).lower()


def words(value: str, length: int = 100, end: str = '...'):
    words = value.split(' ')
    if len(words) > length:
        return ' '.join(words[0:length]) + str(end)
    return value
