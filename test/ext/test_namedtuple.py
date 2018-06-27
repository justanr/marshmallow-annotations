import typing

from marshmallow_annotations.ext.namedtuple import NamedTupleSchema


class SomeTuple(typing.NamedTuple):
    a: int
    b: typing.Optional[int]
    c: typing.Optional[int] = 5


def test_instance_conversion(registry_):
    class SomeTupleSchema(NamedTupleSchema):
        class Meta:
            registry = registry_
            target = SomeTuple

    s = SomeTupleSchema()
    result = s.load({'a': 1, 'b': 2, 'c': 3})

    expected = SomeTuple(a=1, b=2, c=3)
    assert not result.errors
    assert result.data == expected


def test_missing_values(registry_):
    class SomeTupleSchema(NamedTupleSchema):
        class Meta:
            registry = registry_
            target = SomeTuple

    s = SomeTupleSchema()
    result = s.load({'a': 1})

    expected = SomeTuple(a=1, b=None, c=5)
    assert not result.errors
    assert result.data == expected


def test_missing_not_overrides(registry_):
    class SomeTupleSchema(NamedTupleSchema):
        class Meta:
            registry = registry_
            target = SomeTuple

    s = SomeTupleSchema()
    result = s.load({'a': 1, 'c': None})

    expected = SomeTuple(a=1, b=None, c=None)
    assert not result.errors
    assert result.data == expected


def test_missing_required(registry_):
    class SomeTupleSchema(NamedTupleSchema):
        class Meta:
            registry = registry_
            target = SomeTuple

    s = SomeTupleSchema()
    result = s.load({})

    assert result.errors


def test_remove_none_serialization(registry_):
    class SomeTupleSchema(NamedTupleSchema):
        class Meta:
            registry = registry_
            target = SomeTuple

    s = SomeTupleSchema()
    result = s.dump(SomeTuple(a=1, b=None, c=None))

    expected = {'a': 1, 'c': None}
    assert not result.errors
    assert result.data == expected


def test_remove_default_serialize(registry_):
    class SomeTupleSchema(NamedTupleSchema):
        class Meta:
            registry = registry_
            target = SomeTuple

    s = SomeTupleSchema()
    result = s.dump(SomeTuple(a=1, b=3, c=5))

    expected = {'a': 1, 'b': 3}
    assert not result.errors
    assert result.data == expected
