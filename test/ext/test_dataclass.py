from typing import Optional

import marshmallow as ma
import pytest
from marshmallow_annotations.exceptions import AnnotationConversionError

try:
    from marshmallow_annotations.ext.dataclass import (
        DataclassSchema,
        initvar_typehint,
        validator,
    )
    import dataclasses
except ImportError:
    pytestmarker = pytest.mark.skip("dataclasses not installed")


def int_factory() -> int:
    return 1


@dataclasses.dataclass
class SomeClass:
    # required field
    a: int
    # required load only field
    b: dataclasses.InitVar[int] = dataclasses.field(metadata=initvar_typehint(int))

    # non-required, missing is marshmallow.missing
    # also, it's okay mypy, we got this
    c: int = dataclasses.field(default_factory=int_factory)
    # dump only field
    d: int = dataclasses.field(default=1, init=False)
    # non-required, missing is None
    e: Optional[int] = None


def test_properly_converts_dataclass_to_schema(registry_):
    class SomeClassSchema(DataclassSchema):
        class Meta:
            registry = registry_
            target = SomeClass

    s = SomeClassSchema()

    result = s.load({"a": 1, "b": 5})

    expected = SomeClass(a=1, b=2)  # type: ignore
    assert not result.errors
    assert result.data == expected


def test_no_dump_initvar_fields(registry_):
    class SomeClassSchema(DataclassSchema):
        class Meta:
            registry = registry_
            target = SomeClass

    s = SomeClassSchema()
    result = s.dump(SomeClass(a=99, b=55))  # type: ignore

    expected = {"a": 99, "c": 1, "d": 1, "e": None}
    assert not result.errors
    assert result.data == expected


def test_cant_convert_non_dataclass_subclass(registry_):
    class SomeSubclass(SomeClass):
        x: int

    with pytest.raises(KeyError) as excinfo:

        class SomeSubclassSchema(DataclassSchema):
            class Meta:
                registry = registry_
                target = SomeSubclass

    assert "x" in str(excinfo.value)


def test_can_convert_dataclass_subclass(registry_):
    @dataclasses.dataclass
    class SomeSubclass(SomeClass):
        x: int = 500

    class SomeSubClassSchema(DataclassSchema):
        class Meta:
            registry = registry_
            target = SomeSubclass

    s = SomeSubClassSchema()

    result = s.dump(SomeSubclass(a=99, b=55))  # type: ignore

    expected = {"a": 99, "c": 1, "d": 1, "e": None, "x": 500}
    assert not result.errors
    assert result.data == expected
