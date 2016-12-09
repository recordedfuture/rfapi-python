# Copyright 2016 Recorded Future, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Classes for queries."""
from rfapi.datamodel import DotAccessDict


class BaseQuery(DotAccessDict):
    pass


class ReferenceQuery(BaseQuery):
    def __init__(self, d=None, **kwargs):
        BaseQuery.__init__(self)
        self.reference = d if d else {}
        self.reference.update(**kwargs)


class EntityQuery(BaseQuery):
    def __init__(self, d=None, **kwargs):
        BaseQuery.__init__(self)
        self.entity = d if d else {}
        self.entity.update(**kwargs)


class EventQuery(BaseQuery):
    def __init__(self, d=None, **kwargs):
        BaseQuery.__init__(self)
        self.cluster = d if d else {}
        self.cluster.update(**kwargs)


class QueryResponse(object):
    """Response class"""
    def __init__(self, result, response_headers):
        self.result = result
        self._response_headers = response_headers

    @property
    def content_type(self):
        cnt = self._response_headers.get("content-type")
        known = ['json', 'csv', 'xml']
        for k in known:
            if k in cnt:
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
