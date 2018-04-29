from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Set, Tuple, Union

from marshmallow.base import FieldABC, SchemaABC

Options = Dict[str, Any]


class AbstractConverter(ABC):

    @abstractmethod
    def convert(self, typehint: type, **k: Options) -> FieldABC:
        pass

    @abstractmethod
    def convert_with_options(
        self, name: str, typehint: type, kwargs: Options
    ) -> FieldABC:
        pass

    @abstractmethod
    def convert_all(
        self, target: type, ignore: Set[str] = frozenset([])
    ) -> Dict[str, FieldABC]:
        pass


FieldConstructor = Callable[[AbstractConverter, Tuple[type], Dict[str, Any]], FieldABC]


class TypeRegistry(ABC):

    @abstractmethod
    def register(self, target: type, constructor: FieldConstructor) -> None:
        pass

    @abstractmethod
    def field_constructor(self, type: type) -> FieldConstructor:
        pass

    @abstractmethod
    def get(self, type: type) -> FieldConstructor:
        pass

    @abstractmethod
    def register_field_for_type(self, type: type, field: FieldABC) -> None:
        pass

    @abstractmethod
    def register_scheme_constructor(
        self, type: type, scheme_or_name: Union[str, SchemaABC]
    ):
        pass
