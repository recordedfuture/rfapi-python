# Copyright 2016,2017 Recorded Future, Inc.
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
#
"""Client library for the Recorded Future Connect API."""
import os
import re
import hashlib
import shutil
from tempfile import NamedTemporaryFile
import requests
from requests.exceptions import ReadTimeout

from .apiclient import BaseApiClient, DEFAULT_AUTH, DEFAULT_TIMEOUT
from .apiclient import DEFAULT_RETRIES, LOG, requests
from . import CONNECT_API_URL
from .datamodel import DotAccessDict
from .query import ConnectApiResponse
from .query import ConnectApiFileResponse
from .query import ConnectApiCsvFileResponse
from .util import snake_to_camel_case

try:
    from builtins import str as text  # pylint: disable=unused-import
except ImportError:
    pass  # This is only used in the doctests

try:
    from urllib import quote as url_quote  # Python 2.X
except ImportError:
    from urllib.parse import quote as url_quote  # Python 3+


# pylint: disable=too-many-public-methods
class ConnectApiClient(BaseApiClient):
    """Provides simplified access to the Recorded Future Connect API.

    For more documentation see interactive the Connect API webpage
    https://api.recordedfuture.com/v2/

    The api object will handle authentication and encapsulation of
    a query.

    Ex:
    >>> api = ConnectApiClient()
    >>> type(api)
    <class 'rfapi.connectapiclient.ConnectApiClient'>
    """

    def __init__(self,  # pylint: disable=too-many-arguments
                 auth=DEFAULT_AUTH,
                 url=CONNECT_API_URL,
                 proxies=None,
                 timeout=DEFAULT_TIMEOUT,
                 app_name=None,
                 app_version=None,
                 pkg_name=None,
                 pkg_version=None,
                 platform=None,
                 accept_gzip=True,
                 verify=True):
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
            pkg_name and pkg_version: similar to the app_name etc above.
            accept_gzip: whether we accept gzip compressed results or not
            platform: id of the platform running the script (ex Splunk_1.2.3)

        See http://docs.python-requests.org/en/master/user/advanced/#proxies
        for more information about proxies.
        """
        BaseApiClient.__init__(self, auth, url, proxies, timeout,
                               app_name, app_version,
                               pkg_name, pkg_version,
                               accept_gzip,
                               platform,
                               api_version=2,
                               verify=verify)

    # pylint: disable=too-many-branches
    def _query(self,  # pylint: disable=too-many-arguments
               route,
               params=None,
               tries_left=DEFAULT_RETRIES,
               stream=False,
               raw=False):
        """Perform a standard query.

        Args:
            route: the endpoint beyond the api base, ex ip/risklist.
            params: a dict with additional parameters for the API request.
            tries_left: number of retries for read timeouts
            stream: return response as stream
            raw: returns raw response object

        Returns:
          If stream=True or raw=True:
            requests.packages.urllib3.response.HTTPResponse
          else:
            rfapi.query.BaseQueryResponse
        """
        # defer checking auth until we actually query.
        self._check_auth()
        params = self._prepare_params(params)
        headers = self._prepare_headers()
        response = None

        try:
            LOG.debug("Requesting query path_info=%s", route)
            # don't use session for streams. Might cause issues when
            # downloading many files in parallel and connections are
            # evicted from the urllib3 connection pool prematurely.
            url = self._url + route
            req = requests if stream else self._request_session
            response = req.get(url,
                               params=params,
                               headers=headers,
                               auth=self._auth,
                               proxies=self._proxies,
                               timeout=self._timeout,
                               verify=self.verify,
                               stream=stream)
            response.raise_for_status()

        except requests.HTTPError as req_http_err:
            msg = "Exception occurred during path_info: %s. Error was: %s"
            LOG.exception(msg, route, response.content)
            self._raise_http_error(response, req_http_err)

        except ReadTimeout:
            if tries_left > 0:
                LOG.exception("Read timeout during query. "
                              "Retrying. Attempts left: %s", tries_left)
                tries_left -= 1
                return self._query(route,
                                   params=params,
                                   tries_left=tries_left,
                                   stream=stream,
                                   raw=raw)
            else:
                raise

        except requests.RequestException:
            LOG.exception("Exception occurred during query: %s.", route)
            raise

        if raw or stream:
            return response

        expect_json = not ("format" in params and
                           params.get("format", "json") != "json")
        return self._make_response(expect_json, response)

    @staticmethod
    def _make_json_response(resp, response):
        return ConnectApiResponse(resp, response)

    #########################################################################
    #                 Generic
    #########################################################################

    def get_risklist(self,
                     group,
                     category=None,
                     output_format='csv/splunk',
                     gzip=False):
        """Fetch a risk list.

        Args:
            group: datatype such as ip, hash.
            category: limit content to entities matching a category/rule
            output_format: different support per category
            gzip: return a binary file or not

        Supported groups: 'ip', 'hash', 'vulnerability' or 'domain'.
        """
        params = {
            'format': output_format,
            'gzip': gzip
        }
        if category is not None:
            params['list'] = category
        response = self._query('%s/risklist' % group,
                               params=params,
                               stream=True)
        if not gzip:
            response.decode_content = True
        if output_format.startswith('csv') and gzip is False:
            return ConnectApiCsvFileResponse(response)
        elif output_format.startswith('xml') and gzip is False:
            return ConnectApiFileResponse(response)

        return response

    def save_risklist(self,  # pylint: disable=too-many-arguments
                      outfile,
                      group,
                      category=None,
                      output_format='csv/splunk',
                      gzip=False):
        """Save a risk list to a file.
        Args:
            outfile: file handler with write permission
            group: datatype such as ip, hash.
            category: limit content to entities matching a category/rule
            output_format: different support per category
            gzip: return a binary file or not

        Example:
            >> with open("iprisklist.csv", "wb") as f:
            >>     save_risklist(f, "ip")
            >> with open("iprisklist.csv.gz", "wb") as f:
            >>     save_risklist(f, "ip", gzip=True)

        Supported groups: 'ip', 'hash', 'vulnerability' or 'domain'.
        """
        resp = self.get_risklist(group, category, output_format, gzip)
        for chunk in resp.iter_content(chunk_size=1024):
            outfile.write(chunk)

    def get_riskrules(self, category):
        """Fetch a list of Risk rules.

        The category indicates which category of risk rules that should
        be fetched (ip, domain, hash or vulnerability).
        """
        res = self._query('%s/riskrules' % category)
        return [rule for rule in res.entities]

    def search(self, category, **kwargs):
        """
        Generic search function

        Args:
          category: datatype such as ip, malware, hash, ...
          kwargs:
              - fields: the fields that should be included in the response
              - metadata: whether to include metadata (boolean)
              - limit: limit the number of answers
              - offset: records from offset
              - risk_score: risk score (ex [25,50) which represents
                25 <= risk_score < 50)
              - first_seen: limit response to references in this interval
              - last_seen: limit response to references in this interval
              - list_id: Recorded Future list id
              - risk_rule: specific risk rule per category
              - order_by: indicate which field to order by
              - direction: order by asc or desc
              - comment: additional comment
        """
        route = "%s/search" % category

        params = dict((snake_to_camel_case(k), v) for (k, v) in kwargs.items()
                      if v is not None)

        if 'fields' in params and isinstance(params['fields'], list):
            params['fields'] = ",".join(params['fields'])

        if 'metadata' in params:
            assert isinstance(params['metadata'], bool)

        if 'limit' in params:
            limit = params['limit']
            assert isinstance(limit, int) or limit is None

        if 'riskScore' in params:
            assert re.match(r'[\[\(](\d+,\d+|,\d+|\d+,)[\)\]]',
                            params['riskScore'])

        if 'orderBy' in params:
            # field in rest api is `orderby`
            params["orderby"] = params.pop("orderBy")

        if 'direction' in params:
            assert params['direction'] in ['asc', 'desc']

        if 'ipRange' in params:
            # move the attribute (`range` is a python reserved keyword)
            params['range'] = params.pop('ipRange')

        if 'offset' in params:
            # move the attribute (`from` is a python reserved keyword)
            params['from'] = params.pop('offset')

        if 'listId' in params:
            # move the attribute (`list` is a python reserved keyword)
            params['list'] = params.pop('listId')

        return self._query(route, params)

    def get_entity(self, category, name, **kwargs):
        """Get information for a single entity in a category

        Args:
          category: datatype such as ip, malware, hash, ...
          name: entity name
          kwargs:
              - fields: the fields that should be included in the response
              - metadata: whether to include metadata (boolean)
              - comment: additional comment

        Returns:
          A DotAccessDict object with entity information
        """

        params = dict((snake_to_camel_case(k), v) for (k, v) in kwargs.items()
                      if v is not None)

        if 'fields' in params and isinstance(params['fields'], list):
            params['fields'] = ",".join(params['fields'])

        if 'metadata' in params:
            assert isinstance(params['metadata'], bool)

        response = self._query("%s/%s" % (category, name), params)
        return DotAccessDict(response.result)

    def get_extension_info(self, category, entity,
                           extension, metadata=None):
        """Get extension information for an entity.
        Possible extensions vary for your user, enterprise, and category.

        Args:
          category: datatype such as ip, hash, domain, ...
          entity: entity name
          extension: name of extension
          metadata (bool): whether to get metadata or not
        """
        params = dict(metadata=metadata)
        route = "%s/%s/extension/%s" % (category, entity, extension)
        response = self._query(route, params)
        return DotAccessDict(response.result).get('data')

    #########################################################################
    #                 DemoEvents
    #########################################################################

    def get_demoevents(self,
                       group,
                       limit=1000):
        """Fetch a demo events.

        Args:
            group: datatype such as ip, domain or hash.
            limit: the number of events to retrieve.

        Supported groups: 'ip', 'hash' or 'domain'.
        """
        params = {
            'limit': limit
        }
        response = self._query('%s/demoevents' % group,
                               params=params,
                               stream=True)
        return response

    def save_demoevents(self,
                        outfile,
                        group,
                        limit=1000):
        """Save demo events to a file.
        Args:
            group: datatype such as ip, hash.
            limit: the number of events to retrieve.

        Example:
            >> with open("ip-events.log", "wb") as f:
            >>     save_demoevents(f, "ip")

        Supported groups: 'ip', 'hash' or 'domain'.
        """
        resp = self.get_demoevents(group, limit)
        for chunk in resp.iter_content(chunk_size=1024):
            outfile.write(chunk)

    #########################################################################
    #                 IpAddress
    #########################################################################

    def get_ip_risklist(self,
                        category=None,
                        output_format='csv/splunk',
                        gzip=False):
        """Fetch an IP risk list.

        category: limit content to entities matching a category/rule
        output_format: the format of the returned file (ex csv/splunk)
        gzip: return the file compressed in gzip format

        >>> api = ConnectApiClient()
        >>> res = api.get_ip_risklist()
        >>> res.csv_reader.fieldnames
        ['Name', 'Risk', 'RiskString', 'EvidenceDetails']
        """
        return self.get_risklist('ip', category, output_format, gzip)

    def get_ip_riskrules(self):
        """Fetch a list of Risk rules and their properties.

        Returns a list of dicts.
        """
        return self.get_riskrules('ip')

    def search_ips(self, ip_range=None, **kwargs):
        """Search for information about matching ip numbers.

        Args:
          ip_range: Range as start-end or CIDR
          kwargs: generic search terms (see self.search`)

        Returns:
          An ConnectApiResponse object

        Ex:
        >>> api = ConnectApiClient(app_name='DocTest')
        >>> type(api.search_ips(ip_range='8.8.8.8/30'))
        <class 'rfapi.query.ConnectApiResponse'>
        """
        kwargs.update(ip_range=ip_range)
        return self.search('ip', **kwargs)

    def lookup_ip(self, ip_number, **kwargs):
        """Lookup information about the ip.

        Args:
          ip_number: ip number,
          kwargs: see possible values in `self.get_entity`

        Returns:
          Requested entity information fields wrapped in a
          DotAccessDict container.

        Ex:
        >>> api = ConnectApiClient(app_name='DocTest')
        >>> type(api.lookup_ip("8.8.8.8"))
        <class 'rfapi.datamodel.DotAccessDict'>
        """
        return self.get_entity("ip", ip_number, **kwargs)

    def get_ip_extension(self, ip_number, extension, metadata=None):
        """Get extension information for an entity.
        Possible extensions vary for your user, enterprise, and category.

        Args:
          ip_number: ip address
          extension: name of extension
          metadata (bool): whether to get metadata or not
        """
        return self.get_extension_info("ip", ip_number, extension, metadata)

    def get_ip_demoevents(self,
                          limit=1000):
        """Fetch a IP demo events.

        limit: the number of events

        >>> api = ConnectApiClient()
        >>> res = api.get_ip_demoevents()
        >>> isinstance(res.text, text)
        True
        """
        return self.get_demoevents('ip', limit)

    #########################################################################
    #                 Domain
    #########################################################################

    def get_domain_risklist(self,
                            category=None,
                            output_format='csv/splunk',
                            gzip=False):
        """Fetch an Domain risk list.

        category: limit content to entities matching a category/rule
        output_format: the format of the returned file (ex csv/splunk)
        gzip: return the file compressed in gzip format
        """
        return self.get_risklist('domain', category, output_format, gzip)

    def get_domain_riskrules(self):
        """Fetch a list of Risk rules and their properties.

        Returns a list of dicts.
        """
        return self.get_riskrules('domain')

    def search_domains(self, parent=None, **kwargs):
        """Search for information about matching domains.

        Args:
          parent: look for this domain and all matching subdomains
          kwargs: generic search terms (see self.search`)

        Returns:
          An ConnectApiResponse object

        Ex:
        >>> api = ConnectApiClient(app_name='DocTest')
        >>> type(api.search_domains(parent='recordedfuture.com'))
        <class 'rfapi.query.ConnectApiResponse'>
        """
        kwargs.update(parent=parent)
        return self.search('domain', **kwargs)

    def lookup_domain(self, domain_name, **kwargs):
        """Lookup information about the domain name.

        Args:
          domain_name: domain name,
          kwargs: see possible values in `self.get_entity`

        Returns:
          Requested entity information fields wrapped in a
          DotAccessDict container.

        Ex:
        >>> api = ConnectApiClient(app_name='DocTest')
        >>> type(api.lookup_domain('recordedfuture.com'))
        <class 'rfapi.datamodel.DotAccessDict'>
        """
        return self.get_entity("domain", domain_name, **kwargs)

    def get_domain_extension(self, domain_name, extension, metadata=None):
        """Get extension information for an entity.
        Possible extensions vary for your user, enterprise, and category.

        Args:
          domain_name: domain name
          extension: name of extension
          metadata (bool): whether to get metadata or not
        """
        return self.get_extension_info("domain", domain_name,
                                       extension, metadata)

    def get_domain_demoevents(self,
                              limit=1000):
        """Fetch a domain demo events.

        limit: the number of events

        >>> api = ConnectApiClient()
        >>> res = api.get_domain_demoevents()
        >>> isinstance(res.text, text)
        True
        """
        return self.get_demoevents('domain', limit)

    #########################################################################
    #                 Hash
    #########################################################################

    def get_hash_risklist(self,
                          category=None,
                          output_format='csv/splunk',
                          gzip=False):
        """Fetch an Hash risk list.

        category: limit content to entities matching a category/rule
        output_format: the format of the returned file (ex csv/splunk)
        gzip (bool): return the file compressed in gzip format
        """
        return self.get_risklist('hash', category, output_format, gzip)

    def get_hash_riskrules(self):
        """Fetch a list of Risk rules and their properties.

        Returns a list of dicts.
        """
        return self.get_riskrules('hash')

    def search_hashes(self, algorithm=None, **kwargs):
        """Search for information about matching domains.

        Args:
          algorithm: hash algorithm type, such as MD5
          kwargs: generic search terms (see `self.search`)

        Returns:
          An ConnectApiResponse object

        Ex:
        >>> api = ConnectApiClient(app_name='DocTest')
        >>> type(api.search_hashes(algorithm='md5'))
        <class 'rfapi.query.ConnectApiResponse'>
        """
        alg = algorithm.upper() if algorithm else algorithm
        kwargs.update(algorithm=alg)
        return self.search('hash', **kwargs)

    def lookup_hash(self, hash_value, **kwargs):
        """Lookup information about the hash.

        Args:
          hash_value: a hash,
          kwargs: see possible values in `self.get_entity`

        Returns:
          Requested entity information fields wrapped in a
          DotAccessDict container.

        Ex:
        >>> api = ConnectApiClient(app_name='DocTest')
        >>> type(api.lookup_hash("478c076749bef74eaf9bed4af917aee228620b23"))
        <class 'rfapi.datamodel.DotAccessDict'>
        """
        return self.get_entity("hash", hash_value, **kwargs)

    def get_hash_extension(self, hash_value, extension, metadata=None):
        """Get extension information for an entity.
        Possible extensions vary for your user, enterprise, and category.

        Args:
          hash_value: a hash
          extension: name of extension
          metadata (bool): whether to get metadata or not
        """
        return self.get_extension_info("hash", hash_value,
                                       extension, metadata)

    def get_hash_demoevents(self, limit=1000):
        """Fetch a hash demo events.

        limit: the number of events

        >>> api = ConnectApiClient()
        >>> res = api.get_hash_demoevents()
        >>> isinstance(res.text, text)
        True
        """
        return self.get_demoevents('hash', limit)

    #########################################################################
    #                 Malware
    #########################################################################

    def search_malwares(self, freetext=None, **kwargs):
        """Search for information about matching malware.

        Args:
          freetext: A searchterm
          kwargs: generic search terms (see `self.search`)

        Returns:
          An ConnectApiResponse object

        Ex:
        >>> api = ConnectApiClient(app_name='DocTest')
        >>> type(api.search_malwares(freetext='Red October'))
        <class 'rfapi.query.ConnectApiResponse'>
        """
        kwargs.update(freetext=freetext)
        return self.search('malware', **kwargs)

    def lookup_malware(self, malware_id, **kwargs):
        """Lookup information about the malware id.

        Args:
          malware_id: recorded future entity id of a malware,
          kwargs: see possible values in `self.get_entity`

        Returns:
          Requested entity information fields wrapped in a
          DotAccessDict container.

        Ex:
        >>> api = ConnectApiClient(app_name='DocTest')
        >>> type(api.lookup_malware('KoneQR')) # RF ID For Red October
        <class 'rfapi.datamodel.DotAccessDict'>
        """
        return self.get_entity("malware", malware_id, **kwargs)

    #########################################################################
    #                 Vulnerability
    #########################################################################

    def get_vulnerability_risklist(self,
                                   category=None,
                                   output_format='csv/splunk',
                                   gzip=False):
        """Fetch an Vulnerability risk list.

        category: limit content to entities matching a category/rule
        output_format: the format of the returned file (ex csv/splunk)
        gzip: return the file compressed in gzip format
        """
        return self.get_risklist('vulnerability', category,
                                 output_format, gzip)

    def get_vulnerability_riskrules(self):
        """Fetch a list of Risk rules and their properties.

        Returns a list of dicts.
        """
        return self.get_riskrules('vulnerability')

    def search_vulnerabilities(self, freetext=None, cvss_score=None, **kwargs):
        """Search for information about matching vulnerabilities.

        Args:
          freetext: A searchterm
          cvss_score: 0-10 according to the CVSS standard
          kwargs: generic search terms (see self.search`)

        Returns:
          An ConnectApiResponse object

        Ex:
        >>> api = ConnectApiClient(app_name='DocTest')
        >>> type(api.search_vulnerabilities(freetext='Heartbleed'))
        <class 'rfapi.query.ConnectApiResponse'>
        """
        kwargs.update(freetext=freetext, cvss_score=cvss_score)
        return self.search('vulnerability', **kwargs)

    def lookup_vulnerability(self, malware_id, **kwargs):
        """Lookup information about the vulnerability name.
        (CVE number of RF ID)

        Args:
          malware_id: vulnerability id (CVE number of RF ID)
          kwargs: see possible values in `self.get_entity`

        Returns:
          Requested entity information fields wrapped in a
          DotAccessDict container.

        Ex:
        >>> api = ConnectApiClient(app_name='DocTest')
        >>> type(api.lookup_vulnerability('CVE-2014-0160'))
        <class 'rfapi.datamodel.DotAccessDict'>
        """
        return self.get_entity("vulnerability", malware_id, **kwargs)

    def get_vulnerability_extension(self, malware_id, extension,
                                    metadata=None):
        """Get extension information for an entity.
        Possible extensions vary for your user, enterprise, and category.

        Args:
          malware_id: vulnerability id (CVE number of RF ID)
          extension: name of extension
          metadata (bool): whether to get metadata or not
        """
        return self.get_extension_info("vulnerability", malware_id,
                                       extension, metadata)

    def get_vulnerability_demoevents(self, limit=1000):
        """Fetch a vulnerability demo events.

        limit: the number of events

        >>> api = ConnectApiClient()
        >>> res = api.get_vulnerability_demoevents()
        >>> isinstance(res.text, text)
        True
        """
        return self.get_demoevents('vulnerability', limit)

    #########################################################################
    #                 URL
    #########################################################################

    def get_url_risklist(self,
                         category=None,
                         output_format='csv/splunk',
                         gzip=False):
        """Fetch an URL risk list.

        category: limit content to entities matching a category/rule
        output_format: the format of the returned file (ex csv/splunk)
        gzip: return the file compressed in gzip format
        """
        return self.get_risklist('url', category,
                                 output_format, gzip)

    def get_url_riskrules(self):
        """Fetch a list of Risk rules and their properties.

        Returns a list of dicts.
        """
        return self.get_riskrules('url')

    def search_urls(self, freetext=None, cvss_score=None, **kwargs):
        """Search for information about matching URLs.

        Args:
          freetext: A searchterm
          kwargs: generic search terms (see self.search`)

        Returns:
          An ConnectApiResponse object

        Ex:
        >>> api = ConnectApiClient(app_name='DocTest')
        >>> url = 'https://sites.google.com/site/unblockingnotice/'
        >>> type(api.search_urls(freetext=url))
        <class 'rfapi.query.ConnectApiResponse'>
        """
        kwargs.update(freetext=freetext, cvss_score=cvss_score)
        return self.search('url', **kwargs)

    def lookup_url(self, url, **kwargs):
        """Lookup information about the URL.

        Args:
          url: URL
          kwargs: see possible values in `self.get_entity`

        Returns:
          Requested entity information fields wrapped in a
          DotAccessDict container.

        Ex:
        >>> api = ConnectApiClient(app_name='DocTest')
        >>> url = 'https://sites.google.com/site/unblockingnotice/'
        >>> type(api.lookup_url(url))
        <class 'rfapi.datamodel.DotAccessDict'>
        """
        return self.get_entity("url", url_quote(url, safe=''), **kwargs)

    def get_url_extension(self, url, extension, metadata=None):
        """Get extension information for an entity.
        Possible extensions vary for your user, enterprise, and category.

        Args:
          url: URL
          extension: name of extension
          metadata (bool): whether to get metadata or not
        """
        return self.get_extension_info("url", url,
                                       extension, metadata)

    def get_url_demoevents(self, limit=1000):
        """Fetch a url demo events.

        limit: the number of events

        >>> api = ConnectApiClient()
        >>> res = api.get_url_demoevents()
        >>> isinstance(res.text, text)
        True
        """
        return self.get_demoevents('url', limit)

    #########################################################################
    #                 Alerts
    #########################################################################

    def get_alert_rule(self,
                       freetext,
                       limit=10):
        """Fetch information about an alert rule.

        freetext: Freetext search
        limit: limit the number of responses
        """
        params = {
            'freetext': freetext,
            'limit': limit
        }
        return self._query('alert/rule', params=params)

    def search_alerts(self, **kwargs):
        """Search for alerts.

        See ConnectApi for search parameters.

        Ex:
        >>> api = ConnectApiClient(app_name='DocTest')
        >>> res = api.search_alerts()
        >>> type(res)
        <class 'rfapi.query.ConnectApiResponse'>
        """
        return self.search('alert', **kwargs)

    def lookup_alert(self, alert_id):
        """Lookup an alert.

        Ex:
        api = ConnectApiClient(app_name='DocTest')
        res = api.lookup_alert(<an alert id>)
        """
        return self.get_entity('alert', alert_id)

    #########################################################################
    #                 FusionFiles
    #########################################################################

    def get_fusion_file(self, path):
        """Fetch a fusion file.

        Args:
            path: the path to the file, ex /home/example/file.csv
        """
        response = self._query('fusion/files/',
                               params={'path': path},
                               stream=True)
        return response

    def head_fusion_file(self, path):
        """Make a HEAD http requests for a fusion file.

        Args:
            path: the fusion file path

        Returns:
            the headers as a dict.
        """
        self._check_auth()
        route = 'fusion/files'
        params = self._prepare_params({'path': path})
        headers = self._prepare_headers()

        try:
            LOG.debug("Requesting query path_info=%s", route)
            # don't use session for streams. Might cause issues when
            # downloading many files in parallel and connections are
            # evicted from the urllib3 connection pool prematurely.

            url = self._url + 'fusion/files'
            response = requests.head(url,
                                     params=params,
                                     headers=headers,
                                     auth=self._auth,
                                     proxies=self._proxies,
                                     timeout=self._timeout)
            response.raise_for_status()
        except requests.HTTPError as req_http_err:
            msg = "Exception occurred during path_info: %s. Error was: %s"
            LOG.exception(msg, route, response.content)
            self._raise_http_error(response, req_http_err)

        except ReadTimeout:
            msg = "Read Timeout occured during path_info: %s."
            LOG.exception(msg, route)
            raise
        return response.headers

    def save_fusion_file(self,
                         path,
                         outfile):
        """Save a fusion file to local file.
        Args:
            path: the fusion file path
            outfile: file handler with write permission

        Example:
            >> with open("iprisklist.csv", "wb") as f:
            >>     save_risklist(f, "/home/example/file.csv")
        """
        resp = self.get_fusion_file(path)
        for chunk in resp.iter_content(chunk_size=1024):
            outfile.write(chunk)

    def sync_fusion_file(self, path, local_path, tmpdir=None, sha256sum=None):
        """Check if a fusion file differs from a local file. Update if yes.

        Comparaison is made using SHA256 hash sum.

        Args:
            path: the fusion file path
            local_path: the path to the local file
            tmpdir (optional): use a specified temporary directory
        """
        def _needs_sync(path, local_path, sha256sum):
            """Check if a sync is needed."""
            # Make a HEAD call to api about the fusion file
            headers = self.head_fusion_file(path)

            # Check the SHA256 checksum
            desired256 = headers.get('X-RF-Content-SHA256', None)
            if sha256sum is None:  # No checksum supplied, calculate it.
                try:
                    sha256 = hashlib.sha256()
                    with open(local_path, 'rb') as local_fd:
                        for block in iter(lambda: local_fd.read(65536), b''):
                            sha256.update(block)
                    actual256 = sha256.hexdigest()
                except IOError:
                    LOG.debug('Check sum could not be checked, local file '
                              'is missing.')
                    return True  # File proably missing - update
            else:
                actual256 = sha256sum
            if desired256 == actual256:
                LOG.debug('Found matching checksums - files are synced.')
                return False  # Checksum matches - no update necessary
            LOG.debug('Checksum mismatch - files are not synced.')
            LOG.debug('Local file: %s (%s)', actual256, local_path)
            LOG.debug('Api file:   %s', desired256)
            return True  # Checksum mismatch - update

        if _needs_sync(path, local_path, sha256sum):
            if tmpdir is not None:
                kwargs = {'dir': tmpdir}
                LOG.info('Sync of local file %s with fusion file %s needed. '
                         'Using tmpdir %s',
                         local_path, path, tmpdir)
            else:
                kwargs = {}
                LOG.info('Sync of local file %s with fusion file %s needed',
                         local_path, path)
            with NamedTemporaryFile(**kwargs) as out:
                self.save_fusion_file(path, out)
                os.fsync(out)
                out.seek(0)
                with open(local_path, 'w') as destobj:
                    shutil.copyfileobj(out, destobj)
            return True  # Signal that there was an update.
        else:
            LOG.debug('No sync of local file %s with fusion file %s needed',
                      local_path, path)
            return False  # Signal that there was no update.
