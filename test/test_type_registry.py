from ipaddress import IPv4Address

from marshmallow import Schema, fields

import pytest
from marshmallow_annotations.exceptions import AnnotationConversionError
from marshmallow_annotations.registry import (
    DefaultTypeRegistry,
    default_field_factory,
)


def test_unrecognized_type_raises_error():
    registry = DefaultTypeRegistry()

    with pytest.raises(AnnotationConversionError):
        registry.get(IPv4Address)


def test_can_register_type_to_field_factory():
    registry = DefaultTypeRegistry()
    constructor = lambda _, __, k: fields.String(**k)

    registry.register(IPv4Address, constructor)

    assert registry.get(IPv4Address) is constructor


def test_can_register_scheme_for_type():

    class SomeTypeScheme(Schema):
        pass

    class SomeType:
        pass

    registry = DefaultTypeRegistry()
    registry.register_scheme_factory(SomeType, "SomeTypeScheme")

    constructor = registry.get(SomeType)
    field = constructor(None, (), {})

    assert isinstance(field, fields.Nested)
    assert isinstance(field.schema, SomeTypeScheme)


def test_register_using_decorator():
    registry = DefaultTypeRegistry()

    @registry.field_factory(IPv4Address)
    def ipv4_field(converter, subtypes, kwargs):
        return fields.String(**kwargs)

    assert registry.get(IPv4Address) is ipv4_field


def test_register_raw_field_type():
    registry = DefaultTypeRegistry()

    registry.register_field_for_type(IPv4Address, fields.String)

    constructor = registry.get(IPv4Address)
    field = constructor(None, (), {})

    assert isinstance(field, fields.String)


def test_can_preregister_type_field_mapping():
    preregistered = {IPv4Address: default_field_factory(fields.String)}
    registry = DefaultTypeRegistry(preregistered)
    assert registry.get(IPv4Address) is preregistered[IPv4Address]
