class DotAccessDict(dict):
    def __init__(self, d=None, **kwargs):
        if d is None:
            d = {}
        if kwargs:
            d.update(**kwargs)
        for k, v in d.items():
            setattr(self, k, v)
        # Class attributes
        for k in self.__class__.__dict__.keys():
            if not (k.startswith('__') and k.endswith('__')):
                setattr(self, k, getattr(self, k))

    def __setattr__(self, name, value):
        if isinstance(value, (list, tuple)):
            value = [self.__class__(x)
                     if isinstance(x, dict) else x for x in value]
        elif isinstance(value, dict):
            value = DotAccessDict(value)
        dict.__setattr__(self, name, value)
        dict.__setitem__(self, name, value)


class Entity(DotAccessDict):
    """Dict with dot access to values"""
    pass


class Reference(DotAccessDict):
    """Dict with dot access to values"""
    pass


class QueryResponse(object):
    def __init__(self, result, response_headers):
        self.result = result
        self._response_headers = response_headers

    @property
    def content_type(self):
        ct = self._response_headers.get("content-type")
        known = ['json', 'csv', 'xml']
        for k in known:
            if k in ct:
                return k
        return None

    @property
    def is_json(self):
        return isinstance(self.result, dict)

    @property
    def next_page_start(self):
        if isinstance(self.result, dict):
            return self.result.get('next_page_start')
        return self._response_headers.get("X-RF-NEXT-PAGE-START")


