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

# Get from tuple with index for 2.6.x compatibility
if sys.version_info[0] > 2:
    from past.builtins import long  # pylint: disable=redefined-builtin


def get_query_type(query):
    """Return types associated with a query."""
    for atype in _QUERY_TYPE_MAP.keys():
        if atype in query:
            return atype
    return None


_QUERY_TYPE_MAP = {
    'instance': ('instance', 'instances'),
    'reference': ('reference', 'instances'),
    'entity': ('entity', 'entities'),
    'source': ('source', 'sources'),
    'cluster': ('cluster', 'events')
}


class BaseQuery(DotAccessDict):
    """Object to represent an any RFQ."""

    pass


class ReferenceQuery(BaseQuery):
    """Object to represent a reference RFQ.

    See https://github.com/recordedfuture/api/wiki/RecordedFutureAPI#instances
    """

    def __init__(self, d=None, **kwargs):
        """Initialize class."""
        BaseQuery.__init__(self)
        self.reference = d if d else {}
        self.reference.update(**kwargs)


class EntityQuery(BaseQuery):
    """Object to represent an entity RFQ.

    See https://github.com/recordedfuture/api/wiki/RecordedFutureAPI#entities
    """

    def __init__(self, d=None, **kwargs):
        """Initialize class."""
        BaseQuery.__init__(self)
        self.entity = d if d else {}
        self.entity.update(**kwargs)


class EventQuery(BaseQuery):
    """Object to represent an event/cluster RFQ.

    See https://github.com/recordedfuture/api/wiki/RecordedFutureAPI#events
    """

    def __init__(self, d=None, **kwargs):
        """Initialize class."""
        BaseQuery.__init__(self)
        self.cluster = d if d else {}
        self.cluster.update(**kwargs)


class BaseQueryResponse(object):
    """Hold response from an RFQ."""

    def __init__(self, result, req_response):
        """Initialize class."""
        self.result = result
        self._req_response = req_response

    @property
    def returned_count(self):
        """The number of returned answers."""
        if 'X-RF-RETURNED-COUNT' in self._req_response.headers:
            return int(self._req_response.headers.get("X-RF-RETURNED-COUNT"))
        if 'counts' in self.result:  # Indicates Connect API
            return self.result['counts'].get('returned', None)
        if "result" in self.result:  # term query
            return int(self.result['result']['count'])
        return None

    @property
    def has_more_results(self):
        """True if there are more answers to the query."""
        if self.next_page_start is None:
            return False

        if self.returned_count is not None \
                and self.returned_count == self.total_count:
            return False
        return True

    @property
    def next_page_start(self):
        """Return pointer to next page."""
        # this must be string
        return self._req_response.headers.get("X-RF-NEXT-PAGE-START")

    @property
    def total_count(self):
        """Return total count of answers."""
        if 'X-RF-TOTAL-COUNT' in self._req_response.headers:
            return long(self._req_response.headers.get("X-RF-TOTAL-COUNT"))
        elif 'counts' in self.result:  # Indicates Connect API
            # force long, will be int in py3 otherwise
            if 'total' in self.result['counts']:
                return long(self.result['counts']['total'])
        elif "result" in self.result:  # term query
            return long(self.result['result']['total_count'])
        return None


class CSVQueryResponse(BaseQueryResponse):
    """Holds the query result in CSV format."""

    def csv_reader(self):
        """Return results as a CSV reader object.

        See python module csv for details.
        """
        # Get from tuple with index for 2.6.x compatibility
        if sys.version_info[0] >= 3:
            lines = StringIO(self.result)
        else:
            lines = BytesIO(self.result.encode('utf-8'))
        return csv.DictReader(lines)


class JSONQueryResponse(BaseQueryResponse):
    """Holds the result in JSON format."""
    pass


class ConnectApiResponse(JSONQueryResponse):
    """Holds the result in JSON format for connect api requests."""

    @property
    def entities(self):
        for value in self.result['data']['results']:
            dic = DotAccessDict(value)
            if 'entity' in dic:
                dic.id = dic['entity']['id']
            yield dic


class ConnectApiFileResponse(object):
    """Holds file based responses."""

    def __init__(self, response):
        self.response = response

    def iter_content(self, **kwargs):
        """Returns a generator with content."""
        return self.response.iter_content(**kwargs)

    def iter_lines(self, **kwargs):
        """Returns a generator with lines."""
        return self.response.iter_lines(**kwargs)


class ConnectApiCsvFileResponse(ConnectApiFileResponse):
    """Holds CSV file based responses."""

    @property
    def csv_reader(self):
        """Return results as a CSV reader object.

        See python module csv for details.
        """

        if sys.version_info[0] >= 3:
            # decode to bytes iterator per line
            lines = map(lambda s: s.decode('utf-8'),
                        self.response.iter_lines())
        else:
            lines = self.response.iter_lines()
        return csv.DictReader(lines)


# deprecated since version 2.0, see ChangeLog
ApiV2Response = ConnectApiResponse
ApiV2FileResponse = ConnectApiResponse
ApiV2CsvFileResponse = ConnectApiCsvFileResponse
