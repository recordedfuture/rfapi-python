"""Test suite for apiclient."""
import unittest
import sys
import io
import types
import requests
from rfapi.query import ConnectApiResponse
from rfapi import ConnectApiClient
from rfapi.datamodel import DotAccessDict
from . import IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG

if sys.version_info[0] > 2:
    # pylint: disable=redefined-builtin
    from past.builtins import long, basestring


# pylint: disable=too-many-public-methods
class ConnectApiClientTest(unittest.TestCase):
    _multiprocess_can_split_ = True

    expected_riskrule_keys = set(['name', 'description', 'count',
                                  'criticality', 'criticalityLabel'])

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_domain_search(self):
        client = ConnectApiClient()
        resp = client.search_domains()

        self.assertIsInstance(resp, ConnectApiResponse)
        self.assertIsInstance(resp.entities, types.GeneratorType)

        first_entity = next(resp.entities)
        self.assertIsInstance(first_entity, DotAccessDict)
        self.assertEquals(first_entity.id, first_entity.entity.id)
        self.assertIsInstance(resp.returned_count, int)
        self.assertIsInstance(resp.total_count, long)
        self.assertGreater(resp.returned_count, 0)

    def check_list(self, resp):
        self.assertIsInstance(resp, list)
        keys = set(resp[0].keys())
        for e in self.expected_riskrule_keys:
            self.assertIn(e, keys, "Evidence should contain the key=%s" % e)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_ip_riskrule(self):
        client = ConnectApiClient()
        resp = client.get_ip_riskrules()
        self.check_list(resp)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_domain_riskrule(self):
        client = ConnectApiClient()
        resp = client.get_domain_riskrules()
        self.check_list(resp)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_hash_riskrule(self):
        client = ConnectApiClient()
        resp = client.get_hash_riskrules()
        self.check_list(resp)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_vuln_risklist(self):
        client = ConnectApiClient()
        resp = client.get_vulnerability_risklist(gzip=False)
        itr = resp.iter_lines()
        header = next(itr)
        self.assertIsInstance(header, basestring)
        entries = list(itr)
        self.assertGreater(len(entries), 10)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_vuln_risklist_gzip(self):
        """download gzip and write to a byte buffer"""
        client = ConnectApiClient()
        resp = client.get_vulnerability_risklist(gzip=True)
        buf = io.BytesIO()
        for itr in resp.iter_content(chunk_size=1024):
            buf.write(itr)
        buf.seek(0)
        self.assertGreater(len(buf.read()), 1000)
        buf.close()

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_vuln_riskrule(self):
        client = ConnectApiClient()
        resp = client.get_vulnerability_riskrules()
        self.check_list(resp)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_get_search(self):
        client = ConnectApiClient()
        resp = client.search("ip", **dict(risk_score="(91,100]",
                                          direction='desc'))
        self.assertIsInstance(resp, ConnectApiResponse)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_get_ip(self):
        client = ConnectApiClient()
        resp = client.lookup_ip("8.8.8.8")
        self.assertIsInstance(resp, DotAccessDict)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_get_extension(self):
        client = ConnectApiClient()
        info = client.get_extension_info("vulnerability", "CVE-2014-0160",
                                         "shodan")
        self.assertIsInstance(info, DotAccessDict)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_vulnerabilty_extension(self):
        client = ConnectApiClient()
        info = client.get_vulnerability_extension("CVE-2014-0160", "shodan")
        self.assertIsInstance(info, DotAccessDict)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_ip_demoevents(self):
        client = ConnectApiClient()
        res = client.get_ip_demoevents(limit=1)
        # pylint: disable=anomalous-backslash-in-string
        pattern = '.+ \[127.0.0.1\] \[localhost\]: ' \
                  'NetScreen device_id=netscreen2  ' \
                  '\[Root\]system-notification-00257\(traffic\): ' \
                  'start_time=".+" duration=0 policy_id=320001 ' \
                  'service=msrpc Endpoint Mapper\(tcp\) proto=6 src ' \
                  'zone=office dst zone=internet action=Permit sent=0 ' \
                  'rcvd=16384 dst=.+ src=.+'
        self.assertRegexpMatches(res.text, pattern)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_domain_demoevents(self):
        client = ConnectApiClient()
        res = client.get_domain_demoevents(limit=1)
        # pylint: disable=anomalous-backslash-in-string
        pattern = '.+\s+\d+ .+ TCP_MISS/.+GET http://\S+/\S+ - DIRECT/.*'
        self.assertRegexpMatches(res.text, pattern)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_hash_demoevents(self):
        client = ConnectApiClient()
        res = client.get_hash_demoevents(limit=1)
        pattern = '.+ Application hash: [0-9a-f]+, .+'
        self.assertRegexpMatches(res.text, pattern)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_url_demoevents(self):
        client = ConnectApiClient()
        res = client.get_url_demoevents(limit=1)
        # pylint: disable=anomalous-backslash-in-string
        pattern = '.+\s+\d+ .+ TCP_MISS/.+GET https?://\S+/\S* - DIRECT/.*'
        self.assertRegexpMatches(res.text, pattern)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_vuln_demoevents(self):
        client = ConnectApiClient()
        res = client.get_vulnerability_demoevents(limit=1)
        self.assertEquals(res.text[:20], u'{"_scan_result_info"')

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_url_risklist(self):
        client = ConnectApiClient()
        resp = client.get_url_risklist(gzip=False)
        itr = resp.iter_lines()
        header = next(itr)
        self.assertIsInstance(header, basestring)
        entries = list(itr)
        self.assertGreater(len(entries), 10)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_url_risklist_gzip(self):
        """download gzip and write to a byte buffer"""
        client = ConnectApiClient()
        resp = client.get_url_risklist(gzip=True)
        buf = io.BytesIO()
        for itr in resp.iter_content(chunk_size=1024):
            buf.write(itr)
        buf.seek(0)
        self.assertGreater(len(buf.read()), 1000)
        buf.close()

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_get_url(self):
        client = ConnectApiClient()
        url = 'https://sites.google.com/site/unblockingnotice/'
        resp = client.lookup_url(url)
        self.assertIsInstance(resp, DotAccessDict)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_get_hash_extension(self):
        client = ConnectApiClient()
        hash_val = '21232f297a57a5a743894a0e4a801fc3'
        info = client.get_hash_extension(hash_val, 'active_reversinglabs')
        self.assertIsInstance(info, DotAccessDict)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_get_malware(self):
        client = ConnectApiClient()
        resp = client.lookup_malware('KoneQR')
        self.assertIsInstance(resp, DotAccessDict)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_head_fusion_file(self):
        client = ConnectApiClient()
        info = client.head_fusion_file("/public/default_ip_risklist.csv")
        self.assertIsInstance(info, requests.structures.CaseInsensitiveDict)

    @unittest.skipUnless(IS_DEFAULT_API_URL, IS_DEFAULT_API_URL_MSG)
    def test_get_fusion_file(self):
        client = ConnectApiClient()
        info = client.get_fusion_file("/public/default_ip_risklist.csv")
        self.assertIsInstance(info, requests.models.Response)
        self.assertGreater(len(info.content), 0)
