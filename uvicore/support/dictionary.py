from typing import Dict


def deep_merge(override: Dict, default: Dict, *, merge_lists: bool = False) -> Dict:
    """Deep merge a dictionary.
    Values in override will overwrite values in default
    Other non dict values like str, int, list, set will be completely overwritten and not merged.
    This pur function .copy and return a new Dict, it does not transform in place
    """
    override = override.copy()
    default = default.copy()
    def merge(override: Dict, default: Dict) -> Dict:
        for key, value in override.items():
            if isinstance(value, dict):
                # If dict, recurse into values
                node = default.setdefault(key, {})
                merge(value, node)
            elif type(value) == list and merge_lists:
                # If type is list and merge_lists == True, then extend lists
                default[key] = list(set(default[key] + value))  # Sets are unique
            else:
                # If not dict (str, int, array...) override entire value
                # This means arrays will be completely overwritten, not appended
                # Which is accurate for my needs
                default[key] = value
    merge(override, default)
    return default
