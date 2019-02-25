.. image:: https://badge.fury.io/py/rfapi.svg
    :target: https://badge.fury.io/py/rfapi

rfapi-python
============

Python 2/3 library for using the Recorded Future API

Recorded Future’s API enables you to build analytic applications and
perform analysis which is aware of events happening around the globe
24x7. You can perform queries and receive results from the Recorded
Future Temporal Analytics™ Engine across a vast set of events, entities,
and time points spanning from the far past into the future.

We provide our users with 2 API clients in this package; the Connect API Client
and the Raw API Client, see below.

Installing
__________

To install with pip run ``pip install rfapi``

An API token is required to use the Recorded Future APIs. You can request
a Recorded Future API token by contacting `support@recordedfuture.com` or
your account representative. The easiest way to setup your program is to
save your API token inside an environment variable ``RF_TOKEN``. It is
also possible to explicitly pass a token in the api client constructor. Different
licensing models apply to the Raw API and Connect API.

Public documentation for the Raw API has been discontinued. We do provide documentation on
our `Support Portal <https://support.recordedfuture.com/hc/en-us/categories/115000803507-Raw-API>`__

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

