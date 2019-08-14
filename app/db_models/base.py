from typing import Type, TypeVar

import peewee as pw
from playhouse.shortcuts import model_to_dict

from app.db.database import db

T = TypeVar('T')


class S:
    class BgmIpViewer(pw.Model):
        DoesNotExist: pw.DoesNotExist

        class Meta:
            database = db

        def dict(self):
            return model_to_dict(self)

        def __iter__(self):
            yield from self.dict()

        @classmethod
        def get(cls: Type[T], *query, **filters) -> T:
            return super().get(*query, **filters)

        @classmethod
        def upsert(cls, _data=None, **kwargs) -> pw.Insert:
            preserve = []
            for key in _data or kwargs:
                field: pw.Field = getattr(cls, key)
                if not (field.primary_key or field.unique):
                    preserve.append(field)
            return cls.insert(_data, **kwargs).on_conflict(preserve=preserve)
