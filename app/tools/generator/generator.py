from abc import ABC, abstractmethod

from faker import Faker

class Generator(ABC):
    """
    Responsible for creating faker and seeding it.
    """

    def __init__(self):
        f = Faker()
        f.seed(42)
        self._faker = f

    @abstractmethod
    def generate(self):
        """ Generate full model. """
        pass
