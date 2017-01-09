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
import sys
import csv
from io import StringIO, BytesIO
from .datamodel import DotAccessDict
from past.builtins import long


def get_query_type(query):
    for type in _query_type_map.keys():
        if type in query:
            return type
    return None

_query_type_map = {
    'instance': ('instance', 'instances'),
    'reference': ('reference', 'instances'),
    'entity': ('entity', 'entities'),
    'source': ('source', 'sources'),
    'cluster': ('cluster', 'events')
}


class BaseQuery(DotAccessDict):
    """Object to represent an any RFQ"""
    pass


class ReferenceQuery(BaseQuery):
    """Object to represent a reference RFQ
    See https://github.com/recordedfuture/api/wiki/RecordedFutureAPI#instances
    """

    def __init__(self, d=None, **kwargs):
        BaseQuery.__init__(self)
        self.reference = d if d else {}
        self.reference.update(**kwargs)


class EntityQuery(BaseQuery):
    """Object to represent an entity RFQ
    See https://github.com/recordedfuture/api/wiki/RecordedFutureAPI#entities
    """

    def __init__(self, d=None, **kwargs):
        BaseQuery.__init__(self)
        self.entity = d if d else {}
        self.entity.update(**kwargs)


class EventQuery(BaseQuery):
    """Object to represent an event/cluster RFQ
    See https://github.com/recordedfuture/api/wiki/RecordedFutureAPI#events
    """

    def __init__(self, d=None, **kwargs):
        BaseQuery.__init__(self)
        self.cluster = d if d else {}
        self.cluster.update(**kwargs)


class BaseQueryResponse(object):
    """Hold response from an RFQ
    """

    def __init__(self, result, req_response):
        self.result = result
        self._req_response = req_response

    @property
    def returned_count(self):
        return self._req_response.headers.get("X-RF-RETURNED-COUNT")

    @property
    def has_more_results(self):
        if self.next_page_start is None:
            return False

        if self.returned_count is not None \
                and self.returned_count == self.total_count:
            return False
        return True

    @property
    def next_page_start(self):
        # this must be string
        return self._req_response.headers.get("X-RF-NEXT-PAGE-START")

    @property
    def total_count(self):
        return long(self._req_response.headers.get("X-RF-TOTAL-COUNT"))


class CSVQueryResponse(BaseQueryResponse):

    def csv_reader(self):
        if sys.version_info.major >= 3:
            lines = StringIO(self.result)
        else:
            lines = BytesIO(self.result.encode('utf-8'))
        return csv.DictReader(lines)

    @property
    def returned_count(self):
        return len(self.result.encode('utf-8').splitlines()) - 1


class JSONQueryResponse(BaseQueryResponse):
    @property
    def returned_count(self):
        """Get returned and total query hit counts"""
        if isinstance(self.result.get('count'), dict):
            for (key, obj) in self.result['count'].items():
                if isinstance(obj, dict):
                    if 'returned' in obj:
                        return obj['returned']
        return None
