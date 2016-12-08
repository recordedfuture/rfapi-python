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
also possible to explicitely pass a token to the constructor using
``ApiClient(auth='my_token')``

Creating a client
^^^^^^^^^^^^^^^^^

.. code:: python

    from rfapi import ApiClient
    api = ApiClient()

Entity
^^^^^^

.. code:: python

    entity = api.get_entity("ME4QX") # Find the Recorded Future Entity
    print(entity.name) # prints Recorded Future

Entities
^^^^^^^^

.. code:: python

    # create a generator of entities
    entities = api.get_entities({
        "type": "Company"
    }, limit=20)
    for e in entities:
        print(e.name) # prints company names

References
^^^^^^^^^^

.. code:: python

    # create a generator of references
    references = api.get_references({
        "type": "CyberAttack"
    }, limit=20)
    for r in references:
        print(r.fragment) # prints company names

Raw query
^^^^^^^^^

.. code:: python

    # Get QueryResponse object
    import json
    query_response = api.query({
        "references": {
            "type": "CyberAttack",
            "limit": 20
        }
    })
    # get json as dict
    print(json.dumps(query_response.result, indent=2))
