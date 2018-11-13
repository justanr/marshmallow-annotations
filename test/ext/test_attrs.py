import marshmallow as ma
import pytest
from marshmallow_annotations.exceptions import AnnotationConversionError
from typing import List

try:
    from marshmallow_annotations.ext.attrs import AttrsSchema
    import attr
except ImportError:
    pytestmarker = pytest.skip("attrs not installed")


def int_factory() -> int:
    return 1


@attr.s(auto_attribs=True)
class SomeClass:
    a: int = attr.ib()
    # non-required, missing is marshmallow.missing
    # also, it's okay mypy, we got this
    b: int = attr.ib(factory=int_factory)  # type: ignore
    # dump only field
    c: int = attr.ib(default=1, init=False)
    # non-required, missing is 1
    d: int = attr.ib(default=1)
    # Include metadata
    e: str = attr.ib(default="", metadata={"hi": "world"})
    # container of non-attrs class
    f: List[int] = attr.ib(default=[])


def test_properly_converts_attrs_class_to_schema(registry_):
    class SomeClassSchema(AttrsSchema):
        class Meta:
            registry = registry_
            target = SomeClass

    s = SomeClassSchema()

    result = s.load({"a": 1})

    # mypy thinks we're missing arguments for some reason
    expected = SomeClass(a=1)  # type: ignore
    assert not result.errors
    assert result.data == expected


def test_dumps_all_attributes(registry_):
    class SomeClassSchema(AttrsSchema):
        class Meta:
            registry = registry_
            target = SomeClass

    s = SomeClassSchema()
    result = s.dump(SomeClass(a=99))  # type: ignore

    expected = {"a": 99, "b": 1, "c": 1, "d": 1, "e": "", "f": []}
    assert not result.errors
    assert result.data == expected


def test_cant_convert_non_attrs_subclass(registry_):
    class SomeSubclass(SomeClass):
        x: int

    with pytest.raises(AnnotationConversionError) as excinfo:

        class SomeSubclassSchema(AttrsSchema):
            class Meta:
                registry = registry_
                target = SomeSubclass

    assert "x" in str(excinfo.value)


def test_metadata_included(registry_):
    class SomeClassSchema(AttrsSchema):
        class Meta:
            registry = registry_
            target = SomeClass

    s = SomeClassSchema()
    assert s.fields["e"].metadata.keys() == {"hi"}
    assert s.fields["e"].metadata["hi"] == "world"
