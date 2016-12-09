from rfapi.datamodel import DotAccessDict


class BaseQuery(DotAccessDict):
    pass


class ReferenceQuery(BaseQuery):
    def __init__(self, d):
        BaseQuery.__init__(self)
        self.reference = d


class EntityQuery(BaseQuery):
    def __init__(self, d):
        BaseQuery.__init__(self)
        self.entity = d
