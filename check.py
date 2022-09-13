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



class NameParser(Parser):

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
        name_parser = Word(alphanums + '.- _') + StringEnd()
        return name_parser

    # ParseException
    def parse_string(self) -> str:
        name = self.parser.parseString(self.string).asList()
        name = '_'.join(name)
        return name.capitalize()


class PhoneParser(Parser):

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
        symbols = '()_-*# '
        preffix = Optional(Suppress(Word(symbols))) + Optional(Suppress('+'))
        body = OneOrMore(Optional(Suppress(Word(symbols))) + Word(nums))
        phone_parser = Combine(preffix + body)

        return phone_parser

    # ParseException
    def parse_string(self) -> str:
        phone = self.parser.parseString(self.string).asList()[0]
        return phone


class EmailParser(Parser):

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
        quoted_chars = '(),:;<>@[]'
        unquoted_chars = "!#$%&'*+-/=?^_`{|}~"
        quote_lit = Literal('"')
        dot_lit = Literal('.')
        hyphen_lit = Literal('-')
        at_lit = Literal('@')
        space_lit = White()
        end_lit = StringEnd()

        unquoted_unit = Word(alphanums + unquoted_chars) + \
            ZeroOrMore(Optional(dot_lit) + Word(alphanums + unquoted_chars))
        quoted_unit = Word(alphanums + unquoted_chars +
                           quoted_chars + '.' + '\\')

        first_local_part = ZeroOrMore(
            (quote_lit + quoted_unit + quote_lit + dot_lit) | (unquoted_unit + dot_lit))
        last_local_part = (quote_lit + quoted_unit +
                           quote_lit) | unquoted_unit | (quote_lit + space_lit + quote_lit)
        local_part = Combine(first_local_part + last_local_part)('local_part')

        raw_first_order_domain = Word(
            alphanums) + Optional(hyphen_lit + Word(alphanums))
        first_order_domain = ZeroOrMore(
            OneOrMore(raw_first_order_domain) + dot_lit)
        domain = Combine(first_order_domain + Word(alphanums))('domain')

        email_parser = Combine(local_part + at_lit + domain + end_lit)

        return email_parser

    # ParseException
    def parse_string(self) -> str:
        email = self.parser.parseString(self.string)

        if len(email.local_part) > 64:
            return print('EmailLengthException')
        else:
            return email.asList()[0]


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


class AddressParser(Parser):

    def __init__(self, address_items: AddressItems):
        self.__string = None
        self.address_items = address_items
        self.parser = self.create_parser
        self.preffix_delim = Literal(': ')

    @property
    def string(self):
        return self.__string

    @string.setter
    def string(self, new_value):
        self.__string = new_value

    def create_city_parser(self):
        raw_city_parser = Word(alphas + "-/'().,_ ")('city')
        preffix = Literal(self.address_items.CITY.value) + self.preffix_delim
        city_parser = preffix + raw_city_parser + StringEnd()
        return city_parser

    def create_street_parser(self):
        raw_street_parser = Word(alphanums + "-/'().,_ ")('street')
        preffix = Literal(self.address_items.STREET.value) + self.preffix_delim
        street_parser = preffix + raw_street_parser + StringEnd()
        return street_parser

    def create_house_parser(self):
        raw_house_parser = Word(alphanums + "-/'().,_ ")('house')
        preffix = Literal(self.address_items.HOUSE.value) + self.preffix_delim
        house_parser = preffix + raw_house_parser + StringEnd()
        return house_parser

    def create_appartament_parser(self):
        raw_appartmt_parser = Word(alphanums + "-/'().,_ ")('appartment')
        preffix = Literal(
            self.address_items.APPARTAMENT.value) + self.preffix_delim
        appartmt_parser = preffix + raw_appartmt_parser + StringEnd()
        return appartmt_parser

    def create_zip_parser(self):
        raw_zip_parser = Word(nums)('zip')
        preffix = Literal(self.address_items.ZIP.value) + self.preffix_delim
        zip_parser = preffix + raw_zip_parser + StringEnd()
        return zip_parser

    def create_parser(self, parser_type: AddressItems):
        parsers = {
            parser_type.CITY: self.create_city_parser,
            parser_type.STREET: self.create_street_parser,
            parser_type.HOUSE: self.create_house_parser,
            parser_type.APPARTAMENT: self.create_appartament_parser,
            parser_type.ZIP: self.create_zip_parser
        }

        parser = parsers[parser_type]
        return parser()

    # ParseException
    def parse_string(self, parser_type: AddressItems) -> str:
        parser = self.parser(parser_type)
        address_items = parser.parseString(self.string)
        address = ''.join(address_items.asList())
        return address
