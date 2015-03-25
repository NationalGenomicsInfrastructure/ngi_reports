"""
Generally useful utility methods
"""

import collections

def flatten_dict(d, parent_key="", sep="."):
    """
    Flattens a dict by concatinating the keys
    seperated by the specified separator (sep) until it finds a value.
    Optionally it adds parent_key as a prefix.
    E.g. {my : {nested: {key: value}}} -> "my.nested.key: value"
    """
    items = []
    for k, v in d.items():
        new_key = "{}{}{}".format(parent_key, sep, k) if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

