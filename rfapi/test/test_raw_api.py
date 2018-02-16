"""Test suite for apiclient."""
import unittest
import sys
import platform
from rfapi import rawapiclient, __version__
from rfapi.datamodel import Event, Entity, Reference
from rfapi.query import JSONQueryResponse
from rfapi import RawApiClient

# for deprecation alias test
from rfapi import ApiClient


class ApiClientTest(unittest.TestCase):
    _multiprocess_can_split_ = True

    def test_missing_token(self):
        with self.assertRaises(rawapiclient.MissingAuthError):
            client = RawApiClient(auth=None)
            client.get_status()

    def test_with_token(self):
        self.assertIsNotNone(RawApiClient('dummy'))

    def test_with_https_proxy(self):
        proxies = {"https": "http://proxy.example.com:3128"}
        self.assertIsNotNone(
            RawApiClient('dummy', proxies=proxies)
        )

    def test_api_query(self):
        query = {
            "entity": {
                "type": "Company",
                "name": "Recorded Future",
                "limit": 20
            }
        }
        api = ApiClient()
        resp = api.query(query)
        self.assertIsInstance(resp, JSONQueryResponse)
        result = resp.result
        self.assertEqual(result['entities'][0], 'ME4QX')

    def test_paged_entity_query(self):
        query = {
            "type": "AttackVector",
        }
        api = RawApiClient()
        entities = api.get_entities(query, limit=100)
        for e in entities:
            self.assertIsInstance(e, Entity)
            self.assertEqual(e.type, "AttackVector")

    def test_get_entity(self):
        api = RawApiClient()
        entity = api.get_entity("B_FAG")
        self.assertIsInstance(entity, Entity)
        self.assertEqual(entity['name'], "United States")

        entity = api.get_entity("INVALID_ID")
        self.assertEqual(entity, None)

    def test_paged_reference_query(self):
        query = {
            "type": "Acquisition"
        }
        api = RawApiClient()
        references = api.get_references(query, limit=10)
        for r in references:
            self.assertIsInstance(r, Reference)
            self.assertEqual(r.type, "Acquisition")

    def test_enrichment_query_csv(self):
        query = {
            "cluster": {
                "data_group": "IpAddress",
            },
            "output": {
                "format": "csv/splunk",
                "inline_entities": False
            }
        }
        api = RawApiClient()
        resp = api.paged_query(query, limit=30, batch_size=10)
        head = next(resp)
        self.assertIsInstance(head, list)
        for a in resp:
            self.assertIsInstance(a, dict)

    def test_entity_query_csv(self):
        query = {
            "entity": {
                "type": "AttackVector",
            },
            "output": {
                "format": "csv"
            }
        }
        api = RawApiClient()
        resp = api.paged_query(query, limit=30, batch_size=10)
        head = next(resp)
        self.assertIsInstance(head, list)
        for a in resp:
            self.assertIsInstance(a, dict)

    def test_reference_query_csv(self):
        query = {
            "reference": {
                "type": "CyberAttack",
            },
            "output": {
                "format": "csv"
            }
        }
        api = RawApiClient()
        resp = api.paged_query(query, limit=30, batch_size=10)
        head = next(resp)
        self.assertIsInstance(head, list)
        for a in resp:
            self.assertIsInstance(a, dict)

    def test_events_query(self):
        query = {
            "type": "CyberAttack"
        }
        api = RawApiClient()
        events = api.get_events(query, limit=10)
        for e in events:
            self.assertIsInstance(e, Event)

    def test_metadata_query(self):
        api = RawApiClient()
        metadata = api.get_metadata()
        self.assertIsInstance(metadata, list)

    def test_status_query(self):
        api = RawApiClient()
        status = api.get_status(False)
        self.assertIsInstance(status, dict)

    def test_app_id(self):
        rfapi_python = 'rfapi-python/%s' % __version__

        api = RawApiClient(app_name='UnitTest')
        self.assertEqual(api._app_id, 'UnitTest (%s) %s' % (
            platform.platform(), rfapi_python))

        api = RawApiClient(app_name='UnitTest', app_version='42')
        self.assertEqual(api._app_id, 'UnitTest/42 (%s) %s' % (
            platform.platform(), rfapi_python))

        api = RawApiClient(app_name='UnitTest', app_version='42',
                           platform='SIEM_42')
        self.assertEqual(api._app_id, 'UnitTest/42 (%s) %s (%s)' % (
            platform.platform(), rfapi_python, 'SIEM_42'))

        api = RawApiClient()
        self.assertEqual(api._app_id, rfapi_python)

    def test_paging_aggregate_query_fails(self):
        with self.assertRaises(rawapiclient.InvalidRFQError):
            client = RawApiClient()
            query = {
                "instance": {
                    "type": "Acquisition",
                },
                "output": {
                    "count": {
                        "axis": [
                            "publication_year"
                        ],
                        "values": [
                            "instances"
                        ]
                    }
                }
            }
            next(client.paged_query(query))

    def test_page_xml(self):
        client = RawApiClient()
        query = {
            "cluster": {
                "data_group": "IpAddress"
            },
            "output": {
                "format": "xml/stix"
            }
        }
        limit = 30
        responses = [resp for resp in client.paged_query(query,
                                                         batch_size=10,
                                                         limit=limit)]
        n_results = sum(map(lambda r: r.returned_count, responses))
        self.assertEqual(n_results, limit)

    def test_invalid_token(self):
        with self._assertRaisesRegex(rawapiclient.AuthenticationError,
                                     "No or invalid token"):
            client = RawApiClient(auth='nosuchtoken')
            client.get_status()

    def test_invalid_query(self):
        with self._assertRaisesRegex(rawapiclient.HttpError, "No such query"):
            client = RawApiClient()
            client.query({"apa": "bepa"})

    @property
    def _assertRaisesRegex(self):
        return self.assertRaisesRegex if sys.version_info.major >= 3 else \
            self.assertRaisesRegexp
