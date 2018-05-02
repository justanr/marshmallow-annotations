import sys
import typing as t
from uuid import UUID

from marshmallow import fields

import pytest
from marshmallow_annotations.converter import BaseConverter
from marshmallow_annotations.scheme import AnnotationSchema


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


def test_autogenerates_fields(SchemeParent):

    class SomeTypeThingScheme(SchemeParent):

        class Meta:
            target = SomeTypeThing

    scheme_fields = SomeTypeThingScheme._declared_fields

    assert isinstance(scheme_fields["id"], fields.UUID)
    assert isinstance(scheme_fields["name"], fields.String)
    assert not scheme_fields["name"].required
    assert scheme_fields["name"].allow_none


def test_pulls_settings_from_meta(SchemeParent):

    class SomeTypeThingScheme(SchemeParent):

        class Meta:
            target = SomeTypeThing

            class Fields:
                name = {"default": "it wasn't there"}

    name_field = SomeTypeThingScheme._declared_fields["name"]

    assert name_field.default == "it wasn't there"


def test_doesnt_overwrite_explicitly_declared_fields(SchemeParent):

    class SomeTypeThingScheme(SchemeParent):
        id = fields.String()

        class Meta:
            target = SomeTypeThing

    id_field = SomeTypeThingScheme._declared_fields["id"]

    assert isinstance(id_field, fields.String)


def test_doesnt_overwrite_explicitly_declared_fields_from_parent(SchemeParent):

    class SomeTypeThingScheme(SchemeParent):
        id = fields.String()

    class SomeTypeThingSchemeJr(SomeTypeThingScheme):

        class Meta:
            target = SomeTypeThing

    id_field = SomeTypeThingSchemeJr._declared_fields["id"]

    assert isinstance(id_field, fields.String)


def test_pulls_configuration_from_parent(SchemeParent):

    class SomeTypeThingScheme(SchemeParent):

        class Meta:

            class Fields:
                name = {"default": "it wasn't there"}

    class SomeTypeThingSchemeJr(SomeTypeThingScheme):

        class Meta:
            target = SomeTypeThing

    name_field = SomeTypeThingSchemeJr._declared_fields["name"]

    assert (
        name_field.default == "it wasn't there"
    ), SomeTypeThingSchemeJr.opts.field_configs


def test_merges_configuration_with_parents(SchemeParent):

    class SomeTypeThingScheme(SchemeParent):

        class Meta:

            class Fields:
                name = {"default": "it wasn't there"}

    class SomeTypeThingSchemeJr(SomeTypeThingScheme):

        class Meta:
            target = SomeTypeThing

            class Fields:
                id = {"default": 1}
                name = {"dump_only": True}

    name_field = SomeTypeThingSchemeJr._declared_fields["name"]
    id_field = SomeTypeThingSchemeJr._declared_fields["id"]

    assert name_field.default == "it wasn't there"
    assert name_field.dump_only
    assert id_field.default == 1


def test_can_use_custom_converter(SchemeParent):

    class TattleConverter(BaseConverter):

        def convert_all(self, target, ignore=frozenset(), configs=None):  # noqa: B008
            self.called = True
            return super().convert_all(target, ignore, configs)

    class SomeTypeThingScheme(SchemeParent):

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


def test_uses_parent_converter_if_none_present_here(SchemeParent):

    class TattleConverter(BaseConverter):

        def convert_all(self, target, ignore=frozenset(), configs=None):  # noqa: B008
            self.called = True
            return super().convert_all(target, ignore, configs)

    class SomeTypeThingScheme(SchemeParent):

        class Meta:
            converter_factory = TattleConverter
            target = SomeTypeThing

    class SomeTypeThingSchemeJr(SomeTypeThingScheme):
        pass

    assert isinstance(SomeTypeThingSchemeJr.opts.converter, TattleConverter)
    assert SomeTypeThingSchemeJr.opts.converter.called


@pytest.mark.skipif(sys.version_info < (3, 6, 5), reason="Requires 3.6.5+")
@pytest.mark.xfail(strict=True)
def test_forward_declaration_of_scheme_target(SchemeParent):

    class SomeTypeScheme(SchemeParent):

        class Meta:
            target = SomeType

    s = SomeTypeScheme()
    result = s.dump(SomeType(id=1, children=[SomeType(id=2)]))

    expected = {"id": 1, "children": [{"id": 2, "children": []}]}
    assert not result.errors
    assert result.data == expected


def test_builds_nested_many_field_when_typehint_is_scheme(SchemeParent):

    class Album:
        name: str

    class Artist:
        name: str
        albums: t.List[Album]

    class AlbumScheme(SchemeParent):

        class Meta:
            target = Album
            register_as_scheme = True

    class ArtistScheme(SchemeParent):

        class Meta:
            target = Artist
            register_as_scheme = True

    artist_fields = ArtistScheme._declared_fields

    assert isinstance(artist_fields["albums"], fields.Nested)
    assert artist_fields["albums"].many
