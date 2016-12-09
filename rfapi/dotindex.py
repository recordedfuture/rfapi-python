def dot_index(index, data):
    """Internal method for indexing dicts by dot-notation.

    Args:
        index: a string with the dot-index key.
        data: a dict with the index.

    Returns:
        A list with the result.

    Example:
    >>> data  = {'apa': {'bepa': {'cepa': 'depa'}}}
    >>> dot_index('apa', data)
    [{'bepa': {'cepa': 'depa'}}]
    >>> dot_index('apa.bepa.cepa', data)
    ['depa']
    """
    if index:
        for key in index.split('.'):
            if isinstance(data, list):
                data = [x[key] for x in data]
            else:
                data = data[key]
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.items()
    else:
        return [data]
