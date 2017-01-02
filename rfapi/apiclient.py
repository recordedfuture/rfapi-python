"""Client library for the Recorded Future API.
"""
import copy
import logging
import requests

# pylint: disable=redefined-builtin,redefined-variable-type
from past.builtins import basestring
from future.utils import raise_from

from .auth import RFTokenAuth
from .datamodel import Entity, \
    Reference, \
    Event, \
    DotAccessDict

from .query import JSONQueryResponse, \
    CSVQueryResponse, \
    BaseQueryResponse, \
    BaseQuery, \
    ReferenceQuery, \
    EntityQuery, \
    EventQuery, \
    get_query_type

from .error import RemoteServerError, \
    UnknownQueryTypeError, \
    JsonParseError, \
    MissingAuthError

from .dotindex import dot_index
from . import APP_ID, API_URL

LOG = logging.getLogger(__name__)

# connection and read timeouts in seconds
DEFAULT_TIMEOUT = (30, 120)

# authentication method
DEFAULT_AUTH = 'auto'


class ApiClient(object):
    """Provides simplified access to the Recorded Future API.

    The api object will handle authentication and encapsulation of
    a query.

    Ex:
    >>> api = ApiClient()
    >>> query = EntityQuery(type="Company", name="Recorded Future")
    >>> result = api.query(query)
    >>> type(result)
    <class 'rfapi.query.QueryResponse'>
    >>> result.content_type
    'json'
    """

    def __init__(self,
                 auth=DEFAULT_AUTH,
                 url=API_URL,
                 proxies=None,
                 timeout=DEFAULT_TIMEOUT):
        """Initialize API.

        Args:
            auth: If a token (string) is provided it will be used,
                otherwise the environment variables RF_TOKEN (or legacy
                RECFUT_TOKEN) are expected.
                Also accepts a requests.auth.AuthBase object
            url: Recorded Future API url
            proxies: Same format as used by requests.
            timeout: connection and read timeout used by the requests lib.

        See http://docs.python-requests.org/en/master/user/advanced/#proxies
        for more information about proxies.

        Raises:
           MissingTokenError if no token was provided.
        """
        self._url = url
        self._proxies = proxies
        self._timeout = timeout

        # set auth method if any. we defer checking auth mehtod until quering
        self._auth = None
        if isinstance(auth, requests.auth.AuthBase):
            self._auth = auth
        elif isinstance(auth, basestring):
            self._auth = RFTokenAuth(auth)

    def query(self, query, params=None):
        """Perform a standard query.

        Args:
            query: a dict containing the query.
            params: a dict with additional parameters for the API request.

        Returns:
            QueryResponse object
        """
        query = copy.deepcopy(query)

        # defer checking auth until we actually query.
        if not self._auth:
            raise MissingAuthError()

        if params is None:
            params = {}
        else:
            params = copy.deepcopy(params)
        params['app_id'] = APP_ID
        query['comment'] = APP_ID

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
                                     timeout=self._timeout)
            response.raise_for_status()
        except requests.HTTPError as err:
            msg = "Exception occured during query: %s. Error was: %s"
            LOG.exception(msg, query, err.response.content)
            raise err
        except Exception as err:
            LOG.exception("Exception occured during query: %s.", query)
            raise err

        if "output" in query \
           and query['output'].get("format", "json") != "json":
            if 'csv' in response.headers.get('content-type', ''):
                return CSVQueryResponse(response.text, response)
            else:
                return BaseQueryResponse(response.text, response)
        else:
            try:
                resp = response.json()
            except ValueError as e:
                err = JsonParseError(str(e), resp.content)
                raise_from(err, e)

            if resp.get('status', '') == 'FAILURE':
                raise RemoteServerError(("Server failure:\nQuery was '{0}'\n"
                                         "HTTP Status: {1}\t"
                                         "Message: {2}").format(
                                             query,
                                             resp.get('code', None),
                                             resp.get('error', 'NONE')))

            return JSONQueryResponse(resp, response)

    # pylint: disable=too-many-arguments,too-many-locals,too-many-branches
    def paged_query(self,
                    query,
                    limit=None,
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
        query_type = get_query_type(query)
        if not query_type:
            msg = 'Unknown query type {}. Unable to page query.'
            raise UnknownQueryTypeError(msg.format(query_type))

        if limit is None:
            query[query_type]['limit'] = batch_size
        else:
            query[query_type]['limit'] = min(batch_size, limit)

        seen = set()
        n_results = 0
        while True:
            query_response = self.query(query)

            if isinstance(query_response, JSONQueryResponse):
                if field is None:
                    yield query_response.result
                else:
                    tmp = dot_index(field, query_response.result)
                    for item in tmp:
                        if unique:
                            if item in seen:
                                continue
                            seen.add(item)
                        n_results += 1
                        yield item
                        if limit is not None and n_results >= limit:
                            # ok, we are done
                            return
            elif isinstance(query_response, CSVQueryResponse):
                csv_reader = query_response.csv_reader()
                if n_results == 0:
                    yield csv_reader.fieldnames
                next(csv_reader)  # skip header
                for row in csv_reader:
                    n_results += 1
                    yield row
                    if limit is not None and n_results >= limit:
                        # ok we are done
                        return
            else:
                # Bad support for paging, just return plain response
                yield query_response
                return

            if not query_response.has_more_results:
                break

            query[query_type]["page_start"] = query_response.next_page_start

    def get_references(self, query, limit=20):
        """Fetch references (aka instances).

        Args:
          query: the 'instance' part of an RF API query.
          limit: limit number of references in response.
          Set to None for no limit

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

    def get_events(self, query, limit=20):
        """Fetch events.

        Args:
          query: the 'cluster' part of an RF API query.
          limit: limit number of events in response. Set to None for no limit

        Returns:
          An iterator of Events.

        Ex:
        >>> api = ApiClient()
        >>> type(next(api.get_events({"type": "CyberAttack"}, limit=20)))
        <class 'rfapi.datamodel.Event'>
        """
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
        resp = self.query(BaseQuery({
            "status": {},
            "output": {
                "statistics": True
            }
        }))
        return DotAccessDict(resp.result)

    def get_metadata(self):
        """Get metadata of types and events"""
        resp = self.query(BaseQuery(metadata=dict()))
        # pylint: disable=no-member
        return DotAccessDict(resp.result).types
