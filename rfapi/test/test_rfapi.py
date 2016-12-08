"""Test suite for apiclient."""
import unittest
from rfapi import apiclient


class ApiClientTest(unittest.TestCase):

    def test_missing_token(self):
        with self.assertRaises(apiclient.MissingTokenError):
            apiclient.ApiClient(auth=None)

    def test_with_token(self):
        self.assertIsNotNone(apiclient.ApiClient('dummy'))

    def test_with_https_proxy(self):
        proxies = {"https": "http://proxy.example.com:3128"}
        self.assertIsNotNone(
            apiclient.ApiClient('dummy', proxies=proxies)
        )

    def test_api_query(self):
        query = {
            "entity": {
                "type": "Company",
                "name": "Recorded Future",
                "limit": 20
            }
        }
        api = apiclient.ApiClient()
        resp = api.query(query)
        result = resp.result
        self.assertEqual(result['entities'][0], 'ME4QX')

    def test_paged_entity_query(self):
        query = {
            "type": "AttackVector",
        }
        api = apiclient.ApiClient()
        entities = api.get_entities(query, limit=100)
        for e in entities:
            self.assertEqual(e.type, "AttackVector")

    def test_get_entity(self):
        api = apiclient.ApiClient()
        entity = api.get_entity("B_FAG")
        self.assertEqual(entity['name'], "United States")

        entity = api.get_entity("INVALID_ID")
        self.assertEqual(entity, None)

    def test_paged_reference_query(self):
        query = {
            "type": "Acquisition"
        }
        api = apiclient.ApiClient()
        references = api.get_references(query, limit=10)
        for r in references:
            self.assertEqual(r.type, "Acquisition")

    def test_cluster_query(self):
        query = {
            "cluster": {
                "data_group": "IpAddress",
            },
            "output": {
                "format": "csv/splunk",
                "inline_entities": False
            }
        }
        api = apiclient.ApiClient()
        resp = api.paged_query(query, limit=30, batch_size=10)
        head = next(resp)
        self.assertIsInstance(head, list)
        for a in resp:
            self.assertIsInstance(a, dict)

    def test_metadata_query(self):
        api = apiclient.ApiClient()
        metadata = api.get_metadata()
        self.assertIsInstance(metadata, list)

    def test_status_query(self):
        api = apiclient.ApiClient()
        status = api.get_status()
        self.assertIsInstance(status, dict)

 