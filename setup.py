import os
import setuptools

from rfapi import __version__ as rf_version

URL = 'https://github.com/recordedfuture/rfapi-python'


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fdin:
        result = fdin.read()
    return result

setuptools.setup(
    name = 'rfapi',
    packages = ['rfapi'], # this must be the same as the name above
    version = rf_version,
    description = 'API access to the Recorded Future API.',
    long_description = read('README.rst'),
    author = 'Recorded Future, Inc.',
    author_email = ['ess@recordedfuture.com',
                    'edkrantz@recordedfuture.com'],
    license = 'Apache 2',
    url = URL,
    download_url = '%s/tarball/%s' % (URL, rf_version),
    keywords = ['API', 'Recorded Future'],
    install_requires = [
        'requests>=2.5',
        'easydict>=1.6',
        'future'
    ],
    include_package_data=True,
    package_data={
        '': ['*.rst', 'LICENSE'],
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Security'
    ],
)
