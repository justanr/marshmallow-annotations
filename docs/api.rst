.. _api:

###########################
marshmallow_annotations API
###########################


.. warning::

    Scary looking type signatures a head.


********
Type API
********

This section will hopeful ease some of the stress and tension that will
inevitably arise from looking at the following type signatures. Seriously,
they're not pretty.


Field Factory
=============

A field factory **is not** the field's instance constructor, rather it is
any callable that accepts:

1. An :class:`~marshmallow_annotations.base.AbstractConverter` instance
2. A tuple of type hints
3. A dictionary of configuration values for the underlying field

And returns a fully instantiated marshmallow Field instance, for example::

    from marshmallow import List as ListField

    def sequence_converter(converter, subtypes, opts):
        return ListField(converter.convet(subtypes[0]), **opts)

This might be registered against :class:`~typing.Tuple`::

    registry.register(typing.Tuple, sequence_converter)


A method that accepts a field factory contains the following signature::

    Callable[[AbstractConverter, Tuple[type], Dict[str, Any]], FieldABC]


********
Registry
********

.. autoclass:: marshmallow_annotations.base.TypeRegistry
    :members:


.. autoclass:: marshmallow_annotations.registry.DefaultTypeRegistry


.. autofunction:: marshmallow_annotations.registry.field_factory

.. autofunction:: marshmallow_annotations.registry.scheme_factory


*********
Converter
*********


.. autoclass:: marshmallow_annotations.base.AbstractConverter
    :members:

.. autoclass:: marshmallow_annotations.converter.BaseConverter


******
Schema
******

.. autoclass:: marshmallow_annotations.scheme.AnnotationSchemaMeta

    Metaclass that handles produces the
    :class:`~marshmallow_annotations.scheme.AnnotationSchema` class. Provided
    for integration into other libraries and toolkits

.. autoclass:: marshmallow_annotations.scheme.AnnotationSchema

.. autoclass:: marshmallow_annotations.scheme.AnnotationSchemaOpts


**********
NamedTuple
**********

.. autoclass:: marshmallow_annotations.schema.NamedTupleConverter

.. autoclass:: marshmallow_annotations.schema.NamedTupleSchemaOpts

.. autoclass:: marshmallow_annotations.schema.NamedTupleSchema
    :members:
