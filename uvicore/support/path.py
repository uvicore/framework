import os

def find_base(file):
    """Finds app base path relative to some __file__ in the app"""
    count = 0
    path=os.path.dirname(os.path.realpath(file))
    while count < 50:
        if (
            os.path.exists(os.path.realpath(path + '/uvicore')) or
            os.path.exists(os.path.realpath(path + '/setup.py')) or
            os.path.exists(os.path.realpath(path + '/.env'))
        ):
            return os.path.realpath(path)
        else:
            path = os.path.realpath(path + '/../')
        count += 1
    exit("Could not find base path")
