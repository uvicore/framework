import json
from uvicore.support import dictionary


def test_deep_merge():
    # Test deep_merge
    default = {
        'id': 1,
        'colors': ['red', 'blue', 'green'],
        'languages': {
            'php': {
                'usecases': ['web', 'cli'],
                'primary': 'web',
                'frameworks': {
                    'laravel': {
                        'creator': 'Taylor Otwel',
                        'url': 'laravel.com'
                    },
                    'rubyonrails': {
                        'creator': 'David Hansson',
                        'url': 'rubyonrails.org'
                    },
                    'uvicore': {
                        'creator': 'Matthew Reschke',
                        'url': 'uvicore.io',
                        'best': 'better believe it!'
                    }
                }
            },
            'python': {
                'is': 'better than php',
                'because': ['the', 'massive', 'libraries and usecases'],
            },
        },
        'other': 'stuff',
        'andmore': ['array', 'values'],
    }
    override = {
        'id': 2,
        'colors': ['black', 'blue'],
        'new': 'added',
        'languages': {
            'php': {
                'usecases': ['nothing'],
                'frameworks': {
                    'laravel': {
                        'best': 'no, use uvicore',
                        'creator': 'A Genius'
                    },
                },
            },
        },
        'other': 'not sure',
    }
    merged = dictionary.deep_merge(override, default)
    merged_json = json.dumps(merged, sort_keys=True)

    # Merged JSON dumped and sorted should look like this
    # Dictionaries are deep merged while srt, int, list, set...will
    # be completely overwritten
    # {
    #     "andmore": [
    #         "array",
    #         "values"
    #     ],
    #     "colors": [
    #         "black",
    #         "blue"
    #     ],
    #     "id": 2,
    #     "languages": {
    #         "php": {
    #             "frameworks": {
    #                 "laravel": {
    #                     "best": "no, use uvicore",
    #                     "creator": "A Genius",
    #                     "url": "laravel.com"
    #                 },
    #                 "rubyonrails": {
    #                     "creator": "David Hansson",
    #                     "url": "rubyonrails.org"
    #                 },
    #                 "uvicore": {
    #                     "best": "better believe it!",
    #                     "creator": "Matthew Reschke",
    #                     "url": "uvicore.io"
    #                 }
    #             },
    #             "primary": "web",
    #             "usecases": [
    #                 "nothing"
    #             ]
    #         },
    #         "python": {
    #             "because": [
    #                 "the",
    #                 "massive",
    #                 "libraries and usecases"
    #             ],
    #             "is": "better than php"
    #         }
    #     },
    #     "new": "added",
    #     "other": "not sure"
    # }

    assert merged_json == '{"andmore": ["array", "values"], "colors": ["black", "blue"], "id": 2, "languages": {"php": {"frameworks": {"laravel": {"best": "no, use uvicore", "creator": "A Genius", "url": "laravel.com"}, "rubyonrails": {"creator": "David Hansson", "url": "rubyonrails.org"}, "uvicore": {"best": "better believe it!", "creator": "Matthew Reschke", "url": "uvicore.io"}}, "primary": "web", "usecases": ["nothing"]}, "python": {"because": ["the", "massive", "libraries and usecases"], "is": "better than php"}}, "new": "added", "other": "not sure"}'

