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
    def __init__(self, token):
        self.token = self._find_token() if token == 'auto' else token

    def __call__(self, req):
        # If we still haven't a token we need to bail.
        if not self.token:
            raise MissingAuthError
        req.headers['Authorization'] = "RF-TOKEN token=%s" % self.token
        return req

    @staticmethod
    def _find_token():
        if 'RF_TOKEN' in os.environ:
            return os.environ['RF_TOKEN']
        if 'RECFUT_TOKEN' in os.environ:
            return os.environ['RECFUT_TOKEN']
        return None


class SignatureHashAuth(requests.auth.AuthBase):
    """Authenticate using signed queries."""
    def __init__(self, username, userkey):
        self.username = username
        self.userkey = userkey

    def __call__(self, req):
        # pylint: disable=no-member
        timestamp = email.Utils.formatdate()
        split = req.path_url.split("?")
        path_params = split[1] if len(split) > 1 else ""
        hash_text = "?" + path_params + req.body + timestamp
        hmac_hash = hmac.new(self.userkey,
                             hash_text,
                             hashlib.sha256).hexdigest()
        req.headers['Date'] = timestamp
        req.headers['Authorization'] = 'RF-HS256 user=%s, hash=%s' % (
            self.username, hmac_hash
        )
        return req
