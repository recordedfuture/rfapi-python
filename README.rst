.. image:: https://badge.fury.io/py/rfapi.svg
    :target: https://badge.fury.io/py/rfapi

rfapi-python
============

Python 2/3 library for using the Recorded Future Connect API

Recorded Future’s Connect API enables partners and clients to access
Recorded Future threat intelligence programmatically via a simple to use,
information rich RESTful API. In particular, the Connect API makes it easy
to access a wealth of context and risk related information on several
canonical cybersecurity entities, including IP addresses, domains, URLs,
file hashes, and vulnerabilities.

Note that using the rfapi package is NOT a prerequisite for utilizing
the Recorded Future Connect API, and many partners and clients have
created powerful integrations working directly with API calls provided
through the `API Explorer <https://api.recordedfuture.com/v2/>. `
Also, developers with an existing login to the Recorded Future portal
can also access a comprehensive set of documentation on the Connect API via
this users-only `support site <https://support.recordedfuture.com/hc/en-us/categories/115000153607-Connect-API>`.

Installing
__________

To install with pip run ``pip install rfapi``

An API token is required to use the Recorded Future API. You can request
a Recorded Future API token by contacting `support@recordedfuture.com` or
your account representative. The easiest way to setup your program is to
save your API token inside an environment variable ``RF_TOKEN``. It is
also possible to explicitly pass a token in the api client constructor.


Examples for Connect API
________________________

The Connect API client provides a façade for our simplified Connect API.
See the `Connect API Explorer <https://api.recordedfuture.com/v2/>`__.

Creating a ConnectApiClient
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from rfapi import ConnectApiClient
    api = ConnectApiClient()

    # or explicitly
    api = ConnectApiClient(auth='my_token')

