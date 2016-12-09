"""Client library for the Recorded Future API.
"""
import copy
import logging
import requests
import csv
from past.builtins import basestring
from io import StringIO, BytesIO

from .auth import MissingTokenError, RFTokenAuth
from .datamodel import Entity, Reference, QueryResponse, DotAccessDict
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

    Example:
       api = ApiClient()
       query = {"entity": {"type": "Company", "name": "Recorded Future",
                "limit": 20}}
       result = api.query(query)
    """

    def __init__(self,
                 auth=DEFAULT_AUTH,
                 url=API_URL,
                 proxies=None):
        """Initialize API.

        Args:
            auth: If a token (string) is provided it will be used,
                otherwise the environment variables RF_TOKEN (or legacy RECFUT_TOKEN)
                are expected.
                Also accepts a requests.auth.AuthBase object
            url: Recorded Future API url
            proxies: Same format as used by requests.
                See http://docs.python-requests.org/en/master/user/advanced/#proxies

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
                'User-agent': APP_ID
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

        if "output" in query and query['output'].get("format", "json") != "json":
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
            raise UnknownQueryTypeError('Unknown query type {}. Unable to page query.'.format(query_type))

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
                for r in csv_reader:
                    n_results += 1
                    yield r
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
        for w in words:
            if w in query:
                return w
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
        >>> type(api.get_references({"type": "CyberAttack"}, limit=20).next())
        <class 'rfapi.datamodel.Reference'>
        """
        refs = self.paged_query({
            "reference": query
        }, limit=limit, field="instances")
        for r in refs:
            yield Reference(r)

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
        resp = self.query({
            "entity": {"id": entity_id}
        })
        try:
            e = Entity(resp.result['entity_details'][entity_id])
            e.id = entity_id
            return e
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
        >>> type(api.get_entities({"type": "Company"}, limit=20).next())
        <class 'rfapi.datamodel.Entity'>
        """
        entities = self.paged_query({
            "entity": query
        }, limit=limit, field="entity_details")

        for (k, v) in entities:
            e = Entity(v)
            e.id = k
            yield e

    def get_status(self):
        """Find out your token's API usage, broken down by day."""
        return DotAccessDict(self.query({
            "status": {},
            "output": {
                "statistics": True
            }
        }).result)

    def get_metadata(self):
        """Get metadata of types and events"""
        return DotAccessDict(self.query({
            "metadata": {}
        }).result).types


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
