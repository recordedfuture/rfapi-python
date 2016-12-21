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
"""Python library for accessing Recorded Future, Inc. API"""

# must be specified first, is imported by ApiClient
__version__ = '1.0.0'  # nopep8
APP_ID = 'rfapi-python-' + __version__  # nopep8
API_URL = 'https://api.recordedfuture.com/query/'  # nopep8

# export for easy access
from .apiclient import ApiClient  # pylint: disable=wrong-import-position
