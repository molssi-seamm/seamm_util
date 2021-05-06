"""Extend JSON encoding/decoding to handle pint Quantities, as well
as datetimes and timedeltas

To encode:
    import seamm_util
    dump = json.dumps(<variable>, cls=seamm_util.JSONEncoder)

and to decode:
    import seamm_util
    decoder = seamm_util.JSONDecoder()
    <variable> = decoder.decode(dump)

Adapted from
http://taketwoprogramming.blogspot.com/2009/06/subclassing-jsonencoder-and-jsondecode
"""

from seamm_util import ureg, Q_, units_class  # nopep8
import datetime
import json


class JSONEncoder(json.JSONEncoder):
    """
    Encodes a python object, where pint Quantities, datetime and
    timedelta objects are converted into objects that can be decoded
    using the seamm_util.JSONDecoder.

    Adapted from
    http://taketwoprogramming.blogspot.com/2009/06/subclassing-jsonencoder-and-jsondecoder.html  # noqa: E501
    """

    def default(self, obj):
        import seamm

        if isinstance(obj, units_class):
            return {"__type__": "pint_units", "data": obj.to_tuple()}
        elif isinstance(obj, datetime.datetime):
            return {
                "__type__": "datetime",
                "year": obj.year,
                "month": obj.month,
                "day": obj.day,
                "hour": obj.hour,
                "minute": obj.minute,
                "second": obj.second,
                "microsecond": obj.microsecond,
            }
        elif isinstance(obj, datetime.timedelta):
            return {
                "__type__": "timedelta",
                "days": obj.days,
                "seconds": obj.seconds,
                "microseconds": obj.microseconds,
            }
        elif isinstance(obj, seamm.Parameter) or isinstance(obj, seamm.Parameters):

            #  Populate the dictionary with object meta data
            obj_dict = {
                "__class__": obj.__class__.__name__,
                "__module__": obj.__module__,
            }

            #  Populate the dictionary with object properties
            obj_dict.update(obj.to_dict())

            return obj_dict
        else:
            return json.JSONEncoder.default(self, obj)


class JSONDecoder(json.JSONDecoder):
    """Decodes a json string, where pint Quantities, datetime and
    timedelta objects were converted into objects using the
    seamm_util.JSONEncoder, back into a python object.
    """

    def __init__(self):
        super().__init__(object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        if "__type__" in d:
            type = d.pop("__type__")
            if type == "pint_units":
                return Q_.from_tuple(d["data"])
            elif type == "datetime":
                return datetime.datetime(**d)
            elif type == "timedelta":
                return datetime.timedelta(**d)
            else:
                # Oops... better put this back together.
                d["__type__"] = type

        if "__class__" in d:
            class_name = d.pop("__class__")

            if class_name in "Parameter":
                # Get the module name from the dict and import it
                module_name = d.pop("__module__")
                module = __import__(module_name)

                # Get the class from the module
                class_ = getattr(module, class_name)

                # Use dictionary unpacking to initialize the object
                return class_(d)
            elif "Parameters" in class_name:
                # Get the module name from the dict and import it
                module_name = d.pop("__module__")
                module = __import__(module_name)

                # Get the class from the module
                class_ = getattr(module, class_name)

                # Use dictionary unpacking to initialize the object
                return class_(data=d)
            else:
                d["__init__class__"] = class_name

        return d


if __name__ == "__main__":
    acel = ureg("9.8 m/s**2")
    print(acel)
    print(acel.__class__)
    print(units_class)

    t = datetime.datetime.now()
    print(t)
    print(t.__class__)

    dct = {"acel": acel, "time": t}

    dump = json.dumps(dct, cls=JSONEncoder)
    print()
    print(dump)
    print()

    decoder = JSONDecoder()
    t2 = decoder.decode(dump)
    print(t2)
    print()
    print(t2["acel"])
    print(t2["acel"].__class__)
    print(t2["time"])
    print(t2["time"].__class__)
