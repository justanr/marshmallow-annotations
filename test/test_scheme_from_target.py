import typing
from uuid import UUID

from marshmallow import fields

from marshmallow_annotations.scheme import AnnotationSchema
from marshmallow_annotations.converter import BaseConverter


class SomeTypeThing:
    id: UUID
    name: typing.Optional[str]


def test_autogenerates_fields():

    class SomeTypeThingScheme(AnnotationSchema):

        class Meta:
            target = SomeTypeThing

    scheme_fields = SomeTypeThingScheme._declared_fields

    assert isinstance(scheme_fields["id"], fields.UUID)
    assert isinstance(scheme_fields["name"], fields.String)
    assert scheme_fields["name"].required
    assert scheme_fields["name"].allow_none


def test_pulls_settings_from_meta():

    class SomeTypeThingScheme(AnnotationSchema):

        class Meta:
            target = SomeTypeThing
            name = {"default": "it wasn't there"}

    name_field = SomeTypeThingScheme._declared_fields["name"]

    assert name_field.default == "it wasn't there"


def test_doesnt_overwrite_explicitly_declared_fields():

    class SomeTypeThingScheme(AnnotationSchema):
        id = fields.String()

        class Meta:
            target = SomeTypeThing

    id_field = SomeTypeThingScheme._declared_fields["id"]

    assert isinstance(id_field, fields.String)


def test_doesnt_overwrite_explicitly_declared_fields_from_parent():

    class SomeTypeThingScheme(AnnotationSchema):
        id = fields.String()

    class SomeTypeThingSchemeJr(SomeTypeThingScheme):

        class Meta:
            target = SomeTypeThing

    id_field = SomeTypeThingSchemeJr._declared_fields["id"]

    assert isinstance(id_field, fields.String)


def test_pulls_configuration_from_parent():

    class SomeTypeThingScheme(AnnotationSchema):

        class Meta:
            name = {"default": "it wasn't there"}

    class SomeTypeThingSchemeJr(SomeTypeThingScheme):

        class Meta:
            target = SomeTypeThing

    name_field = SomeTypeThingSchemeJr._declared_fields["name"]

    assert name_field.default == "it wasn't there"


def test_can_use_custom_converter():
    class TattleConverter(BaseConverter):
        def convert_all(self, target, ignore=frozenset()):  # noqa: B008
            self.called = True
            return super().convert_all(target, ignore)

    class SomeTypeThingScheme(AnnotationSchema):
        class Meta:
            converter = TattleConverter
            target = SomeTypeThing

    assert SomeTypeThingScheme.Meta.converter.called


def test_registers_schema_as_field_for_target_type(registry):
    assert SomeTypeThing not in registry

    class SomeTypeThingScheme(AnnotationSchema):
        class Meta:
            target = SomeTypeThing
            converter = lambda scheme: BaseConverter(scheme, registry=registry)
            register_as_scheme = True

    assert SomeTypeThing in registry
