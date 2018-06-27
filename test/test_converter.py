import typing

from marshmallow import fields, missing

from marshmallow_annotations.converter import BaseConverter


class SomeType:
    id: int
    name: typing.Optional[str]
    points: typing.List[float]


class SomeTuple(typing.NamedTuple):
    id: int
    items: typing.Optional[int] = 0
    value: typing.Optional[int] = None


def test_convert_from_typehint(registry_):
    converter = BaseConverter(registry=registry_)

    field = converter.convert(typing.Optional[int])
    assert isinstance(field, fields.Integer)
    assert field.allow_none


def test_pulls_options_from_passed_options(registry_):
    options = {"default": "it wasn't here"}
    converter = BaseConverter(registry=registry_)

    field = converter.convert(typing.Optional[str], options)

    assert isinstance(field, fields.String)
    assert field.default == "it wasn't here"


def test_convert_all_generates_schema_fields_from_type(registry_):
    converter = BaseConverter(registry=registry_)
    generated_fields = converter.convert_all(SomeType)

    assert set(generated_fields.keys()) == {"id", "name", "points"}
    assert isinstance(generated_fields["id"], fields.Integer)
    assert isinstance(generated_fields["name"], fields.String)
    assert isinstance(generated_fields["points"], fields.List)
    assert isinstance(generated_fields["points"].container, fields.Float)


def test_convert_all_generates_field_options_from_named_configs(registry_):
    converter = BaseConverter(registry=registry_)
    named_options = {"name": {"default": "it wasn't here"}}
    generated_fields = converter.convert_all(SomeType, configs=named_options)

    assert generated_fields["name"].default == "it wasn't here"


def test_ignores_fields_passed_to_it_in_convert_all(registry_):
    converter = BaseConverter(registry=registry_)
    generated_fields = converter.convert_all(SomeType, ignore={"id", "name"})

    assert (generated_fields.keys() & {"id", "name"}) == set()
    assert set(generated_fields.keys()) == {"points"}


def test_ignores_classvar_when_generating_fields(registry_):
    class SomeOtherType(SomeType):
        frob: typing.ClassVar[int] = 0

    converter = BaseConverter(registry=registry_)
    generated_fields = converter.convert_all(SomeOtherType)

    assert "frob" not in generated_fields


def test_passes_interior_options_to_list_subtype(registry_):
    converter = BaseConverter(registry=registry_)

    opts = {"_interior": {"as_string": True}}
    field = converter.convert(typing.List[int], opts)

    assert field.container.as_string


def test_defaults_missing(registry_):
    converter = BaseConverter(registry=registry_)
    generated_fields = converter.convert_all(SomeTuple)

    assert generated_fields['id'].missing == missing
    assert generated_fields['items'].missing == 0
    assert generated_fields['value'].missing is None


def test_override_missing(registry_):
    converter = BaseConverter(registry=registry_)
    named_options = {'value': {'missing': 3}}
    generated_fields = converter.convert_all(SomeTuple, configs=named_options)

    assert generated_fields['id'].missing == missing
    assert generated_fields['items'].missing == 0
    assert generated_fields['value'].missing == 3
