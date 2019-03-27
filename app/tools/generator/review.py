from faker.providers import date_time, lorem

from tools.generator.generator import Generator

class Review(Generator):
    """ Generate a review that has blurb, date, rating. """

    def __init__(self):
        """ Create base class and add specifc provider. """
        super().__init__()
        self._faker.add_provider(date_time)
        self._faker.add_provider(lorem)

    def generate(self):
        """ Generate a review. """
        return  {
            'date': self.generate_date(),
            'blurb': self.generate_blurb(),
            'rating': self.generate_rating()
        }

    def generate_date(self):
        """ Generate a time in the past. """
        return self._faker.past_datetime()

    def generate_blurb(self):
        """ Generate a 1 to 3 sentence paragraph. """
        return self._faker.paragraph()

    def generate_rating(self):
        """ Generate a 1 to 5 rating """
        return self._faker.random_int(1, 5)
