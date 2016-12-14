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
"""Data models to manipulate responses from the API."""


class DotAccessDict(dict):
    """Creates a dict/object hybrid.

    Instances of DotAccessDict behaves like dicts and objects
    at the same time. Ex d['example'] = 1 and d.example = 1 are
    equivalent.

    Ex:
    >>> example = DotAccessDict()
    >>> example.key1 = 'value1'
    >>> example['key2'] = 'value2'
    >>> example
    {'key2': 'value2', 'key1': 'value1'}
    """
    def __init__(self, d=None, **kwargs):
        dict.__init__(self)
        if d is None:
            d = {}
        if kwargs:
            d.update(**kwargs)
        for key, value in d.items():
            setattr(self, key, value)
        # Class attributes
        for key in self.__class__.__dict__.keys():
            if not (key.startswith('__') and key.endswith('__')):
                setattr(self, key, getattr(self, key))

    def __setattr__(self, name, value):
        if isinstance(value, (list, tuple)):
            value = [self.__class__(x)
                     if isinstance(x, dict) else x for x in value]
        elif isinstance(value, dict):
            value = DotAccessDict(value)
        dict.__setattr__(self, name, value)
        dict.__setitem__(self, name, value)


class Entity(DotAccessDict):
    """Dict with dot access to values"""
    pass


class Reference(DotAccessDict):
    """Dict with dot access to values"""
    pass


class Event(DotAccessDict):
    """Dict with dot access to values"""
    pass
