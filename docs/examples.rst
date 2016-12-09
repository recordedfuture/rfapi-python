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

Metadata
^^^^^^^^^

.. code:: python

    # Get dict with metadata info
    import json
    metadata = api.get_metadata()
    # get json as dict
    print(json.dumps(metadata, indent=2))

Status
^^^^^^^^^

.. code:: python

    # Get API user token usage
    import json
    status = api.get_status()
    # get json as dict
    print(json.dumps(status, indent=2))

