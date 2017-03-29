"""Test suite for apiclient."""
import unittest
import sys
import io
from rfapi.query import ApiV2Response
from rfapi import ApiV2Client
from rfapi.datamodel import DotAccessDict
import types

if sys.version_info[0] > 2:
    from past.builtins import long, basestring  # pylint: disable=redefined-builtin


class ApiV2ClientTest(unittest.TestCase):
    _multiprocess_can_split_ = True

    def test_domain_search(self):
        client = ApiV2Client()
        resp = client.search_domains()

        self.assertIsInstance(resp, ApiV2Response)
        self.assertIsInstance(resp.entities, types.GeneratorType)

        first_entity = next(resp.entities)
        self.assertIsInstance(first_entity, DotAccessDict)
        self.assertEquals(first_entity.id, first_entity.entity.id)
        self.assertIsInstance(resp.returned_count, int)
        self.assertIsInstance(resp.total_count, long)
        self.assertGreater(resp.returned_count, 0)

    def test_ip_riskrule(self):
        client = ApiV2Client()
        resp = client.get_ip_riskrules()

        self.assertIsInstance(resp, list)
        self.assertEquals(set(resp[0].keys()),
                          set(['name', 'description',
                               'criticality', 'criticalityLabel']))

    def test_domain_riskrule(self):
        client = ApiV2Client()
        resp = client.get_domain_riskrules()

        self.assertIsInstance(resp, list)
        self.assertEquals(set(resp[0].keys()),
                          set(['name', 'description',
                               'criticality', 'criticalityLabel']))

    def test_hash_riskrule(self):
        client = ApiV2Client()
        resp = client.get_hash_riskrules()

        self.assertIsInstance(resp, list)
        self.assertEquals(set(resp[0].keys()),
                          set(['name', 'description',
                               'criticality', 'criticalityLabel']))

    def test_vulnerability_risklist(self):
        client = ApiV2Client()
        resp = client.get_vulnerability_risklist(gzip=False)
        it = resp.iter_lines()
        header = next(it)
        self.assertIsInstance(header, basestring)
        entries = list(it)
        self.assertGreater(len(entries), 10)

    def test_vulnerability_risklist_gzip(self):
        """download gzip and write to a byte buffer"""
        client = ApiV2Client()
        resp = client.get_vulnerability_risklist(gzip=True)
        buf = io.BytesIO()
        for it in resp.iter_content(chunk_size=1024):
            buf.write(it)
        buf.seek(0)
        self.assertGreater(len(buf.read()), 1000)
        buf.close()


    def test_vulnerability_riskrule(self):
        client = ApiV2Client()
        resp = client.get_vulnerability_riskrules()

        self.assertIsInstance(resp, list)
        self.assertEquals(set(resp[0].keys()),
                          set(['name', 'description',
                               'criticality', 'criticalityLabel']))

    def test_get_search(self):
        client = ApiV2Client()
        resp = client.search("ip", **dict(risk_score="(91,100]"))
        self.assertIsInstance(resp, ApiV2Response)

    def test_get_ip(self):
        client = ApiV2Client()
        resp = client.lookup_ip("8.8.8.8")
        self.assertIsInstance(resp, DotAccessDict)

    def test_get_extension(self):
        client = ApiV2Client()
        info = client.get_extension_info("vulnerability", "CVE-2014-0160", "shodan")
        self.assertIsInstance(info, DotAccessDict)

    def test_vulnerabilty_extension(self):
        client = ApiV2Client()
        info = client.get_vulnerability_extension("CVE-2014-0160", "shodan")
        self.assertIsInstance(info, DotAccessDict)
