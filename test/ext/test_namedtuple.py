import typing

from marshmallow3_annotations.ext.namedtuple import NamedTupleSchema


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
    result = s.load({"a": 1, "b": 2, "c": 3})

    expected = SomeTuple(a=1, b=2, c=3)
    assert result == expected


def test_missing_values(registry_):
    class SomeTupleSchema(NamedTupleSchema):
        class Meta:
            registry = registry_
            target = SomeTuple

    s = SomeTupleSchema()
    result = s.load({"a": 1})

    expected = SomeTuple(a=1, b=None, c=5)
    assert result == expected


def test_dump_default_fields(registry_):
    class SomeTupleSchema(NamedTupleSchema):
        class Meta:
            registry = registry_
            target = SomeTuple
            dump_default_fields = True

    s = SomeTupleSchema()
    result = s.dump(SomeTuple(a=1, b=None, c=5))

    expected = {"a": 1, "b": None, "c": 5}
    assert result == expected


def test_no_dump_default_fields(registry_):
    class SomeTupleSchema(NamedTupleSchema):
        class Meta:
            registry = registry_
            target = SomeTuple
            dump_default_fields = False

    s = SomeTupleSchema()
    result1 = s.dump(SomeTuple(a=1, b=None, c=5))
    result2 = s.dump(SomeTuple(a=1, b=5, c=None))

    expected1 = {"a": 1}
    assert result1 == expected1

    expected2 = {"a": 1, "b": 5, "c": None}
    assert result2 == expected2
