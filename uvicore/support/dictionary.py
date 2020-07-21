def deep_merge(source, destination):
    """Deep merge a dictionary.  Other non dict values like
    str, int, list, set will be completely overwritten and not merged
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # If dict, recurse into values
            node = destination.setdefault(key, {})
            deep_merge(value, node)
        else:
            # If not dict (str, int, array...) override entire value
            # This means arrays will be completely overwritten, not appended
            # Which is accurate for my needs
            destination[key] = value
    return destination
