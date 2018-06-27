.. _extensions:

##########
Extensions
##########

Specialized extensions are provided for specific use cases.


*****************
typing.NamedTuple
*****************

If you are working with :class:`typing.NamedTuple` definitions, you may use :class:`~marshmallow_annotations.ext.namedtuple.NamedTupleSchema`
to generate your schema. This modifies loading behavior to deserialize
directly to instances of your defined :class:`~typing.NamedTuple`::

    from marshmallow_annotations import NamedTupleSchema
    from typing import NamedTuple, Optional

    class Vector(NamedTuple):
        x: int
        y: Optional[int]
        z: Optional[int] = 5

    class VectorSchema(NamedTupleSchema):
        class Meta:
            target = Vector

    schema = VectorSchema()
    schema.load({'x': 1}).data

    # Vector(x=1, y=None, z=5)

    schema.dump(Vector(x=1, y=None, z=5)).data

    # {'x': 1, 'y': None, 'z': 5}


Additionally, the ``Meta`` class provides you with the option flag
``dump_default_args`` to control whether attribute values matching defaults
should be dumped or ignored::

    class VectorSchemaDropDefaults(NamedTupleSchema):
        class Meta:
            target = Vector
            dump_default_args = False

    schema = VectorSchemaDropDefaults()
    schema.dump(Vector(x=1, y=None, z=5)).data

    # {'x': 1}


NamedTuple API
==============

..autoclass:: marshmallow_annotations.ext.namedtuple.NamedTupleSchema

..autoclass:: marshmallow_annotations.ext.namedtuple.NamedTupleSchemaOpts
