"""Random utility functions."""

def search(data: dict, term: str, parent=None):
    """Recursively search a dictionary for a substring value
    and return all paths from the top-level dictionary that have
    matching values. Good for locating a value within a big dictionary.
    """
    result = []
    parent = parent if parent is not None else []
    if isinstance(data, dict):
        for key, value in data.items():
            par = copy.deepcopy(parent)
            par.append(key)
            depth = search(value, term, par)
            if depth:
                result.append(depth)
    elif isinstance(data, (list, tuple)):
        for i, item in enumerate(data):
            par = copy.deepcopy(parent)
            par.append(i)
            depth = search(item, term, par)
            if depth:
                result.append(depth)
    else:
        if term in str(data).lower():
            return parent, data
    return result
