=======================
marshmallow-annotations
=======================

marshmallow-annotations allows you to create marshmallow schema from classes
with annotations on them

.. code-block:: python
    # music.py
    from typing import List

     class Album:
        id: int
        name: str

        def __init__(self, id: int, name: str):
            self.id = id
            self.name = name

    class Artist:
        id: int
        name: str
        albums: List[Album]

        def __init__(self, id: int, name: str, albums: List[Album]):
            self.id = id
            self.name = name
            self.albums = albums



.. code-block:: python

    # schema.py
    from marshmallow_annotations import AnnotationSchema
    from .music import Album, Artist

    class AlbumScheme(AnnotationSchema):
        class Meta:
            target = Album
            register_as_scheme = True


    class ArtistScheme(AnnotationSchema):
        class Meta:
            target = Artist
            register_as_scheme = True


    scheme = ArtistScheme()
    scheme.dump(
        Artist(
            id=1, name="Abominable Putridity",
            albums=[
                Album(
                    id=1,
                    name="The Anomalies of Artificial Origin"
                )
            ]
        )
    )

    # {
    #     "albums": [
    #         {
    #             "id": 1,
    #             "name": "The Anomalies of Artificial Origin"
    #         }
    #     ],
    #     "id": 1,
    #     "name": "Abominable Putridity"
    # }

************
Installation
************


marshmallow-annotations is available on `pypi <https://pypi.org/project/marshmallow-annotations/>`_
and installable with::

    pip install marshmallow-annotations

marshmallow-annotations supports Python 3.6+ and marshmallow 2.x.x


.. note::

    If you are install ``marshmallow-annotations`` outside of a virtual
    environment, consider installing with
    ``pip install --user marshmallow-annotations`` rather than using sudo or
    adminstrator privileges to avoid installing it into your system Python.


Why?
====

Keeping up with entity definitions, ORM mappings and schema shapes can be a huge
pain the butt. If you change one thing, you need to change three things.

Instead, marshmallow-annotations wants to drive schema shapes from your
entity defintions (with a little help from you of course).


More Information
----------------

- For more information, `please visit the documentation <http://marshmallow-annotations.readthedocs.io>`_.
- Found a bug, have a question, or want to request a feature? Here is our `issue tracker <https://github.com/justanr/marshmallow-annotations/issues>`_.
- Need the source code? Here is the `repository <https://github.com/justanr/marshmallow-annotations>`_
