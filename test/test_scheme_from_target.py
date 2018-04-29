import typing
from uuid import UUID

from marshmallow import fields

from marshmallow_annotations.converter import BaseConverter
from marshmallow_annotations.scheme import AnnotationSchema


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

            class Defaults:
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

            class Defaults:
                name = {"default": "it wasn't there"}

    class SomeTypeThingSchemeJr(SomeTypeThingScheme):

        class Meta:
            target = SomeTypeThing

    name_field = SomeTypeThingSchemeJr._declared_fields["name"]

    assert (
        name_field.default == "it wasn't there"
    ), SomeTypeThingSchemeJr.opts.field_configs


def test_merges_configuration_with_parents():
    class SomeTypeThingScheme(AnnotationSchema):

        class Meta:

            class Defaults:
                name = {"default": "it wasn't there"}

    class SomeTypeThingSchemeJr(SomeTypeThingScheme):

        class Meta:
            target = SomeTypeThing

            class Defaults:
                id = {"default": 1}
                name = {"dump_only": True}

    name_field = SomeTypeThingSchemeJr._declared_fields['name']
    id_field = SomeTypeThingSchemeJr._declared_fields['id']

    assert name_field.default == "it wasn't there"
    assert name_field.dump_only
    assert id_field.default == 1


def test_can_use_custom_converter():

    class TattleConverter(BaseConverter):

        def convert_all(self, target, ignore=frozenset(), configs=None):  # noqa: B008
            self.called = True
            return super().convert_all(target, ignore, configs)

    class SomeTypeThingScheme(AnnotationSchema):

        class Meta:
            converter_factory = TattleConverter
            target = SomeTypeThing

    assert SomeTypeThingScheme.opts.converter.called


def test_registers_schema_as_field_for_target_type(registry):
    assert SomeTypeThing not in registry

    passed_registry = registry

    class SomeTypeThingScheme(AnnotationSchema):

        class Meta:
            target = SomeTypeThing
            converter_factory = BaseConverter
            register_as_scheme = True
            registry = passed_registry

    assert SomeTypeThing in registry


def test_uses_parent_converter_if_none_present_here():

    class TattleConverter(BaseConverter):

        def convert_all(self, target, ignore=frozenset(), configs=None):  # noqa: B008
            self.called = True
            return super().convert_all(target, ignore, configs)

    class SomeTypeThingScheme(AnnotationSchema):

        class Meta:
            converter_factory = TattleConverter
            target = SomeTypeThing

    class SomeTypeThingSchemeJr(SomeTypeThingScheme):
        pass

    assert isinstance(SomeTypeThingSchemeJr.opts.converter, TattleConverter)
    assert SomeTypeThingSchemeJr.opts.converter.called
