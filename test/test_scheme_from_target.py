# type: ignore
import sys
import typing as t
from uuid import UUID

from marshmallow import fields

import pytest
from marshmallow3_annotations.converter import BaseConverter
from marshmallow3_annotations.scheme import AnnotationSchema


class SomeTypeThing:
    id: UUID
    name: t.Optional[str]


class SomeType:
    children: t.List["SomeType"]
    id: int

    def __init__(self, id, children=None):
        self.id = id
        if children is None:
            children = []
        self.children = children


def test_autogenerates_fields(registry_):
    class SomeTypeThingScheme(AnnotationSchema):
        class Meta:
            registry = registry_
            target = SomeTypeThing
            registry = registry_

    scheme_fields = SomeTypeThingScheme._declared_fields

    assert isinstance(scheme_fields["id"], fields.UUID)
    assert isinstance(scheme_fields["name"], fields.String)
    assert not scheme_fields["name"].required
    assert scheme_fields["name"].allow_none


def test_pulls_settings_from_meta(registry_):
    class SomeTypeThingScheme(AnnotationSchema):
        class Meta:
            registry = registry_
            target = SomeTypeThing
            registry = registry_

            class Fields:
                name = {"default": "it wasn't there"}

    name_field = SomeTypeThingScheme._declared_fields["name"]

    assert name_field.default == "it wasn't there"


def test_doesnt_overwrite_explicitly_declared_fields(registry_):
    class SomeTypeThingScheme(AnnotationSchema):
        id = fields.String()

        class Meta:
            registry = registry_
            target = SomeTypeThing

    id_field = SomeTypeThingScheme._declared_fields["id"]

    assert isinstance(id_field, fields.String)


def test_doesnt_overwrite_explicitly_declared_fields_from_parent(registry_):
    class SomeTypeThingScheme(AnnotationSchema):
        id = fields.String()

    class SomeTypeThingSchemeJr(SomeTypeThingScheme):
        class Meta:
            registry = registry_
            target = SomeTypeThing

    id_field = SomeTypeThingSchemeJr._declared_fields["id"]

    assert isinstance(id_field, fields.String)


def test_pulls_configuration_from_parent(registry_):
    class SomeTypeThingScheme(AnnotationSchema):
        class Meta:
            registry = registry_

            class Fields:
                name = {"default": "it wasn't there"}

    class SomeTypeThingSchemeJr(SomeTypeThingScheme):
        class Meta:
            registry = registry_
            target = SomeTypeThing

    name_field = SomeTypeThingSchemeJr._declared_fields["name"]

    assert (
        name_field.default == "it wasn't there"
    ), SomeTypeThingSchemeJr.opts.field_configs


def test_merges_configuration_with_parents(registry_):
    class SomeTypeThingScheme(AnnotationSchema):
        class Meta:
            registry = registry_

            class Fields:
                name = {"default": "it wasn't there"}

    class SomeTypeThingSchemeJr(SomeTypeThingScheme):
        class Meta:
            registry = registry_

            target = SomeTypeThing

            class Fields:
                id = {"default": 1}
                name = {"dump_only": True}

    name_field = SomeTypeThingSchemeJr._declared_fields["name"]
    id_field = SomeTypeThingSchemeJr._declared_fields["id"]

    assert name_field.default == "it wasn't there"
    assert name_field.dump_only
    assert id_field.default == 1


def test_can_use_custom_converter(registry_):
    class TattleConverter(BaseConverter):
        def convert_all(self, target, ignore=frozenset(), configs=None):  # noqa: B008
            self.called = True
            return super().convert_all(target, ignore, configs)

    class SomeTypeThingScheme(AnnotationSchema):
        class Meta:
            registry = registry_

            converter_factory = TattleConverter
            target = SomeTypeThing

    assert SomeTypeThingScheme.opts.converter.called


def test_registers_schema_as_field_for_target_type(registry_):
    assert SomeTypeThing not in registry_

    class SomeTypeThingScheme(AnnotationSchema):
        class Meta:
            registry = registry_
            target = SomeTypeThing
            converter_factory = BaseConverter
            register_as_scheme = True

    assert SomeTypeThing in registry_


def test_uses_parent_converter_if_none_present_here(registry_):
    class TattleConverter(BaseConverter):
        def convert_all(self, target, ignore=frozenset(), configs=None):  # noqa: B008
            self.called = True
            return super().convert_all(target, ignore, configs)

    class SomeTypeThingScheme(AnnotationSchema):
        class Meta:
            registry = registry_

            converter_factory = TattleConverter
            target = SomeTypeThing

    class SomeTypeThingSchemeJr(SomeTypeThingScheme):
        pass

    assert isinstance(SomeTypeThingSchemeJr.opts.converter, TattleConverter)
    assert SomeTypeThingSchemeJr.opts.converter.called


@pytest.mark.skipif(sys.version_info < (3, 6, 5), reason="Requires 3.6.5+")
def test_forward_declaration_of_scheme_target(registry_):
    class SomeTypeScheme(AnnotationSchema):
        class Meta:
            registry = registry_
            target = SomeType
            register_as_scheme = True

    s = SomeTypeScheme()
    result = s.dump(SomeType(id=1, children=[SomeType(id=2)]))

    expected = {"id": 1, "children": [{"id": 2, "children": []}]}
    assert result == expected


def test_builds_nested_many_field_when_typehint_is_scheme(registry_):
    class Album:
        name: str

    class Artist:
        name: str
        albums: t.List[Album]

    class AlbumScheme(AnnotationSchema):
        class Meta:
            registry = registry_

            target = Album
            register_as_scheme = True

    class ArtistScheme(AnnotationSchema):
        class Meta:
            registry = registry_

            target = Artist
            register_as_scheme = True

    artist_fields = ArtistScheme._declared_fields

    assert isinstance(artist_fields["albums"], fields.Nested)
    assert artist_fields["albums"].many


def test_excludes_fields_declared_in_exclude(registry_):
    class SomeTypeThingScheme(AnnotationSchema):
        class Meta:

            registry = registry_
            target = SomeTypeThing
            exclude = ("id",)

    assert "id" not in SomeTypeThingScheme._declared_fields
