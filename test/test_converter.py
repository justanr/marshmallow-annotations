from marshmallow import fields
from marshmallow_annotations.converter import BaseConverter
import typing


class SomeType:
    id: int
    name: typing.Optional[str]
    points: typing.List[float]


def test_convert_from_typehint(registry, scheme):
    converter = BaseConverter(scheme, registry=registry)

    field = converter.convert(typing.Optional[int])
    assert isinstance(field, fields.Integer)
    assert field.allow_none


def test_pulls_options_from_meta(registry, scheme):
    scheme.Meta = set_meta_options(name={"default": "it wasn't here"})
    converter = BaseConverter(scheme, registry=registry)

    field = converter.convert_with_options("name", typing.Optional[str], {})

    assert isinstance(field, fields.String)
    assert field.default == "it wasn't here"


def test_convert_all_generates_schema_fields_from_type(registry, scheme):
    converter = BaseConverter(scheme, registry=registry)
    generated_fields = converter.convert_all(SomeType)

    assert set(generated_fields.keys()) == {"id", "name", "points"}
    assert isinstance(generated_fields["id"], fields.Integer)
    assert isinstance(generated_fields["name"], fields.String)
    assert isinstance(generated_fields["points"], fields.List)
    assert isinstance(generated_fields["points"].container, fields.Float)


def test_ignores_fields_passed_to_it_in_convert_all(registry, scheme):
    converter = BaseConverter(scheme, registry=registry)
    generated_fields = converter.convert_all(SomeType, ignore={"id", "name"})

    assert (generated_fields.keys() & {"id", "name"}) == set()
    assert set(generated_fields.keys()) == {"points"}


def test_ignores_classvar_when_generating_fields(registry, scheme):

    class SomeOtherType(SomeType):
        frob: typing.ClassVar[int] = 0

    converter = BaseConverter(scheme, registry=registry)
    generated_fields = converter.convert_all(SomeOtherType)

    assert "frob" not in generated_fields


def set_meta_options(**kwargs):
    return type("Meta", (object,), kwargs)
