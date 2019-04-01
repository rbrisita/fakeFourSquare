from datetime import datetime
import math

from faker.providers import company

from tools.generator.generator import Generator

class Place(Generator):
    """ Generate a place name, location and tags. """
    _EARTH_RADIUS = 6378137

    def __init__(self):
        """ Create base class and add specifc provider. """
        super().__init__()
        self._faker.add_provider(company)

    def generate(self, lng, lat, meters):
        """ Generate a place """
        return {
            'name': self.generate_name(),
            'location': self.generate_location(lng, lat, meters),
            'tags': self.generate_tags(),
            'created_at': datetime.utcnow()
        }

    def generate_name(self):
        """ Generate a name with a 50% chance of having a suffix. """
        f = self._faker

        # f.company() + (' ' + f.company_suffix() if (f.random_int(1, 100) > 50) else '')
        if (f.random_int(1, 100) > 50):
            name = f.company() + ' ' + f.company_suffix()
        else:
            name = f.company()

        return name

    def generate_location(self, lng, lat, meters):
        """ Generate 2 random geo-coordinates and return array. """
        f = self._faker
        er = self._EARTH_RADIUS
        pi = math.pi

        dLng = (meters * f.random.random()) / (er * math.cos(pi * lat / 180))
        dLat = (meters * f.random.random()) / er

        new_lng = lng + dLng * 180 / pi
        new_lat = lat + dLat * 180 / pi

        return [new_lng, new_lat]

    def generate_tags(self, min_tags = 0, max_tags = 3):
        """ Generate min to max tags. """
        f = self._faker
        tags = []

        total = f.random_int(min_tags, max_tags)
        for _ in range(total):
            tags.append(f.word())

        return tags
