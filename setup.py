import setuptools
import re

from rfapi-red import __version__

URL = 'https://github.com/recordedfuture/rfapi-python'
LONG_DESCRIPTION = """rfapi-python
============

Python 2/3 library for using the Recorded Future API

Recorded Future's API enables you to build analytic applications and
perform analysis which is aware of events happening around the globe
24x7. You can perform queries and receive results from the Recorded
Future Temporal Analytics Engine across a vast set of events,
entities, and time points spanning from the far past into the future.

See `GitHub source <https://github.com/recordedfuture/rfapi-python>`__
for further details and example usage.

To install with pip run ``pip install rfapi``

..
"""

setuptools.setup(
    name = 'rfapi-red',
    packages = ['rfapi-red'], # this must be the same as the name above
    version = __version__,
    description = 'API access to the Recorded Future API.',
    long_description = LONG_DESCRIPTION,
    author = 'Recorded Future, Inc.',
    author_email = 'edkrantz@recordedfuture.com',
    license = 'Apache 2',
    url = URL,
    download_url = '%s/tarball/%s' % (URL, version),
    keywords = ['API', 'Recorded Future'],
    install_requires = [
        'requests>=2.5',
        'future'
    ],
    include_package_data=True,
    package_data={
        '': ['*.rst', 'LICENSE'],
    },
    classifiers = [
        'Development Status :: 6 - Mature',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Security'
    ],
)
