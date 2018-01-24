"""Extend JSON encoding/decoding to handle pint Quantities, as well
as datetimes and timedeltas

To encode:
    import molssi_util
    dump = json.dumps(<variable>, cls=molssi_util.JSONEncoder)

and to decode:
    import molssi_util
    decoder = molssi_util.JSONDecoder()
    <variable> = decoder.decode(dump)

Adapted from
http://taketwoprogramming.blogspot.com/2009/06/subclassing-jsonencoder-and-jsondecode
"""

try:
    from molssi_workflow import units, Q_, units_class  # nopep8
except:
    print('Importing pint directly')
    import pint
    units = pint.UnitRegistry()
    Q_ = units.Quantity
    units_class = units('1 km').__class__
import datetime
import json


class JSONEncoder(json.JSONEncoder):
    """ 
    Encodes a python object, where pint Quantities, datetime and
    timedelta objects are converted into objects that can be decoded
    using the molssi_util.JSONDecoder.

    Adapted from
    http://taketwoprogramming.blogspot.com/2009/06/subclassing-jsonencoder-and-jsondecoder.html  # nopep8
    """

    def default(self, obj):
        if isinstance(obj, units_class):
            return {'__type__': 'pint_units', 'data': obj.to_tuple()}
        elif isinstance(obj, datetime.datetime):
            return {
                '__type__': 'datetime',
                'year': obj.year,
                'month': obj.month,
                'day': obj.day,
                'hour': obj.hour,
                'minute': obj.minute,
                'second': obj.second,
                'microsecond': obj.microsecond,
            }
        elif isinstance(obj, datetime.timedelta):
            return {
                '__type__': 'timedelta',
                'days': obj.days,
                'seconds': obj.seconds,
                'microseconds': obj.microseconds,
            }
        else:
            return json.JSONEncoder.default(self, obj)


class JSONDecoder(json.JSONDecoder):
    """Decodes a json string, where pint Quantities, datetime and
    timedelta objects were converted into objects using the
    molssi_util.JSONEncoder, back into a python object.
    """

    def __init__(self):
        super().__init__(object_hook=self.dict_to_object)

    def dict_to_object(self, d):
        if '__type__' not in d:
            return d

        type = d.pop('__type__')
        if type == 'pint_units':
            return Q_.from_tuple(d['data'])
        elif type == 'datetime':
            return datetime.datetime(**d)
        elif type == 'timedelta':
            return datetime.timedelta(**d)
        else:
            # Oops... better put this back together.
            d['__type__'] = type
            return d


if __name__ == '__main__':
    acel = units('9.8 m/s**2')
    print(acel)
    print(acel.__class__)
    print(units_class)

    t = datetime.datetime.now()
    print(t)
    print(t.__class__)

    dct = {'acel': acel, 'time': t}

    dump = json.dumps(dct, cls=JSONEncoder)
    print()
    print(dump)
    print()

    decoder = JSONDecoder()
    t2 = decoder.decode(dump)
    print(t2)
    print()
    print(t2['acel'])
    print(t2['acel'].__class__)
    print(t2['time'])
    print(t2['time'].__class__)
