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
"""Helper classes for extracting data from recursive dicts."""


def dot_index(index, data):
    """Internal method for indexing dicts by dot-notation.

    Args:
        index: a string with the dot-index key.
        data: a dict with the index.

    Returns:
        A list with the result.

    Example:
    >>> data  = {'apa': {'bepa': {'cepa': 'depa'}}}
    >>> list(dot_index('apa', data))
    [('bepa', {'cepa': 'depa'})]
    >>> list(dot_index('apa.bepa.cepa', data))
    ['depa']
    """
    if index:
        for key in index.split('.'):
            if isinstance(data, list):
                data = [x[key] for x in data]
            else:
                data = data[key]
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.items()
    else:
        return [data]
