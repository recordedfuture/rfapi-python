"""Test suite for apiclient."""
import unittest
import sys
import io
from rfapi.query import ConnectApiResponse
from rfapi import ConnectApiClient
from rfapi.datamodel import DotAccessDict
import types

if sys.version_info[0] > 2:
    # pylint: disable=redefined-builtin
    from past.builtins import long, basestring


class ConnectApiClientTest(unittest.TestCase):
    _multiprocess_can_split_ = True

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

    def test_ip_riskrule(self):
        client = ConnectApiClient()
        resp = client.get_ip_riskrules()

        self.assertIsInstance(resp, list)
        self.assertEquals(set(resp[0].keys()),
                          set(['name', 'description', 'count',
                               'criticality', 'criticalityLabel']))

    @unittest.skip
    def test_domain_riskrule(self):
        client = ConnectApiClient()
        resp = client.get_domain_riskrules()

        self.assertIsInstance(resp, list)
        self.assertEquals(set(resp[0].keys()),
                          set(['name', 'description', 'count',
                               'criticality', 'criticalityLabel']))

    def test_hash_riskrule(self):
        client = ConnectApiClient()
        resp = client.get_hash_riskrules()

        self.assertIsInstance(resp, list)
        self.assertEquals(set(resp[0].keys()),
                          set(['name', 'description', 'count',
                               'criticality', 'criticalityLabel']))

    def test_vulnerability_risklist(self):
        client = ConnectApiClient()
        resp = client.get_vulnerability_risklist(gzip=False)
        it = resp.iter_lines()
        header = next(it)
        self.assertIsInstance(header, basestring)
        entries = list(it)
        self.assertGreater(len(entries), 10)

    def test_vulnerability_risklist_gzip(self):
        """download gzip and write to a byte buffer"""
        client = ConnectApiClient()
        resp = client.get_vulnerability_risklist(gzip=True)
        buf = io.BytesIO()
        for it in resp.iter_content(chunk_size=1024):
            buf.write(it)
        buf.seek(0)
        self.assertGreater(len(buf.read()), 1000)
        buf.close()

    def test_vulnerability_riskrule(self):
        client = ConnectApiClient()
        resp = client.get_vulnerability_riskrules()

        self.assertIsInstance(resp, list)
        self.assertEquals(set(resp[0].keys()),
                          set(['name', 'description', 'count',
                               'criticality', 'criticalityLabel']))

    def test_get_search(self):
        client = ConnectApiClient()
        resp = client.search("ip", **dict(risk_score="(91,100]", direction='desc'))
        self.assertIsInstance(resp, ConnectApiResponse)

    def test_get_ip(self):
        client = ConnectApiClient()
        resp = client.lookup_ip("8.8.8.8")
        self.assertIsInstance(resp, DotAccessDict)

    @unittest.skip
    def test_get_extension(self):
        client = ConnectApiClient()
        info = client.get_extension_info("vulnerability", "CVE-2014-0160",
                                         "shodan")
        self.assertIsInstance(info, DotAccessDict)

    @unittest.skip
    def test_vulnerabilty_extension(self):
        client = ConnectApiClient()
        info = client.get_vulnerability_extension("CVE-2014-0160", "shodan")
        self.assertIsInstance(info, DotAccessDict)

    def test_ip_demoevents(self):
        client = ConnectApiClient()
        res = client.get_ip_demoevents(limit=1)
        pattern = '.+ \[127.0.0.1\] \[localhost\]: ' \
                  'NetScreen device_id=netscreen2  ' \
                  '\[Root\]system-notification-00257\(traffic\): ' \
                  'start_time=".+" duration=0 policy_id=320001 ' \
                  'service=msrpc Endpoint Mapper\(tcp\) proto=6 src ' \
                  'zone=office dst zone=internet action=Permit sent=0 ' \
                  'rcvd=16384 dst=.+ src=.+'
        self.assertRegexpMatches(res.text, pattern)

    def test_domain_demoevents(self):
        client = ConnectApiClient()
        res = client.get_domain_demoevents(limit=1)
        pattern = '.+\s+\d+ .+ TCP_MISS/.+GET http://\S+/\S+ - DIRECT/.*'
        self.assertRegexpMatches(res.text, pattern)

    def test_hash_demoevents(self):
        client = ConnectApiClient()
        res = client.get_hash_demoevents(limit=1)
        pattern = '.+ Application hash: [0-9a-f]+, .+'
        self.assertRegexpMatches(res.text, pattern)
