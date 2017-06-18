====================
marshmallow-annotations
====================

.. code-block:: python

        from marshmallow_annotations import AnnotatedSchema
        from marshmallow import fields

        class BookSchema(AnnotatedSchema):
            author: fields.String()
            title: fields.String()
            published: fields.Date()

        book = dict(author='Anne Droid', title='Robots', published='3000-01-23')
        BookSchema().dump(book).data
        # {
        #     'author': 'Anne Droid',
        #     'title': 'Robots',
        #     'published': date(3000, 1, 23)
        # }

Install
=======

.. code-block:: bash

        pip install marshmallow-annotations

Why?
====

Why not? Type annotations are pretty cool and so is marshmallow, it's like the chocolate peanut butter cup of data validation.
