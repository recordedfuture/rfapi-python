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
"""Python library for accessing Recorded Future, Inc. API."""

# must be specified first, is imported by RawApiClient

__version__ = '2.5.1'  # nopep8

import os

# RFQ-7231 about user agent: product/product-version
APP_ID = 'rfapi-python/%s' % __version__
DEFAULT_API_URL = 'https://api.recordedfuture.com'
RF_API_URL = os.environ.get("RF_API_URL", DEFAULT_API_URL)
RAW_API_URL = '%s/rfq/' % RF_API_URL
CONNECT_API_URL = '%s/v2/' % RF_API_URL

# export for easy access

# pylint: disable=wrong-import-position
from .auth import RFTokenAuth, \
    SignatureHashAuth  # nopep8

# pylint: disable=wrong-import-position
from .error import MissingAuthError, \
    RemoteServerError, \
    JsonParseError, \
    InvalidRFQError  # nopep8

# pylint: disable=wrong-import-position
from .datamodel import Reference, Entity, Event  # nopep8

# pylint: disable=wrong-import-position
from .query import BaseQuery, \
    ReferenceQuery, \
    EntityQuery, \
    EventQuery, \
    BaseQueryResponse, \
    CSVQueryResponse, \
    JSONQueryResponse  # nopep8

# pylint: disable=wrong-import-position
from .rawapiclient import RawApiClient  # nopep8
from .connectapiclient import ConnectApiClient  # nopep8

# Set default logging handler to avoid "No handler found" warnings.
# pylint: disable=wrong-import-order
import logging  # nopep8
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """Defines a NullHandler, ie a does-nothing handler."""

        def emit(self, record):
            """Emit a log message, does nothing per design."""
            pass

logging.getLogger(__name__).addHandler(NullHandler())

# deprecated from version 2.0, see Changelog
API_URL = RAW_API_URL
APIV2_URL = CONNECT_API_URL
ApiClient = RawApiClient
ApiV2Client = ConnectApiClient
