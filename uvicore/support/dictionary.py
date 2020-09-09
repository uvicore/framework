def deep_merge(override, default):
    """Deep merge a dictionary.
    Values in override will overwrite values in default
    Other non dict values like str, int, list, set will be completely overwritten and not merged.
    """
    for key, value in override.items():
        if isinstance(value, dict):
            # If dict, recurse into values
            node = default.setdefault(key, {})
            deep_merge(value, node)
        else:
            # If not dict (str, int, array...) override entire value
            # This means arrays will be completely overwritten, not appended
            # Which is accurate for my needs
            default[key] = value
    return default
