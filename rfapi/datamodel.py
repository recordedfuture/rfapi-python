from easydict import EasyDict

class Entity(EasyDict):
    """Dict with dot access to values"""
    pass


class Reference(EasyDict):
    """Dict with dot access to values"""
    pass


class QueryResponse(object):
    def __init__(self, result, response_headers):
        self.result = result
        self._response_headers = response_headers

    @property
    def content_type(self):
        ct = self._response_headers.get("content-type")
        known = ['json', 'csv', 'json']
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


