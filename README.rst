rfapi-python
============

Python 2/3 library for using the Recorded Future API

Recorded Future’s API enables you to build analytic applications and
perform analysis which is aware of events happening around the globe
24x7. You can perform queries and receive results from the Recorded
Future Temporal Analytics™ Engine across a vast set of events, entities,
and time points spanning from the far past into the future.

See the `API
documentation <https://github.com/recordedfuture/api/wiki/RecordedFutureAPI>`__
for further details and example usage.

Installing
__________

To install with pip run ``pip install rfapi``

An API token is required to use the Recorded Future API. You can request
a Recorded Future API token by contacting support@recordedfuture.com or
your account representative. The easiest way to setup your program is to
save your API token inside an environment variable ``RF_TOKEN``. It is
also possible to explicitly pass a token in the constructor.

Examples
________

Creating a client
^^^^^^^^^^^^^^^^^

.. code:: python

    from rfapi import ApiClient
    api = ApiClient()

    # or explicitly
    api = ApiClient(auth='my_token')


Entity
^^^^^^

If you know the id of an entity, here's how to retrieve the
information about it:

.. code:: python

    entity = api.get_entity("ME4QX") # Find the Recorded Future Entity
    print(entity.name) # prints Recorded Future

Entities
^^^^^^^^

Searching for entities is done using ``get_entities``. The first
mandatory argument corresponds to the ``entity`` section of API call (see
the documentation for `Entities
<https://github.com/recordedfuture/api/wiki/RecordedFutureAPI#entity-query-example>`__
in the API documentation).

.. code:: python

    # create a generator of entities
    entities = api.get_entities({
        "type": "Company"
    }, limit=20)
    for e in entities:
        print(e.name) # prints company names

References
^^^^^^^^^^

Searching for references is done using ``get_references``. The first
mandatory argument corresponds to the ``instance`` section of API call (see
the documentation for `References (aka Instances)
<https://github.com/recordedfuture/api/wiki/RecordedFutureAPI#instance-query-example>`__
in the API documentation).

.. code:: python

    # create a generator of references
    references = api.get_references({
        "type": "CyberAttack"
    }, limit=20)
    for r in references:
        print(r.fragment) # prints event fragments


Events
^^^^^^^^^^

Searching for events is done using ``get_events``. The first
mandatory argument corresponds to the ``cluster`` section of API call (see
the documentation for `Events (aka Clusters)
<https://github.com/recordedfuture/api/wiki/RecordedFutureAPI#events>`__
in the API documentation).

.. code:: python

    # create a generator of events
    events = api.get_events({
        "type": "CyberAttack"
    }, limit=20)
    for e in events:
        print(e.id) # prints event id


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

    print(json.dumps(query_response.result, indent=2))

Metadata
^^^^^^^^^

.. code:: python

    # Get dict with metadata info
    import json
    metadata = api.get_metadata()

    print(json.dumps(metadata, indent=2))

Status
^^^^^^^^^

.. code:: python

    # Get API user token usage
    import json
    status = api.get_status()
    # get json as dict
    print(json.dumps(status, indent=2))

