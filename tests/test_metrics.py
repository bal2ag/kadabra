"""
    tests.metrics
    ~~~~~~~~~~~
    Definitions of basic metric classes and serialization/deserialization.

    :copyright: (c) 2016 by Alex Landau.
    :license: BSD, see LICENSE for more details.
"""

import kadabra

def get_dimension():
    return {"name": "dimensionName", "value": "dimensionValue"}

def test_dimension():
    expected = get_dimension()
    dimension = kadabra.Dimension(expected["name"], expected["value"])

    assert expected["name"] == dimension.name
    assert expected["value"] == dimension.value
    assert expected == dimension.serialize()
    
    deserialized = kadabra.Dimension.deserialize(expected)
    assert dimension.name == deserialized.name
    assert dimension.value == deserialized.value
