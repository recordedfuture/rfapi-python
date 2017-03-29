"""Test suite for apiclient."""
import unittest
import sys
from rfapi import apiv1client, __version__
from rfapi.datamodel import Event, Entity, Reference
from rfapi.query import JSONQueryResponse
from rfapi import ApiClient


class ApiClientTest(unittest.TestCase):
    _multiprocess_can_split_ = True
    def test_missing_token(self):
        with self.assertRaises(apiv1client.MissingAuthError):
            client = ApiClient(auth=None)
            client.get_status()

    def test_with_token(self):
        self.assertIsNotNone(ApiClient('dummy'))

    def test_with_https_proxy(self):
        proxies = {"https": "http://proxy.example.com:3128"}
        self.assertIsNotNone(
            ApiClient('dummy', proxies=proxies)
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
        api = ApiClient()
        entities = api.get_entities(query, limit=100)
        for e in entities:
            self.assertIsInstance(e, Entity)
            self.assertEqual(e.type, "AttackVector")

    def test_get_entity(self):
        api = ApiClient()
        entity = api.get_entity("B_FAG")
        self.assertIsInstance(entity, Entity)
        self.assertEqual(entity['name'], "United States")

        entity = api.get_entity("INVALID_ID")
        self.assertEqual(entity, None)

    def test_paged_reference_query(self):
        query = {
            "type": "Acquisition"
        }
        api = ApiClient()
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
        api = ApiClient()
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
        api = ApiClient()
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
        api = ApiClient()
        resp = api.paged_query(query, limit=30, batch_size=10)
        head = next(resp)
        self.assertIsInstance(head, list)
        for a in resp:
            self.assertIsInstance(a, dict)

    def test_events_query(self):
        query = {
            "type": "CyberAttack"
        }
        api = ApiClient()
        events = api.get_events(query, limit=10)
        for e in events:
            self.assertIsInstance(e, Event)

    def test_metadata_query(self):
        api = ApiClient()
        metadata = api.get_metadata()
        self.assertIsInstance(metadata, list)

    def test_status_query(self):
        api = ApiClient()
        status = api.get_status()
        self.assertIsInstance(status, dict)

    def test_app_id(self):
        rfapi_python = 'rfapi-python/%s' % __version__

        api = ApiClient(app_name='UnitTest')
        self.assertEqual(api._app_id, 'UnitTest %s' % rfapi_python)

        api = ApiClient(app_name='UnitTest', app_version='42')
        self.assertEqual(api._app_id, 'UnitTest/42 %s' % rfapi_python)

        api = ApiClient()
        self.assertEqual(api._app_id, rfapi_python)

    def test_paging_aggregate_query_fails(self):
        with self.assertRaises(apiv1client.InvalidRFQError):
            client = ApiClient()
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
        client = ApiClient()
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
        with self._assertRaisesRegex(apiv1client.AuthenticationError, "Unknown key=nosuchtoken"):
            client = ApiClient(auth='nosuchtoken')
            client.get_status()

    def test_invalid_query(self):
        with self._assertRaisesRegex(apiv1client.HttpError, "No such query"):
            client = ApiClient()
            client.query({"apa": "bepa"})

    @property
    def _assertRaisesRegex(self):
        return self.assertRaisesRegex if sys.version_info.major >= 3 else self.assertRaisesRegexp