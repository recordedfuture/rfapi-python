rfapi-python
============

Python library for using the Recorded Future API

Recorded Future’s API enables you to build analytic applications and
perform analysis which is aware of events happening around the globe
24x7. You can perform queries and receive results from the Recorded
Future Temporal Analytics™ Engine across a vast set of events, entities,
and time points spanning from the far past into the future.

See the `API
documentation <https://github.com/recordedfuture/api/wiki/RecordedFutureAPI>`__
for further details and example usage.

To install with pip run ``pip install rfapi``

An API token is required to use the Recorded Future API. You can request
a Recorded Future API token by contacting support@recordedfuture.com or
your account representative. The easiest way to setup your program is to
save your api token inside an enviroment variable ``RF_TOKEN``. It is
also possible to explicitely pass a token in the constructor.

Creating a client
^^^^^^^^^^^^^^^^^

.. code:: python

    from rfapi import ApiClient
    api = ApiClient()

    # or explicitely
    api = ApiClient(auth='my_token')


.. _Examples: docs/examples.rst
    
.. _API documentation: https://github.com/recordedfuture/api/wiki/RecordedFutureAPI

