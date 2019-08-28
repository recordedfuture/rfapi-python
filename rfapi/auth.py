# Copyright 2016 Recorded Future, Inc.
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
"""Auth provider for RF tokens stored in environment."""
import os
import email
import hashlib
import hmac
import requests
from .error import MissingAuthError


# pylint: disable=too-few-public-methods
class RFTokenAuth(requests.auth.AuthBase):
    """Authenticate using a token stored in an environment variable.

    The class will look for tokens in RF_TOKEN and RECFUT_TOKEN (legacy).
    """

    def __init__(self, token, api_version=1):
        """Initialize the class. Provide a valid token."""
        self.token = self._find_token() if token == 'auto' else token
        self._api_version = api_version

    def __call__(self, req):
        """Add the authentication header when class is called."""
        # If we still haven't a token we need to bail.
        if not self.token:
            raise MissingAuthError
        if self._api_version == 1:
            req.headers['Authorization'] = "RF-TOKEN token=%s" % self.token
        else:
            req.headers['X-RFToken'] = self.token
        return req

    @staticmethod
    def _find_token():
        if 'RF_TOKEN' in os.environ:
            return os.environ['RF_TOKEN']
        if 'RECFUT_TOKEN' in os.environ:
            return os.environ['RECFUT_TOKEN']
        raise MissingAuthError('Auth method auto selected but no token '
                               'found in environment (RF_TOKEN or '
                               'RECFUT_TOKEN).')


class SignatureHashAuth(requests.auth.AuthBase):
    """Authenticate using signed queries."""

    def __init__(self, username, userkey):
        """Initialize. Provide a valid username and key."""
        self.username = username
        self.userkey = userkey

    def __call__(self, req):
        """Add the auth headers to a request."""
        # pylint: disable=no-member
        timestamp = email.Utils.formatdate()
        split = req.path_url.split("?")
        path_params = split[1] if len(split) > 1 else ""
        body = req.body if req.body else ""

        if "v2" in req.path_url:
            v2_url = req.path_url.replace("/rfq", "")
            hash_text = v2_url + body + timestamp
        else:
            hash_text = "?" + path_params + body + timestamp

        hmac_hash = hmac.new(self.userkey,
                             hash_text,
                             hashlib.sha256).hexdigest()
        req.headers['Date'] = timestamp
        req.headers['Authorization'] = 'RF-HS256 user=%s, hash=%s' % (
            self.username, hmac_hash
        )
        return req
