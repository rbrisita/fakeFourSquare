import math

from faker import Faker
from faker.providers import company, date_time, lorem

class Generator:
    """
    Responsible for creating faker and seeding it.
    """
    _EARTH_RADIUS = 6378137

    def __init__(self):
        f = Faker()
        f.seed(42)
        f.add_provider(company)
        f.add_provider(date_time)
        f.add_provider(lorem)
        self._faker = f

    def generate_place(self, lat, lng, meters):
        return {
            'name': self.generate_name(),
            'location': self.generate_location(lat, lng, meters),
            'tags': self.generate_tags()
        }

    def generate_name(self):
        f = self._faker

        # f.company() + (' ' + f.company_suffix() if (f.random_int(1, 100) > 50) else '')
        if (f.random_int(1, 100) > 50):
            name = f.company() + ' ' + f.company_suffix()
        else:
            name = f.company()

        return name

    def generate_location(self, lat, lng, meters):
        """ Generate 2 random geo-coordinates and return array. """
        f = self._faker
        er = self._EARTH_RADIUS
        pi = math.pi

        dLat = (meters * f.random.random()) / er
        dLng = (meters * f.random.random()) / (er * math.cos(pi * lat / 180))
        new_lat = lat + dLat * 180 / pi
        new_lng = lng + dLng * 180 / pi

        return [new_lat, new_lng]

    def generate_tags(self):
        f = self._faker
        tags = []

        total = f.random_int(0, 3)
        for _ in range(total):
            tags.append(f.word())

        return tags

    def generate_review(self):
        return  {
            'date': self.generate_date(),
            'blurb': self.generate_blurb(),
            'rating': self.generate_rating()
        }

    def generate_date(self):
        return self._faker.past_datetime()

    def generate_blurb(self):
        return self._faker.paragraph()

    def generate_rating(self):
        return self._faker.random_int(1, 5)
