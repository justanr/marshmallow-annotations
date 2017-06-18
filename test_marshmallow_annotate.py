from marshmallow_annotations import AnnotatedSchema as Schema
from datetime import date
from marshmallow import fields


def test_adds_annotated_fields():
    class BookSchema(Schema):
        author: fields.String()
        title: fields.String()
        published: fields.Date()

    expected = dict(author='Anne Droid', title='Robots', published=date(3000, 1, 23))
    in_ = dict(author='Anne Droid', title='Robots', published='3000-01-23')

    assert expected == BookSchema(strict=True).load(in_).data
