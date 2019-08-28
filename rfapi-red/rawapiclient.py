import warnings

import requests
from requests.exceptions import ReadTimeout
import copy
import logging

from .apiclient import BaseApiClient, DEFAULT_AUTH, DEFAULT_TIMEOUT, \
    DEFAULT_RETRIES
from . import RAW_API_URL
from .dotindex import dot_index
from .datamodel import Entity, \
    Reference, \
    Event, \
    DotAccessDict
from .query import BaseQuery, \
    ReferenceQuery, \
    EntityQuery, \
    EventQuery, \
    get_query_type

from .query import JSONQueryResponse, \
    CSVQueryResponse

# pylint: disable=unused-import
from .error import RemoteServerError, InvalidRFQError

LOG = logging.getLogger(__name__)


class RawApiClient(BaseApiClient):
    """Provides simplified access to the Recorded Future API.

    The api object will handle authentication and encapsulation of
    a query.

    Ex:
    >>> api = RawApiClient()
    >>> query = EntityQuery(type="Company", name="Recorded Future")
    >>> result = api.query(query)
    >>> type(result)
    <class 'rfapi.query.JSONQueryResponse'>
    >>> int(result.total_count)
    1
    """

    def __init__(self,
                 auth=DEFAULT_AUTH,
                 url=RAW_API_URL,
                 proxies=None,
                 timeout=DEFAULT_TIMEOUT,
                 app_name=None,
                 app_version=None,
                 pkg_name=None,
                 pkg_version=None,
                 accept_gzip=True,
                 platform=None):
        """Initialize API.

        Args:
            auth: If a token (string) is provided it will be used,
                otherwise the environment variables RF_TOKEN (or legacy
                RECFUT_TOKEN) are expected.
                Also accepts a requests.auth.AuthBase object
            url: Recorded Future API url
            proxies: Same format as used by requests.
            timeout: connection and read timeout used by the requests lib.
            app_name: an app name which is added to the user-agent http
                header (ex "ExampleApp").
            app_version: an app version which is added to the user-agent http
                header (ex "1.0"). Use of this requires app_name above.
            pkg_name and pkg_version: same as above for package.
            accept_gzip: whether or not we access gzip compressed data or not
            platform: id of the platform running the script (ex Splunk_1.2.3)

        See http://docs.python-requests.org/en/master/user/advanced/#proxies
        for more information about proxies.
        """
        BaseApiClient.__init__(self, auth, url,
                               proxies, timeout,
                               app_name, app_version,
                               pkg_name, pkg_version,
                               accept_gzip,
                               platform)

    # pylint: disable=too-many-branches
    def query(self, query, params=None, tries_left=DEFAULT_RETRIES):
        """Perform a standard query.

        Args:
            query: a dict containing the query.
            params: a dict with additional parameters for the API request.
            tries_left: number of retries for read timeouts

        Returns:
            QueryResponse object
        """

        # defer checking auth until we actually query.
        self._check_auth()

        query = copy.deepcopy(query)

        params = self._prepare_params(params)
        headers = self._prepare_headers()
        response = None

        query_type = get_query_type(query)
        is_scan = (query_type in query and
                   query[query_type].get("searchtype") == "scan")
        try:
            LOG.debug("Requesting query json=%s", query)
            response = self._request_session.post(self._url,
                                                  json=query,
                                                  params=params,
                                                  headers=headers,
                                                  auth=self._auth,
                                                  proxies=self._proxies,
                                                  timeout=self._timeout)
            response.raise_for_status()

        except requests.HTTPError as req_http_err:
            if response.status_code == 502 or response.status_code == 503:
                # gateway error or service unavailable, ok to retry
                if tries_left > 0:
                    tries_left -= 1
                    msg = "Got error with status=%s. " \
                          "Retrying with tries=%s left"
                    LOG.warning(msg, response.status_code, tries_left)
                    return self.query(query,
                                      params=params,
                                      tries_left=tries_left)

            msg = "An exception occurred during the query: %s. " \
                  "Error was: %s"
            LOG.exception(msg, query, response.content)
            self._raise_http_error(response, req_http_err)

        except ReadTimeout:

            if is_scan and "page_start" in query[query_type]:
                # we will get illegal page start if we retry
                raise

            if tries_left > 0:
                LOG.exception("Read timeout during query. "
                              "Retrying. Attempts left: %s", tries_left)
                tries_left -= 1
                return self.query(query,
                                  params=params,
                                  tries_left=tries_left)
            else:
                raise

        except requests.RequestException:
            LOG.exception("Exception occurred during query: %s.", query)
            raise

        expect_json = not ("output" in query and
                           query['output'].get("format", "json") != "json")
        return self._make_response(expect_json, response)

    def _validate_json_response(self, resp):
        if resp.get('status', '') == 'FAILURE':
            msg = "Server failure:\n" \
                  "HTTP Status: {code}\t" \
                  "Message: {error}"
            code = resp.get('code', None)
            error = resp.get('error', 'NONE')
            msg = msg.format(code=code, error=error)
            raise RemoteServerError(msg)

    # pylint: disable=too-many-arguments,too-many-locals,too-many-branches
    def paged_query(self,
                    query,
                    limit=None,
                    batch_size=1000,
                    field=None,
                    unique=False,
                    raw=False):
        """Generator for paged query results.

        Args:
            query: a dict containing the query.
            limit: optional int, return a max of limit result units
            field: optional string with dot-notation for getting specific
                fields.
            batch_size: optional int
            unique: optional bool for filtering to unique values.
            raw: return raw QueryResponse object

        """
        query = copy.deepcopy(query)
        query_type = get_query_type(query)
        if not query_type:
            msg = 'Unknown query type {}. Unable to page query.'
            raise InvalidRFQError(msg.format(query_type), query)

        # Check for aggregate queries
        output = query.get('output')
        if isinstance(output, dict) and 'count' in output:
            msg = 'Aggregate query cannot be used in paging'
            raise InvalidRFQError(msg, query)

        if 'limit' in query[query_type]:
            msg = "Ignoring limit in query, use limit " \
                  "and batch_size arguments in paged queries."
            warnings.warn(msg, SyntaxWarning)

        if limit is None:
            query[query_type]['limit'] = batch_size
        else:
            query[query_type]['limit'] = min(batch_size, limit)

        seen = set()
        n_results = 0
        # pylint: disable=too-many-nested-blocks
        while True:
            query_response = self.query(query)

            if raw:
                n_results += query_response.returned_count
                yield query_response

            elif isinstance(query_response, JSONQueryResponse):
                if field is None:
                    n_results += query_response.returned_count
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

                for row in csv_reader:
                    n_results += 1
                    yield row
                    if limit is not None and n_results >= limit:
                        # ok we are done
                        return
            else:
                # XML, just return plain response
                n_results += query_response.returned_count
                yield query_response

            LOG.debug("Received %s/%s items", n_results,
                      query_response.total_count)
            if query_response.total_count <= n_results:
                return

            if not query_response.has_more_results:
                return

            if limit is not None and n_results >= limit:
                return

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
        >>> api = RawApiClient()
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
        >>> api = RawApiClient()
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
        >>> api = RawApiClient()
        >>> str(api.get_entity('ME4QX').name)
        'Recorded Future'
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
        >>> api = RawApiClient()
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

    def get_status(self, show_statistics=True):
        """Find out your token's API usage, broken down by day."""
        query = {"status": {}}
        if show_statistics:
            query["output"] = {"statistics": True}
        resp = self.query(BaseQuery(query))
        return DotAccessDict(resp.result)

    def get_metadata(self):
        """Get metadata of types and events."""
        resp = self.query(BaseQuery(metadata=dict()))
        # pylint: disable=no-member
        return DotAccessDict(resp.result).types
