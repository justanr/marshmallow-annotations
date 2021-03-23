import sys

IS_PY36 = sys.version_info[:2] == (3, 6)

if IS_PY36:

    def _is_class_var(typehint):
        from typing import _ClassVar  # type: ignore

        try:
            return isinstance(typehint, _ClassVar)
        except TypeError:  # pragma: no branch
            return False

    def _get_base(typehint):
        return typehint.__base__


else:

    def _is_class_var(typehint):
        # follow the lead of stdlib's dataclass implementation
        from typing import ClassVar, _GenericAlias  # type: ignore

        return typehint is ClassVar or (
            type(typehint) is _GenericAlias and typehint.__origin__ is ClassVar
        )

    def _get_base(typehint):
        return typehint.__origin__
