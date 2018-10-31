import setuptools
import re

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

# resolve version by opening file. We cannot do import duing install
# since the package does not yet exist
with open('rfapi/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setuptools.setup(
    name = 'rfapi',
    packages = ['rfapi'], # this must be the same as the name above
    version = version,
    description = 'API access to the Recorded Future API.',
    long_description = LONG_DESCRIPTION,
    author = 'Recorded Future, Inc.',
    author_email = ['ess@recordedfuture.com',
                    'edkrantz@recordedfuture.com'],
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
