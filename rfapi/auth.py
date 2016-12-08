import requests
import os


class RFTokenAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = self._find_token() if token == 'auto' else token

    def __call__(self, r):
        # If we still haven't a token we need to bail.
        if not self.token:
            raise MissingTokenError
        r.headers['Authorization'] = "RF-TOKEN token=%s" % self.token
        return r

    @staticmethod
    def _find_token():
        if 'RECFUT_TOKEN' in os.environ:
            return os.environ['RECFUT_TOKEN']
        if 'RF_TOKEN' in os.environ:
            return os.environ['RF_TOKEN']
        return None


class MissingTokenError(Exception):
    """No token was supplied."""

    def __str__(self):
        """Format the error message."""
        return 'no Recorded Future API key was provided.'
