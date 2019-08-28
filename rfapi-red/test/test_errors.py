import unittest
from rfapi.error import JsonParseError, MissingAuthError


class ApiClientTest(unittest.TestCase):
    def test_json_parse_error(self):
        resp = type('', (object,), {"content": ""})()
        msg = "Could not parse"
        e = JsonParseError(msg, resp)
        self.assertEqual(str(e), msg)

    def test_missing_auth_error(self):
        e = MissingAuthError()
        self.assertTrue("API" in str(e))
