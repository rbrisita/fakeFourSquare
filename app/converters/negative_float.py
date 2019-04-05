from werkzeug.routing import NumberConverter

class NegativeFloatConverter(NumberConverter):
    """ Override NumberConverter to fix the issue with negative floats.
    Geocoordinates range:
    -90 <= latitude <= 90
    -180 <= longitude <= 180
    """
    regex = r'\-?\d+\.\d+'
    num_convert = float

    def __init__(self, map, min = None, max = None):
        NumberConverter.__init__(self, map, 0, min, max)
