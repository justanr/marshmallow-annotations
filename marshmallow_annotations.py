from marshmallow.schema import SchemaMeta, Schema
from marshmallow.base import FieldABC


class AnnotatedSchemaMeta(SchemaMeta):
    @classmethod
    def get_declared_fields(mcls, klass, cls_fields, inherited_fields, dict_cls):
        fields = super().get_declared_fields(klass, cls_fields, inherited_fields, dict_cls)
        annotations = getattr(klass, '__annotations__', {})
        if annotations:
            fields.update({k: v for k, v in annotations.items() if isinstance(v, FieldABC)})
        return fields


class AnnotatedSchema(Schema, metaclass=AnnotatedSchemaMeta):
    pass
