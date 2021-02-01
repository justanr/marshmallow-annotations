#######################
marshmallow-annotations
#######################

Version |version| (:ref:`Change Log <changelog>`)

marshmallow-annotations allows you to create marshmallow schema from classes
with annotations on them::

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


.. include:: installation.rst


*******
Content
*******

.. toctree::
   :maxdepth: 1

   quickstart
   usage
   customizing
   api
   ext/index
   changelog
