import json
import collections
import datetime
from datetime import date

REGISTERED_CLASS = {}


class MetaSerializable(type):
    def __call__(cls, *args, **kwargs):
        if cls.__name__ not in REGISTERED_CLASS:
            REGISTERED_CLASS[cls.__name__] = cls
        return super().__call__(*args, **kwargs)


class BaseSerializable(json.JSONEncoder, metaclass=MetaSerializable):
    fmt = "%m/%d/%Y - %H:%M"
    def default(self, obj):
        if isinstance(obj, date):
            return dict(_date_object=obj.strftime(self.fmt))
        if isinstance(obj, collections.Set):
            return dict(_set_object=list(obj))
        if isinstance(obj, BaseSerializable):
            jclass = {}
            jclass["name"] = type(obj).__name__
            jclass["dict"] = obj.__dict__
            return dict(_class_object=jclass)
        else:
            return json.JSONEncoder.default(self, obj)

    @classmethod
    def json_to_class(cls, dct):
        if '_set_object' in dct:
            return set(dct['_set_object'])
        elif '_date_object' in dct:
            dt = datetime.datetime.strptime(dct['_date_object'], cls.fmt).date()
            return dt
        elif '_class_object' in dct:
            cclass = dct['_class_object']
            cclass_name = cclass["name"]
            if cclass_name not in REGISTERED_CLASS:
                raise RuntimeError(
                    "Class {} not registered in JSON Parser"
                    .format(cclass["name"])
                )
            instance = REGISTERED_CLASS[cclass_name]()
            instance.__dict__ = cclass["dict"]
            return instance
        return dct

    def storeJSON(self):
        s = json.dumps(
            self.__dict__, cls=BaseSerializable,
            indent=4,
            sort_keys=True
        )
        return s

    @classmethod
    def loadJSON(cls, json_str):
        return json.loads(
            json_str,
            object_hook=cls.json_to_class
        )

