import typing as T
from uuid import UUID, uuid4

from marshmallow import post_load

import marshmallow_annotations as ma
import pytest


class Foo:
    bar: "Bar"
    id: UUID

    def __init__(self, bar, *, id=None):
        self.bar = bar
        self.id = id if id is not None else uuid4()


class Bar:
    foo: Foo
    id: UUID

    def __init__(self, *, id=None):
        self.id = id if id is not None else uuid4()


def test_throws_annotation_error_on_unregistered_unthunked_field(registry_):
    with pytest.raises(ma.AnnotationConversionError):

        class FooSchema(ma.AnnotationSchema):
            class Meta:
                target = Foo


def test_can_generate_schema_with_thunked_field(registry_):
    class FooSchema(ma.AnnotationSchema):
        class Meta:
            registry = registry_
            target = Foo
            register_as_scheme = True

            class Fields:
                bar = ma.thunked({"exclude": ("foo",)})

    class BarSchema(ma.AnnotationSchema):
        class Meta:
            registry = registry_
            target = Bar
            register_as_scheme = True

            class Fields:
                foo = {"exclude": ("bar",)}

    assert Foo in registry_
    assert Bar in registry_
    assert isinstance(FooSchema._declared_fields["bar"], ma.ThunkedField)


def test_can_serialize_with_thunked_field(registry_):
    foo_id = uuid4()
    bar_id = uuid4()

    class FooSchema(ma.AnnotationSchema):
        class Meta:
            registry = registry_
            target = Foo
            register_as_scheme = True

            class Fields:
                bar = ma.thunked({"exclude": ("foo",)})

    class BarSchema(ma.AnnotationSchema):
        class Meta:
            registry = registry_
            target = Bar
            register_as_scheme = True

            class Fields:
                foo = {"exclude": ("bar",)}

    serialized = FooSchema().dump(Foo(Bar(id=bar_id), id=foo_id)).data
    assert serialized["id"] == str(foo_id)
    assert serialized["bar"]["id"] == str(bar_id)


def test_can_deserialize_with_thunked_field(registry_):
    foo_id = uuid4()
    bar_id = uuid4()

    class FooSchema(ma.AnnotationSchema):
        @post_load
        def into_foo(self, data, **kwargs):
            return Foo(**data)

        class Meta:
            registry = registry_
            target = Foo
            register_as_scheme = True

            class Fields:
                bar = ma.thunked({"exclude": ("foo",)})

    class BarSchema(ma.AnnotationSchema):
        @post_load
        def into_bar(self, data, **kwargs):
            return Bar(**data)

        class Meta:
            registry = registry_
            target = Bar
            register_as_scheme = True

            class Fields:
                foo = {"exclude": ("bar",)}

    deserialized = (
        FooSchema().load({"id": str(foo_id), "bar": {"id": str(bar_id)}}).data
    )
    assert foo_id == deserialized.id
    assert bar_id == deserialized.bar.id


def test_thunked_field_throws_annotation_conversion_error_if_thunk_cannot_resolve(
    registry_,
):
    class FooSchema(ma.AnnotationSchema):
        class Meta:
            registry = registry_
            target = Foo
            register_as_scheme = True

            class Fields:
                bar = ma.thunked({"exclude": ("foo",)})

    with pytest.raises(ma.AnnotationConversionError):
        FooSchema().dump(Foo(Bar()))


@pytest.mark.regression
def test_optional_field_is_not_thunked(registry_):
    class TypeWithOptional:
        count: T.Optional[int]

    class TypeWithOptionalSchema(ma.AnnotationSchema):
        class Meta:
            registry = registry_
            target = TypeWithOptional

    assert not isinstance(
        TypeWithOptionalSchema._declared_fields["count"], ma.ThunkedField
    )


@pytest.mark.regression
def test_list_field_is_not_thunked(registry_):
    class TypeWithList:
        things: T.List[int]

    class TypeWithListSchema(ma.AnnotationSchema):
        class Meta:
            registry = registry_
            target = TypeWithList

    assert not isinstance(
        TypeWithListSchema._declared_fields["things"], ma.ThunkedField
    )
