from abc import ABC, abstractmethod
from enum import Enum
from pyparsing import *


class Parser(ABC):

    @abstractmethod
    def create_parser(self):
        pass

    @abstractmethod
    def parse_string(self):
        pass


class AddressItems(Enum):
    CITY = 'CITY'
    STREET = 'STREET'
    HOUSE = 'HOUSE'
    APPARTAMENT = 'APPARTAMENT'
    ZIP = 'ZIP'



class BirthdayParser(Parser):

    def __init__(self):
        self.__string = None
        self.parser = self.create_parser()

    @property
    def string(self):
        return self.__string

    @string.setter
    def string(self, new_value):
        self.__string = new_value

    def create_parser(self):
        delimiters = '.,;:/\-_'
        days_digits = ''.join([str(i) for i in range(1, 32)])
        months_digits = ''.join([str(i) for i in range(1, 13)])

        delimiter_unit = Word(delimiters) | White()
        days = Word(days_digits)
        months = Word(months_digits)

        day_unit = Combine(Optional('0') + days) + Suppress(delimiter_unit)
        month_unit = Combine(Optional('0') + months) + Suppress(delimiter_unit)
        year_unit = Combine(Char(nums) * (1, 4))

        date_str_parser = day_unit + month_unit + year_unit
        date_int_parser = date_str_parser.setParseAction(
            lambda t: [int(i) for i in t.asList() if i])

        return date_int_parser

    # ParseException
    def parse_string(self) -> list:
        date = self.parser.parseString(self.string).asList()[::-1]
        return date

phone =   BirthdayParser()
phone.string = "08-09-1988"
print (phone.parse_string())  