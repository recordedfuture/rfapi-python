"""Client library for the Recorded Future API.
"""
import copy
import logging
import csv
from io import StringIO, BytesIO
import requests
# pylint: disable=redefined-builtin,redefined-variable-type
from past.builtins import basestring

from .auth import MissingTokenError, RFTokenAuth
from .datamodel import Entity, Reference, Event, DotAccessDict
from .query import QueryResponse, BaseQuery, ReferenceQuery, EntityQuery, EventQuery
from .dotindex import dot_index
from . import __version__

LOG = logging.getLogger(__name__)
LOG.addHandler(logging.NullHandler())

APP_ID = 'rfapi-python-' + __version__
DEFAULT_TIMEOUT = 30  # seconds
API_URL = 'https://api.recordedfuture.com/query/'
DEFAULT_AUTH = 'auto'


class ApiClient(object):
    """Provides simplified access to the Recorded Future API.

    The api object will handle authentication and encapsulation of
    a query.

    Ex:
       >>> api = ApiClient()
       >>> query = EntityQuery(type="Company", name="Recorded Future")
       >>> result = api.query(query)
       <class 'rfapi.query.QueryResponse'>
    """

    def __init__(self,
                 auth=DEFAULT_AUTH,
                 url=API_URL,
                 proxies=None):
        """Initialize API.

        Args:
            auth: If a token (string) is provided it will be used,
                otherwise the environment variables RF_TOKEN (or legacy
                RECFUT_TOKEN) are expected.
                Also accepts a requests.auth.AuthBase object
            url: Recorded Future API url
            proxies: Same format as used by requests.

        See http://docs.python-requests.org/en/master/user/advanced/#proxies
        for more information about proxies.

        Raises:
           MissingTokenError if no token was provided.
        """
        self._url = url
        self._proxies = proxies
        self.logger = LOG.getChild(self.__class__.__name__)

        if isinstance(auth, requests.auth.AuthBase):
            self._auth = auth
        elif isinstance(auth, basestring):
            self._auth = RFTokenAuth(auth)
        else:
            raise MissingTokenError()

    def query(self, query, params=None, timeout=DEFAULT_TIMEOUT):
        """Perform a standard query.

        Args:
            query: a dict containing the query.
            params: a dict with additional parameters for the API request.
            timeout: connection and read timeout used by the requests lib.

        Returns:
            QueryResponse object
        """
        query = copy.deepcopy(query)

        if params is None:
            params = {}
        else:
            params = copy.deepcopy(params)
        params['rfapi_id'] = APP_ID

        try:
            LOG.debug("Requesting query json=%s", query)
            headers = {
                'User-Agent': APP_ID
            }
            response = requests.post(self._url,
                                     json=query,
                                     params=params,
                                     headers=headers,
                                     auth=self._auth,
                                     proxies=self._proxies,
                                     timeout=timeout)
            response.raise_for_status()
        except Exception as err:
            raise RemoteServerError(("Exception occurred during query:\n" +
                                     "Query was '{0}'\n" +
                                     "Exception: {1}").format(query, err))

        if "output" in query \
           and query['output'].get("format", "json") != "json":
            resp = response.text
        else:
            resp = response.json()
            if resp.get('status', '') == 'FAILURE':
                raise RemoteServerError(("Server failure:\nQuery was '{0}'\n"
                                         "HTTP Status: {1}\t"
                                         "Message: {2}").format(
                                             query,
                                             resp.get('code', None),
                                             resp.get('error', 'NONE')))

        return QueryResponse(resp, response.headers)

    # pylint: disable=too-many-arguments,too-many-locals,too-many-branches
    def paged_query(self,
                    query,
                    limit=1000,
                    batch_size=1000,
                    field=None,
                    unique=False):
        """Generator for paged query results.

        Args:
            query: a dict containing the query.
            limit: optional int, return a max of limit result units
            field: optional string with dot-notation for getting specific
                fields.
            batch_size: optional int
            unique: optional bool for filtering to unique values.

        """
        query = copy.deepcopy(query)
        query_type = self.get_query_type(query)
        if not query_type:
            raise UnknownQueryTypeError(
                'Unknown query type {}. Unable to page query.'.format(
                    query_type))

        query[query_type]['limit'] = min(batch_size, limit)

        seen = set()
        n_results = 0
        while True:
            resp = self.query(query)
            if resp.is_json:
                tmp = dot_index(field, resp.result)
                for item in tmp:
                    if unique:
                        if item in seen:
                            continue
                        seen.add(item)
                    n_results += 1
                    yield item
                    if n_results >= limit:
                        # ok, we are done
                        return
            elif resp.content_type == 'csv':
                import sys
                if sys.version_info.major >= 3:
                    lines = StringIO(resp.result)
                else:
                    lines = BytesIO(resp.result.encode('utf-8'))

                csv_reader = csv.DictReader(lines)
                if n_results == 0:
                    yield csv_reader.fieldnames
                next(csv_reader)  # skip header
                for row in csv_reader:
                    n_results += 1
                    yield row
                    if n_results >= limit:
                        # ok we are done
                        return
            else:
                # Bad support, just return plain response
                yield resp
                return

            next_page_start = resp.next_page_start
            if next_page_start is None:
                break

            query[query_type]["page_start"] = next_page_start

    @staticmethod
    def get_query_type(query):
        words = ['instance', 'reference', 'source', 'cluster', 'entity']
        for word in words:
            if word in query:
                return word
        return None

    def get_references(self, query, limit=20):
        """Fetch references (aka instances).

        Args:
          query: the 'instance' part of an RF API query.
          limit: limit number of references in response.

        Returns:
          An iterator of References.

        Ex:
        >>> api = ApiClient()
        >>> type(next(api.get_references({"type": "CyberAttack"}, limit=20)))
        <class 'rfapi.datamodel.Reference'>
        """
        ref_query = ReferenceQuery(query)
        refs = self.paged_query(ref_query, limit=limit, field="instances")
        for ref in refs:
            yield Reference(ref)

    def get_events(self, query, limit=100):
        event_query = EventQuery(query)
        events = self.paged_query(event_query, limit=limit, field="events")
        for event in events:
            yield Event(event)

    def get_entity(self, entity_id):
        """Get an entity.

        Args:
          entity_id: the unique id of the entity

        Returns:
          An entity

        Ex:
        >>> api = ApiClient()
        >>> api.get_entity('ME4QX').name
        u'Recorded Future'
        """
        resp = self.query(EntityQuery(id=entity_id))
        try:
            entity = Entity(resp.result['entity_details'][entity_id])
            entity.id = entity_id
            return entity
        except KeyError:
            return None

    def get_entities(self, query, limit=20):
        """Get a list of matching entities.

        Args:
          query: the query
          limit: on return this many matches

        Returns:
          An iterator yielding Entities.

        Ex:
        >>> api = ApiClient()
        >>> type(next(api.get_entities({"type": "Company"}, limit=20)))
        <class 'rfapi.datamodel.Entity'>
        """
        entities = self.paged_query(EntityQuery(query),
                                    limit=limit,
                                    field="entity_details")

        for (key, value) in entities:
            entity = Entity(value)
            entity.id = key
            yield entity

    def get_status(self):
        """Find out your token's API usage, broken down by day."""
        return DotAccessDict(self.query(BaseQuery({
            "status": {},
            "output": {
                "statistics": True
            }
        })).result)

    def get_metadata(self):
        """Get metadata of types and events"""
        # pylint: disable=no-member
        return DotAccessDict(
            self.query(BaseQuery(metadata=dict())).result
        ).types


class UnknownQueryTypeError(Exception):
    """The query type could not be identified."""

    def __init__(self, msg=''):
        """Setup the exception.

        Keyword arguments:
        msg: a message that will be added to the exception.
        """
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        """Format the error message."""
        return "Unable to page query. %s" % self.msg


class RemoteServerError(Exception):
    pass
