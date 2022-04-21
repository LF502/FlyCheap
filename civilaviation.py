__all__ = ('Airline', 'Airport', 'Route', 'copy_data')

from random import choice
from typing import Literal
from pandas import DataFrame, read_csv

_airport = read_csv(r'.\_airport.csv').fillna('')
_airport['province'] = _airport['province'].astype('category')
_airport['airport'] = _airport['city'] + _airport['airport']
_airline = read_csv(r'.\_airline.csv').fillna('')
_airline['country'] = _airline['country'].astype('category')

def copy_data(__key: Literal['airport', 'airline', 'throughput'], __deep: bool = True) -> DataFrame:
    return eval(f'_{__key}.copy({__deep})')
class AirlineNotFound(KeyError): ...
class AirportNotFound(KeyError): ...
class InvalidCode(ValueError): ...

class Airline:
    '''Support IATA/ICAO Code and Chinese airline name input
    Note: Chinese names are auto-translated by Google, except for airlines frequently seen in China.'''
    __slots__ = ('icao', 'iata', 'name', 'name_eng', 'callsign', 'country')
    
    iata: str
    icao: str
    name: str
    name_eng: str
    callsign: str
    country: str
    
    def __new__(cls, __str):
        self = object.__new__(cls)
        if isinstance(__str, str):
            __str = __str.upper()
            if __str.isupper():
                if len(__str) == 2:
                    _loc = _airline.loc[_airline['iata'] == __str]
                elif len(__str) == 3:
                    _loc = _airline.loc[_airline['icao'] == __str]
                else:
                    raise InvalidCode('IATA or ICAO code input error')
            else:
                _loc = _airline.loc[_airline['name'] == __str.strip('航空')]
            if not len(_loc):
                raise AirlineNotFound(
                    f'Airline {__str} not found, add one by `add` method')
            self.iata, self.icao, self.name, self.name_eng, self.callsign, self.country = \
                _loc.values[0]
            return self
        else:
            raise TypeError(
                "IATA/ICAO code string or airline name string required.")

    def __eq__(self, other):
        if isinstance(other, Airline):
            return self.icao == other.icao
        elif isinstance(other, str):
            other = other.upper()
            return self.icao == other or self.iata == other or self.name in other or \
                self.name_eng.upper() in other or self.callsign.upper() == other
        else:
            return False
    
    def __hash__(self):
        return hash(repr(self).encode())
    
    def __repr__(self):
        return "{0}.{1}('{2}', '{3}', '{4}', ...))".format(
            self.__class__.__module__, 
            self.__class__.__qualname__, 
            self.iata, self.icao, self.name_eng)
    
    def __str__(self):
        return self.name
    
    def __dict__(self):
        return dict((k, v) for k, v in zip(self.__slots__, self.separates))

    @classmethod
    def random(cls):
        return cls.__new__(Airline, choice(_airline['icao']))
    
    @classmethod
    def add(cls, iata: str, icao: str, **kwargs):
        '''
        Add an aiport by iata code and icao code (least required)
        `**kwargs`: name, name_eng, callsign, country
        '''
        self = object.__new__(cls)
        self.iata, self.icao = iata, icao
        self.name, self.name_eng, self.callsign, self.country = (
            kwargs.get('name', ''), kwargs.get('name_eng', ''), 
            kwargs.get('callsign', ''), kwargs.get('country', ''))
        return self

    @property
    def separates(self) -> tuple:
        '''iata, icao, name, name_eng, callsign, country'''
        return self.iata, self.icao, self.name, self.name_eng, self.callsign, self.country

class Airport:
    '''
    Support IATA/ICAO Code and Chinese airport name input
    Note: `code` is the primary airport of multi airport cities, except `BJS` == `PEK`
    '''
    __slots__ = (
        'icao', 'iata', 'city', 'airport', 'city_eng', 'airport_eng', 'province', 
        'latitude', 'longitude', 'elevation','type', 'code', 'multi')
    
    iata: str
    icao: str
    code: str
    city: str
    airport: str
    city_eng: str
    airport_eng: str
    province: str
    type: str
    latitude: float
    longitude: float
    elevation: int
    multi: bool
    
    def __new__(cls, __str):
        self = object.__new__(cls)
        if isinstance(__str, str):
            __str = __str.upper()
            if __str.isupper():
                if len(__str) == 3:
                    _loc = _airport.loc[_airport['iata'] == __str]
                elif len(__str) == 4:
                    _loc = _airport.loc[_airport['icao'] == __str]
                else:
                    raise InvalidCode('IATA or ICAO code input error')
            else:
                _loc = _airport.loc[_airport['city'] == __str]
                if not len(_loc):
                    _loc = _airport.loc[_airport['airport'] == __str]
            if not len(_loc):
                raise AirportNotFound(
                    f'Airport {__str} not found, add one by `add` method')
            self.iata, self.icao, self.city, self.airport, self.city_eng, self.airport_eng, \
                self.province, self.latitude, self.longitude, self.elevation, self.type = _loc.values[0]
            self.code = 'BJS' if self.city == '北京' else _airport.loc[_airport['city'] == self.city]['iata'].values[0]
            self.multi = len(_airport.loc[_airport['city'] == self.city]) != 1
            return self
        else:
            raise TypeError(
                "IATA/ICAO code string or city name string required,", 
                "for multi airport cities, input", 
                "'北京大兴'/'北京首都'... for exact airport code.")
    
    def citycmp(self, __other):
        if isinstance(__other, Airport):
            return True if __other.city == self.city else __other == self
        elif isinstance(__other, str):
            return True if __other == self.city else __other == self
        else:
            return False
    
    def __eq__(self, other):
        if isinstance(other, Airport):
            return self.iata == other.iata
        elif isinstance(other, str):
            other = other.upper()
            return True if other == 'BJS' and self.iata == 'PEK' else self.icao == other or \
                self.iata == other or (self.city in other and self.airport in other) or \
                (self.city_eng.upper() in other and self.airport_eng.upper() in other)
        else:
            return False
    
    def __hash__(self):
        return hash(repr(self).encode())
    
    def __sub__(self, other):
        if isinstance(other, Airport) or isinstance(other, str):
            return Route(self, other)
        else:
            raise TypeError("String or class 'Airport' required")
    
    def __add__(self, other):
        if isinstance(other, Airport):
            return self.city + '-' + other.city
        elif isinstance(other, str):
            return self.city + '-' + other
        else:
            raise TypeError("String or class 'Airport' required")
    
    def __repr__(self):
        return "{0}.{1}('{2}', '{3}', '{4}', ...)".format(
            self.__class__.__module__, 
            self.__class__.__qualname__, 
            self.iata, self.icao, self.airport)
    
    def __str__(self):
        return self.airport if self.multi else self.city
    
    def __dict__(self):
        return dict((k, v) for k, v in zip(self.__slots__, self.separates))
    
    @classmethod
    def random(cls):
        return cls.__new__(Airport, choice(_airport['icao']))
    
    @classmethod
    def add(cls, iata: str, city: str, **kwargs):
        '''
        Add an aiport by iata code and city (least required)
        `**kwargs`: icao, airport, city_eng, airport_eng, 
        latitude, longitude, elevation, type, code, multi
        '''
        self = object.__new__(cls)
        self.iata, self.city = iata, city
        self.icao, self.airport = kwargs.get('icao', ''), kwargs.get('airport', '')
        self.city_eng, self.airport_eng = kwargs.get('city_eng', ''), kwargs.get('airport_eng', '')
        self.province = kwargs.get('province', '')
        self.latitude, self.longitude = kwargs.get('latitude', -1), kwargs.get('longitude', -1)
        self.elevation, self.type = kwargs.get('elevation', -1), kwargs.get('type', '')
        self.code = kwargs.get('code', _airport.loc[_airport['city'] == city]['iata'].values[0] \
            if city in _airport['city'] else iata)
        self.multi = kwargs.get('multi', self.city in _airport['city'])
        return self
    
    @property
    def separates(self) -> tuple:
        '''iata, icao, city, airport, city in English, airport in English, 
        province, latitude, elevation in ft, longitude, type, code, multi'''
        return self.iata, self.icao, self.city, self.airport, self.city_eng, self.airport_eng, \
            self.province, self.latitude, self.longitude, self.elevation, self.type, self.code, self.multi


class Route:
    '''An one way route'''
    __slots__ = 'dep', 'arr', 'airfare', 'greatcircle'
    
    dep: Airport
    arr: Airport
    airfare: int
    greatcircle: int
    
    def __new__(cls, __dep: Airport | str, __arr: Airport | str, /):
        self = object.__new__(cls)
        if isinstance(__dep, str):
            __dep = Airport(__dep)
        if isinstance(__arr, str):
            __arr = Airport(__arr)
        if isinstance(__dep, Airport) and isinstance(__arr, Airport):
            self.dep, self.arr = __dep, __arr
            self.airfare = _airfare.get(
                (__dep.iata, __arr.iata), _airfare.get((__arr.iata, __dep.iata), 0))
            self.greatcircle = _greatcircle.get(
                (__dep.code, __arr.code), _greatcircle.get((__arr.code, __dep.code), 0))
            return self
        else:
            raise TypeError("String or class 'Airport' required")
    
    @classmethod
    def fromformat(cls, __str: str, sep: str = '-'):
        return cls.__new__(Route, *(__str.split(sep, 1)))
    
    @classmethod
    def random(cls):
        return cls.__new__(Route, Airport.random(), Airport.random())
    
    def __eq__(self, other):
        if isinstance(other, Route):
            return self.dep == other.dep and self.arr == other.arr
        elif isinstance(other, str):
            return str(self) == other
        elif isinstance(other, tuple):
            return other[0] == self.dep and other[1] == self.arr if len(other) == 2 else False
        else:
            return False
    
    def citycmp(self, __other, __oneway = True, /):
        if isinstance(__other, Route):
            cmp = self.dep.citycmp(__other.dep) and self.arr.citycmp(__other.arr)
            return cmp if __oneway else cmp or self.arr.citycmp(__other.dep) and self.dep.citycmp(__other.arr)
        else:
            return False
    
    def __repr__(self):
        return "{0}.{1}({2}, {3})".format(
            self.__class__.__module__, self.__class__.__qualname__, 
            self.dep, self.arr)
    
    def __str__(self):
        return f"{self.dep}-{self.arr}"
    
    def __hash__(self):
        return hash(repr(self).encode())
    
    def __dict__(self):
        return dict((k, v) for k, v in zip(self.__slots__, self.separates))
    
    def format(self, key: str = 'code', sep: str = '-'):
        return f"{eval(self.dep)}{sep}{eval(self.arr)}" if key == '' or key is None \
            else f"{eval(f'self.dep.{key}')}{sep}{eval(f'self.arr.{key}')}"
    
    @property
    def returns(self):
        return self.__new__(Route, self.arr, self.dep)
    
    def separates(self, key: str | None = None, /):
        return (self.dep, self.arr) if key == '' or key is None else \
            (eval(f"self.dep.{key}"), eval(f"self.arr.{key}"))
    
    def ismulti(self):
        return self.dep.multi or self.arr.multi
    
    def isinactive(self):
        return (self.dep.code, self.arr.code) in _inactive \
            or (self.arr.code, self.dep.code) in _inactive
    
    def islow(self):
        return (self.dep.code, self.arr.code) in skipped_routes \
            or (self.arr.code, self.dep.code) in skipped_routes


_inactive = {
    ('BJS', 'TSN'), ('BJS', 'SJW'), ('BJS', 'TYN'), ('BJS', 'TNA'), 
    ('BJS', 'SHE'), ('CGO', 'NKG'), ('TYN', 'TNA'), ('DLC', 'CGQ'), 
    ('BJS', 'HET'), ('SJW', 'TSN'), ('TSN', 'DLC'), ('TSN', 'TAO'), 
    ('SJW', 'TYN'), ('SJW', 'TNA'), ('TSN', 'TNA'), ('TSN', 'TYN'), 
    ('SHE', 'CGQ'), ('CGQ', 'HRB'), ('SHE', 'HRB'), ('DLC', 'SHE'), 
    ('BJS', 'SHE'), ('BJS', 'CGO'), ('TNA', 'CGO'), ('BJS', 'TAO'), 
    ('TNA', 'TAO'), ('CGO', 'WUH'), ('XIY', 'SJW'), ('WUX', 'YTY'), 
    ('CGO', 'SJW'), ('CGO', 'XIY'), ('CGO', 'HFE'), ('CGO', 'TYN'), 
    ('XIY', 'INC'), ('XIY', 'LHW'), ('CTU', 'XIY'), ('XIY', 'TYN'), 
    ('XIY', 'WUH'), ('WUH', 'KHN'), ('NKG', 'HGH'), ('HGH', 'WUX'), 
    ('WUH', 'HFE'), ('WUH', 'NKG'), ('NKG', 'HFE'), ('WUH', 'CSX'), 
    ('WUH', 'HGH'), ('NKG', 'SHA'), ('SHA', 'YTY'), ('WUX', 'NTG'), 
    ('NKG', 'WUX'), ('NKG', 'CZX'), ('NKG', 'NTG'), ('NKG', 'YTY'), 
    ('SHA', 'HGH'), ('SHA', 'WUX'), ('SHA', 'NTG'), ('SHA', 'CZX'), 
    ('HGH', 'CZX'), ('HGH', 'NTG'), ('HGH', 'YTY'), ('WUX', 'CZX'), 
    ('CZX', 'NTG'), ('CZX', 'YTY'), ('NTG', 'YTY'), ('SHA', 'HFE'), 
    ('HGH', 'HFE'), ('SZX', 'SWA'), ('WUH', 'WUX'), ('KHN', 'XMN'), 
    ('HFE', 'CZX'), ('WUH', 'NTG'), ('KHN', 'KWE'), ('HGH', 'XMN'), 
    ('HFE', 'WUX'), ('HFE', 'YTY'), ('HFE', 'NTG'), ('WUH', 'CZX'), 
    ('WUH', 'YTY'), ('KHN', 'CSX'), ('KHN', 'HGH'), ('KHN', 'FOC'), 
    ('CSX', 'CAN'), ('CSX', 'NNG'), ('CSX', 'FOC'), ('CSX', 'XMN'), 
    ('HGH', 'FOC'), ('ZUH', 'SWA'), ('KWE', 'NNG'), ('FOC', 'XMN'), 
    ('CAN', 'SZX'), ('CAN', 'ZUH'), ('ZUH', 'SZX'), ('CAN', 'SWA'), 
    ('SWA', 'FOC'), ('SWA', 'XMN'), ('CAN', 'NNG'), ('FOC', 'NNG'), 
    ('CKG', 'XIY'), ('KWE', 'KMG'), ('HET', 'SJW'), ('FOC', 'ZHA'), 
    ('KMG', 'NNG'), ('KWE', 'CTU'), ('KWE', 'CSX'), ('CKG', 'KWE'), 
    ('CTU', 'CKG'), ('HET', 'TYN'), ('SWA', 'ZHA'), ('FOC', 'SZX'), 
    ('LHW', 'XNN'), ('XNN', 'INC'), ('INC', 'LHW'), ('HET', 'INC'), 
    ('JJN', 'XMN'), ('JJN', 'FOC'), ('JJN', 'ZHA'), ('SZX', 'JJN'), 
    ('HAK', 'SYX'), ('HRB', 'HLD'), ('SZX', 'ZHA'), ('FOC', 'SYX'), 
    ('HFE', 'CSX'), ('CGQ', 'TSN'), ('TSN', 'JJN'), 
    }

_low = {
    ('LXA', 'ZHA'), ('LXA', 'SZX'), ('LXA', 'JJN'), ('CTU', 'SWA'), 
    ('SHA', 'LXA'), ('TSN', 'LXA'), ('URC', 'SWA'), ('NKG', 'LXA'), 
    ('LXA', 'XMN'), ('LXA', 'CZX'), ('LXA', 'WUX'), ('LXA', 'HLD'), 
    ('LXA', 'JHG'), ('LXA', 'SWA'), ('TAO', 'SWA'), ('CGO', 'LXA'), 
    ('LXA', 'TAO'), ('LXA', 'DLC'), ('LXA', 'SYX'), ('LXA', 'HAK'), 
    ('LXA', 'FOC'), ('LXA', 'JJN'), ('WUH', 'LXA'), ('JHG', 'HAK'), 
    ('JHG', 'CZX'), ('JHG', 'WUX'), ('JHG', 'XMN'), ('JHG', 'JJN'), 
    ('JHG', 'HRB'), ('JHG', 'ZHA'), ('TSN', 'WUX'), ('LHW', 'SWA'), 
    ('JHG', 'SWA'), ('JHG', 'SYX'), ('JHG', 'HLD'), ('JHG', 'URC'), 
    ('JHG', 'TAO'), ('JHG', 'DLC'), ('HLD', 'URC'), ('HLD', 'TAO'), 
    ('HLD', 'KMG'), ('WUX', 'LHW'), ('XMN', 'ZHA'), ('WUH', 'JHG'), 
    ('TAO', 'JJN'), ('TSN', 'ZHA'), ('LHW', 'HAK'), ('KMG', 'ZHA'),
    ('HRB', 'WUX'), ('ZHA', 'HAK'), ('XIY', 'SWA'), ('CTU', 'ZHA'), 
    ('LHW', 'JJN'), ('TAO', 'CZX'), ('HLD', 'CKG'), ('HLD', 'SYX'), 
    ('WUX', 'XMN'), ('CZX', 'CGO'), ('HLD', 'SHA'), ('WUH', 'JJN'), 
    ('JHG', 'SZX'), ('HLD', 'LHW'), ('CZX', 'XMN'), ('CZX', 'FOC'), 
    ('TSN', 'SWA'), ('CGO', 'ZHA'), ('CZX', 'SYX'), ('TSN', 'NKG'), 
    ('LHW', 'SYX'), ('HGH', 'SWA'), ('HLD', 'WUX'), ('CGQ', 'CZX'), 
    ('HLD', 'DLC'), ('URC', 'LXA'), ('TSN', 'CGO'), ('WUX', 'SWA'), 
    ('HLD', 'XMN'), ('XMN', 'SYX'), ('WUH', 'ZHA'), ('HLD', 'CTU'), 
    ('HLD', 'FOC'), ('CGO', 'SWA'), ('HLD', 'ZHA'), ('HRB', 'JJN'), 
    ('DLC', 'ZHA'), ('HLD', 'HGH'), ('JJN', 'SWA'), ('URC', 'SYX'), 
    ('HLD', 'XIY'), ('XIY', 'ZHA'), ('WUX', 'HAK'), ('CKG', 'JHG'), 
    ('HLD', 'SWA'), ('HGH', 'LXA'), ('HRB', 'URC'), ('CZX', 'URC'), 
    ('HLD', 'WUH'), ('HLD', 'NKG'), ('DLC', 'SWA'), ('JHG', 'LHW'), 
    ('URC', 'FOC'), ('NKG', 'ZHA'), ('TAO', 'ZHA'), ('JJN', 'SYX'), 
    ('HLD', 'CAN'), ('TSN', 'CZX'), ('SWA', 'HAK'), ('CZX', 'JJN'), 
    ('URC', 'ZHA'), ('ZHA', 'SYX'), ('WUH', 'LHW'), ('WUX', 'ZHA'), 
    ('HLD', 'CGO'), ('WUX', 'FOC'), ('CKG', 'LHW'), ('LXA', 'CAN'), 
    ('TAO', 'FOC'), ('HLD', 'HAK'), ('CTU', 'JHG'), ('CZX', 'CKG'), 
    ('NKG', 'SWA'), ('BJS', 'HLD'), ('BJS', 'CZX'), ('WUX', 'XIY'), 
    ('BJS', 'JHG'), ('JHG', 'XIY'), ('NKG', 'JHG'), ('XMN', 'SZX'), 
    ('TSN', 'SYX'), ('HGH', 'JJN'), ('HRB', 'LHW'), ('CZX', 'KMG'), 
    ('DLC', 'CZX'), ('WUX', 'CGO'), ('JHG', 'CAN'), ('DLC', 'URC'), 
    ('URC', 'JJN'), ('HRB', 'DLC'), ('WUH', 'SWA'), ('LHW', 'LXA'), 
    ('HRB', 'ZHA'), ('SWA', 'SYX'), ('CZX', 'LHW'), ('TSN', 'JHG'), 
    ('HLD', 'TSN'), ('XIY', 'JJN'), ('FOC', 'HAK'), ('JHG', 'FOC'), 
    ('HLD', 'SZX'), ('HRB', 'SWA'), ('WUX', 'URC'), ('DLC', 'SYX'), 
    ('HRB', 'LXA'), ('TAO', 'URC'), ('TSN', 'LHW'), ('CZX', 'ZHA'), 
    ('CGO', 'JHG'), ('LHW', 'ZHA'), ('DLC', 'WUX'), ('CKG', 'ZHA'), 
    ('CZX', 'XIY'), ('WUX', 'JJN'), ('HLD', 'CZX'), ('CZX', 'SWA'), 
    ('WUX', 'SYX'), ('HGH', 'ZHA'), ('HLD', 'JJN'), ('CZX', 'HAK'), 
    ('DLC', 'JJN'), ('DLC', 'LHW'), ('JJN', 'HAK'), ('TAO', 'WUX'), 
    ('HRB', 'INC'), ('KMG', 'INC'), ('INC', 'FOC'), ('SZX', 'CSX'), 
    ('XMN', 'INC'), ('HFE', 'XIY'), ('SJW', 'SZX'), ('TSN', 'SHE'), 
    ('CGQ', 'INC'), ('SJW', 'HFE'), ('HFE', 'FOC'), ('TSN', 'HFE'), 
    ('XMN', 'LHW'), ('SJW', 'WUH'), ('SZX', 'INC'), ('INC', 'WUH'), 
    ('SYX', 'INC'), ('SJW', 'TAO'), ('CSX', 'CGO'), ('TSN', 'INC'), 
    ('CGQ', 'LHW'), ('SJW', 'CZX'), ('SJW', 'WUX'), ('SJW', 'INC'), 
    ('SJW', 'CSX'), ('HFE', 'INC'), ('HAK', 'INC'), ('CZX', 'INC'), 
    ('SHE', 'INC'), ('CGQ', 'URC'), ('HFE', 'LHW'), ('CZX', 'CSX'), 
    ('WUX', 'INC'), ('INC', 'DLC'), ('SJW', 'DLC'), ('SHE', 'LHW'), 
    ('CGQ', 'WUX'), ('SJW', 'NKG'), ('INC', 'TAO'), ('HRB', 'CZX'), 
    }

_airfare = {
    ('PEK', 'CAN'): 3060, ('PEK', 'CKG'): 2170, ('PEK', 'CTU'): 2230, 
    ('PEK', 'DLC'): 930, ('PEK', 'FOC'): 2020, ('PEK', 'HAK'): 3160, 
    ('PEK', 'HGH'): 2660, ('PEK', 'HRB'): 1700, ('PEK', 'JJN'): 1730, 
    ('PEK', 'KMG'): 2550, ('PEK', 'LHW'): 2010, ('PEK', 'LXA'): 3260, 
    ('PEK', 'NKG'): 2230, ('PEK', 'SHA'): 1960, ('PEK', 'SWA'): 1910, 
    ('PEK', 'SYX'): 3680, ('PEK', 'SZX'): 2500, ('PEK', 'URC'): 3480, 
    ('PEK', 'WUH'): 2510, ('PEK', 'WUX'): 2110, ('PEK', 'XIY'): 2450, 
    ('PEK', 'XMN'): 2120, ('CAN', 'HAK'): 1890, ('CAN', 'SYX'): 1590, 
    ('CAN', 'ZHA'): 970, ('CGO', 'CAN'): 1700, ('CGO', 'CKG'): 1270, 
    ('CGO', 'CTU'): 1220, ('CGO', 'FOC'): 1370, ('CGO', 'HAK'): 2220, 
    ('CGO', 'HGH'): 940, ('CGO', 'JJN'): 1360, ('CGO', 'KMG'): 2060, 
    ('CGO', 'LHW'): 1100, ('CGO', 'SHA'): 1280, ('CGO', 'SYX'): 2470, 
    ('CGO', 'SZX'): 2360, ('CGO', 'URC'): 2560, ('CGO', 'XMN'): 1360, 
    ('CKG', 'CAN'): 1650, ('CKG', 'HAK'): 1900, ('CKG', 'KMG'): 1180, 
    ('CKG', 'LXA'): 2730, ('CKG', 'SWA'): 1740, ('CKG', 'SYX'): 2230, 
    ('CKG', 'SZX'): 1940, ('CKG', 'URC'): 2750, ('CKG', 'WUH'): 1250, 
    ('CTU', 'CAN'): 2070, ('CTU', 'HAK'): 1740, ('CTU', 'KMG'): 1410, 
    ('CTU', 'LHW'): 1110, ('CTU', 'LXA'): 2590, ('CTU', 'SYX'): 2680, 
    ('CTU', 'SZX'): 2350, ('CTU', 'URC'): 2860, ('CTU', 'WUH'): 1470, 
    ('CZX', 'CAN'): 1460, ('CZX', 'CTU'): 1600, ('CZX', 'SZX'): 1540, 
    ('DLC', 'CAN'): 2190, ('DLC', 'CGO'): 960, ('DLC', 'CKG'): 1950, 
    ('DLC', 'CTU'): 2130, ('DLC', 'FOC'): 1680, ('DLC', 'HAK'): 2700, 
    ('DLC', 'HGH'): 1240, ('DLC', 'KMG'): 2880, ('DLC', 'NKG'): 1000, 
    ('DLC', 'SHA'): 1130, ('DLC', 'SZX'): 2460, ('DLC', 'TAO'): 1000, 
    ('DLC', 'WUH'): 1490, ('DLC', 'XIY'): 1410, ('DLC', 'XMN'): 1890, 
    ('FOC', 'CAN'): 1480, ('FOC', 'CKG'): 1610, ('FOC', 'CTU'): 1920, 
    ('FOC', 'KMG'): 2260, ('FOC', 'LHW'): 2060, ('FOC', 'WUH'): 1050, 
    ('FOC', 'XIY'): 1680, ('HGH', 'CAN'): 1550, ('HGH', 'CKG'): 2000, 
    ('HGH', 'CTU'): 2230, ('HGH', 'HAK'): 1940, ('HGH', 'JHG'): 2200, 
    ('HGH', 'KMG'): 2390, ('HGH', 'LHW'): 1760, ('HGH', 'SYX'): 2510, 
    ('HGH', 'SZX'): 1650, ('HGH', 'URC'): 3280, ('HGH', 'XIY'): 1540, 
    ('HRB', 'CAN'): 3780, ('HRB', 'CGO'): 1820, ('HRB', 'CKG'): 2480, 
    ('HRB', 'CTU'): 3050, ('HRB', 'CZX'): 1740, ('HRB', 'FOC'): 2350, 
    ('HRB', 'HAK'): 3330, ('HRB', 'HGH'): 2230, ('HRB', 'KMG'): 4100, 
    ('HRB', 'NKG'): 1740, ('HRB', 'SHA'): 1810, ('HRB', 'SYX'): 3480, 
    ('HRB', 'SZX'): 3360, ('HRB', 'TAO'): 1570, ('HRB', 'TSN'): 1250, 
    ('HRB', 'WUH'): 2050, ('HRB', 'XIY'): 1980, ('HRB', 'XMN'): 2550, 
    ('JJN', 'CAN'): 1120, ('JJN', 'CKG'): 1510, ('JJN', 'CTU'): 1750, 
    ('JJN', 'KMG'): 1890, ('KMG', 'CAN'): 1970, ('KMG', 'HAK'): 1440, 
    ('KMG', 'JHG'): 2010, ('KMG', 'LHW'): 2050, ('KMG', 'LXA'): 2480, 
    ('KMG', 'SWA'): 1830, ('KMG', 'SYX'): 1810, ('KMG', 'SZX'): 2220, 
    ('KMG', 'URC'): 3400, ('KMG', 'WUH'): 1660, ('KMG', 'XIY'): 2060, 
    ('LHW', 'CAN'): 2210, ('LHW', 'SZX'): 2100, ('NKG', 'CAN'): 1710, 
    ('NKG', 'CKG'): 1620, ('NKG', 'CTU'): 2150, ('NKG', 'FOC'): 920, 
    ('NKG', 'HAK'): 1940, ('NKG', 'JJN'): 1020, ('NKG', 'KMG'): 2160, 
    ('NKG', 'LHW'): 1650, ('NKG', 'SYX'): 1960, ('NKG', 'SZX'): 2030, 
    ('NKG', 'URC'): 3380, ('NKG', 'XIY'): 1180, ('NKG', 'XMN'): 1110, 
    ('SHA', 'CAN'): 1780, ('SHA', 'CKG'): 1870, ('SHA', 'CTU'): 2560, 
    ('SHA', 'FOC'): 1030, ('SHA', 'HAK'): 1750, ('SHA', 'JHG'): 2350, 
    ('SHA', 'JJN'): 1350, ('SHA', 'LHW'): 1860, ('SHA', 'SWA'): 1220, 
    ('SHA', 'SYX'): 2620, ('SHA', 'SZX'): 2030, ('SHA', 'TAO'): 1660, 
    ('SHA', 'URC'): 3280, ('SHA', 'WUH'): 2060, ('SHA', 'XIY'): 1520, 
    ('SHA', 'XMN'): 1820, ('SHA', 'ZHA'): 1760, ('SZX', 'HAK'): 1220, 
    ('SZX', 'SYX'): 1120, ('TAO', 'CAN'): 2010, ('TAO', 'CGO'): 930, 
    ('TAO', 'CKG'): 1910, ('TAO', 'CTU'): 1690, ('TAO', 'HAK'): 2300, 
    ('TAO', 'HGH'): 900, ('TAO', 'KMG'): 2660, ('TAO', 'LHW'): 1750, 
    ('TAO', 'NKG'): 1200, ('TAO', 'SYX'): 2640, ('TAO', 'SZX'): 2870, 
    ('TAO', 'WUH'): 1300, ('TAO', 'XIY'): 1510, ('TAO', 'XMN'): 1590, 
    ('TSN', 'CAN'): 2260, ('TSN', 'CKG'): 1540, ('TSN', 'CTU'): 2380, 
    ('TSN', 'FOC'): 1630, ('TSN', 'HAK'): 2470, ('TSN', 'HGH'): 1770, 
    ('TSN', 'KMG'): 2750, ('TSN', 'SHA'): 2120, ('TSN', 'SZX'): 2360, 
    ('TSN', 'URC'): 2780, ('TSN', 'WUH'): 1150, ('TSN', 'XIY'): 1410, 
    ('TSN', 'XMN'): 1900, ('URC', 'CAN'): 3410, ('URC', 'HAK'): 3850, 
    ('URC', 'LHW'): 1920, ('URC', 'SZX'): 3460, ('URC', 'WUH'): 2800, 
    ('URC', 'XIY'): 2660, ('WUH', 'CAN'): 1930, ('WUH', 'HAK'): 1410, 
    ('WUH', 'SYX'): 1690, ('WUH', 'SZX'): 2080, ('WUX', 'CAN'): 1540, 
    ('WUX', 'CKG'): 1410, ('WUX', 'CTU'): 2090, ('WUX', 'KMG'): 2640, 
    ('WUX', 'SZX'): 1690, ('XIY', 'CAN'): 1850, ('XIY', 'HAK'): 2210, 
    ('XIY', 'LXA'): 2500, ('XIY', 'SYX'): 2660, ('XIY', 'SZX'): 2380, 
    ('XMN', 'CAN'): 1670, ('XMN', 'CKG'): 1840, ('XMN', 'CTU'): 2060, 
    ('XMN', 'HAK'): 1180, ('XMN', 'KMG'): 2170, ('XMN', 'LHW'): 2150, 
    ('XMN', 'URC'): 3730, ('XMN', 'WUH'): 990, ('XMN', 'XIY'): 2270, 
    ('PEK', 'CGQ'): 2000, ('PEK', 'CSX'): 1780, ('PEK', 'HFE'): 1710, 
    ('PEK', 'INC'): 1410, ('CAN', 'INC'): 2030, ('CGQ', 'CAN'): 3010, 
    ('CGQ', 'CKG'): 2560, ('CGQ', 'CSX'): 2250, ('CGQ', 'CTU'): 2700, 
    ('CGQ', 'HAK'): 3410, ('CGQ', 'HGH'): 2140, ('CGQ', 'NKG'): 1550, 
    ('CGQ', 'SHA'): 1850, ('CGQ', 'SJW'): 1360, ('CGQ', 'SYX'): 3310, 
    ('CGQ', 'SZX'): 3320, ('CGQ', 'TAO'): 1130, ('CGQ', 'WUH'): 2040, 
    ('CGQ', 'XIY'): 1910, ('CGQ', 'XMN'): 2430, ('CSX', 'CKG'): 1400, 
    ('CSX', 'CTU'): 1470, ('CSX', 'DLC'): 1790, ('CSX', 'KMG'): 1400, 
    ('CSX', 'TAO'): 1620, ('CSX', 'URC'): 3270, ('CSX', 'XIY'): 1500, 
    ('HFE', 'CAN'): 1290, ('HFE', 'CKG'): 1210, ('HFE', 'CTU'): 1430, 
    ('HFE', 'KMG'): 2100, ('HFE', 'SZX'): 1190, ('HRB', 'CSX'): 2250, 
    ('HRB', 'HFE'): 1840, ('NKG', 'CSX'): 970, ('SHA', 'CSX'): 2200, 
    ('SHA', 'INC'): 1980, ('SHA', 'KMG'): 2340, ('SHE', 'CAN'): 2730, 
    ('SHE', 'CGO'): 1380, ('SHE', 'CKG'): 2250, ('SHE', 'CSX'): 2100, 
    ('SHE', 'CTU'): 2690, ('SHE', 'CZX'): 1340, ('SHE', 'HAK'): 2880, 
    ('SHE', 'HGH'): 2180, ('SHE', 'KMG'): 3200, ('SHE', 'NKG'): 1640, 
    ('SHE', 'SHA'): 2030, ('SHE', 'SYX'): 3410, ('SHE', 'SZX'): 3300, 
    ('SHE', 'TAO'): 1150, ('SHE', 'URC'): 2940, ('SHE', 'WUH'): 1830, 
    ('SHE', 'WUX'): 1390, ('SHE', 'XIY'): 1840, ('SHE', 'XMN'): 2150, 
    ('SJW', 'CAN'): 1790, ('SJW', 'SHA'): 1200, ('SYX', 'CSX'): 1890, 
    ('TSN', 'CSX'): 1390, ('SHE', 'SJW'): 920, ('SHE', 'HFE'): 1610, 
    ('SHE', 'FOC'): 1980, ('HRB', 'SJW'): 1490, ('CGQ', 'WUX'): 1940, 
    ('CGQ', 'HFE'): 1700, ('CGQ', 'KMG'): 3540, ('CGQ', 'FOC'): 2210, 
    ('CGQ', 'CGO'): 1700, ('SJW', 'NKG'): 1040, ('SJW', 'HGH'): 1650, 
    ('SJW', 'SYX'): 2620, ('SJW', 'HAK'): 2230, ('SJW', 'XMN'): 1760, 
    ('SJW', 'CTU'): 1830, ('SJW', 'CKG'): 1310, ('SJW', 'KMG'): 2030, 
    ('SJW', 'LHW'): 1180, ('SJW', 'URC'): 2610, ('SJW', 'FOC'): 1600, 
    ('NKG', 'INC'): 1650, ('HGH', 'CSX'): 970, ('HGH', 'INC'): 1740, 
    ('WUX', 'CSX'): 1370, ('HFE', 'SYX'): 2100, ('HFE', 'HAK'): 1990, 
    ('HFE', 'XMN'): 940, ('HFE', 'URC'): 2840, ('HFE', 'TAO'): 800, 
    ('HFE', 'DLC'): 1220, ('HAK', 'CSX'): 1410, ('CSX', 'LHW'): 1680, 
    ('CSX', 'INC'): 1630, ('CTU', 'INC'): 1260, ('CKG', 'INC'): 1230, 
    ('INC', 'URC'): 1730, ('INC', 'TAO'): 1550, ('INC', 'CGO'): 1040, 
    ('KWE', 'PEK'): 1980, ('KWE', 'HRB'): 2730, ('KWE', 'SHA'): 1850, 
    ('KWE', 'NKG'): 1560, ('KWE', 'HGH'): 1700, ('KWE', 'CAN'): 1510, 
    ('KWE', 'XIY'): 1010, ('KWE', 'FOC'): 1620, ('WGN', 'CSX'): 880, 
    ('HYN', 'KMG'): 2380, ('SHE', 'NTG'): 1450, ('XNN', 'URC'): 1930, 
    ('XIY', 'UYN'): 1200, ('SZX', 'YTY'): 1550, ('XMN', 'JNG'): 1330, 
    ('KOW', 'XMN'): 900, ('URC', 'MIG'): 2180, ('CAN', 'XNN'): 2680, 
    ('XNN', 'PEK'): 2500, ('SYX', 'XNN'): 2750, ('BPE', 'SJW'): 1100, 
    ('TYN', 'HGH'): 1360, ('SHA', 'TYN'): 1550, ('YIH', 'TYN'): 940, 
    ('HGH', 'YIH'): 1100, ('RIZ', 'WUH'): 950, ('YNT', 'CTU'): 1840, 
    ('YIW', 'SYX'): 1800, ('KMG', 'WNH'): 770, ('LNJ', 'KMG'): 1210, 
    ('NKG', 'MIG'): 1700, ('LJG', 'CTU'): 1280, ('NTG', 'HRB'): 1840, 
    ('CSX', 'LXA'): 2640, ('PEK', 'YIH'): 1500, ('WEH', 'CTU'): 1900, 
    ('NTG', 'CGO'): 960, ('CGQ', 'ZUH'): 2860, ('CGQ', 'YTY'): 1540, 
    ('LYG', 'CGQ'): 1200, ('KWE', 'HAK'): 1530, ('CAN', 'PEK'): 2540, 
    ('CAN', 'PKX'): 2310, ('CKG', 'PEK'): 2380, ('CKG', 'PKX'): 2610, 
    ('CTU', 'PEK'): 2690, ('TFU', 'PEK'): 2690, ('CTU', 'PKX'): 2230, 
    ('TFU', 'PKX'): 2450, ('DLC', 'PEK'): 1230, ('DLC', 'PKX'): 1230, 
    ('FOC', 'PEK'): 2680, ('FOC', 'PKX'): 2220, ('HAK', 'PEK'): 3810, 
    ('HAK', 'PKX'): 3160, ('HGH', 'PEK'): 2200, ('HGH', 'PKX'): 2420, 
    ('HRB', 'PEK'): 1870, ('HRB', 'PKX'): 1700, ('JJN', 'PEK'): 1900, 
    ('JJN', 'PKX'): 1730, ('KMG', 'PEK'): 3080, ('KMG', 'PKX'): 3080, 
    ('LHW', 'PEK'): 2210, ('LHW', 'PKX'): 2010, ('LXA', 'PEK'): 3260, 
    ('NKG', 'PEK'): 2230, ('NKG', 'PKX'): 2230, ('SHA', 'PEK'): 1960, 
    ('PVG', 'PEK'): 1960, ('SHA', 'PKX'): 1790, ('PVG', 'PKX'): 1790, 
    ('SWA', 'PEK'): 1910, ('SWA', 'PKX'): 1910, ('SYX', 'PEK'): 4040, 
    ('SYX', 'PKX'): 3680, ('SZX', 'PEK'): 2750, ('SZX', 'PKX'): 3020, 
    ('URC', 'PEK'): 3170, ('URC', 'PKX'): 2890, ('WUH', 'PEK'): 2070, 
    ('WUH', 'PKX'): 2290, ('WUX', 'PEK'): 2320, ('WUX', 'PKX'): 2700, 
    ('XIY', 'PEK'): 2030, ('XIY', 'PKX'): 2450, ('XMN', 'PEK'): 2330, 
    ('XMN', 'PKX'): 2810, ('HAK', 'CAN'): 2070, ('SYX', 'CAN'): 1770, 
    ('CKG', 'CGO'): 1160, ('CTU', 'CGO'): 1340, ('TFU', 'CGO'): 1470, 
    ('FOC', 'CGO'): 1250, ('HAK', 'CGO'): 2020, ('HGH', 'CGO'): 1030, 
    ('JJN', 'CGO'): 1490, ('KMG', 'CGO'): 1880, ('SHA', 'CGO'): 1690, 
    ('PVG', 'CGO'): 1690, ('SYX', 'CGO'): 2710, ('SZX', 'CGO'): 1960, 
    ('URC', 'CGO'): 3090, ('XMN', 'CGO'): 1490, ('CAN', 'CKG'): 1990, 
    ('HAK', 'CKG'): 1580, ('KMG', 'CKG'): 900, ('LXA', 'CKG'): 2490, 
    ('SWA', 'CKG'): 1590, ('SYX', 'CKG'): 2030, ('SZX', 'CKG'): 1770, 
    ('URC', 'CKG'): 2500, ('WUH', 'CKG'): 1500, ('CAN', 'CTU'): 1890, 
    ('CAN', 'TFU'): 2070, ('HAK', 'CTU'): 2540, ('HAK', 'TFU'): 2540, 
    ('KMG', 'CTU'): 1700, ('KMG', 'TFU'): 1410, ('LHW', 'CTU'): 1220, 
    ('LHW', 'TFU'): 1110, ('LXA', 'TFU'): 2360, ('SYX', 'CTU'): 1840, 
    ('SYX', 'TFU'): 1840, ('SZX', 'CTU'): 1780, ('SZX', 'TFU'): 1780, 
    ('URC', 'CTU'): 2600, ('URC', 'TFU'): 2860, ('WUH', 'CTU'): 1340, 
    ('WUH', 'TFU'): 1470, ('TFU', 'CZX'): 1600, ('SZX', 'CZX'): 1690, 
    ('CAN', 'DLC'): 2400, ('CGO', 'DLC'): 1040, ('CKG', 'DLC'): 2140, 
    ('TFU', 'DLC'): 2130, ('HGH', 'DLC'): 1360, ('SHA', 'DLC'): 1360, 
    ('PVG', 'DLC'): 1490, ('SZX', 'DLC'): 2240, ('CKG', 'FOC'): 1940, 
    ('CTU', 'FOC'): 1750, ('TFU', 'FOC'): 1920, ('KMG', 'FOC'): 2480, 
    ('LHW', 'FOC'): 2260, ('WUH', 'FOC'): 880, ('XIY', 'FOC'): 1530, 
    ('CAN', 'HGH'): 1410, ('CKG', 'HGH'): 1510, ('CTU', 'HGH'): 2450, 
    ('TFU', 'HGH'): 2450, ('HAK', 'HGH'): 2130, ('JHG', 'HGH'): 2420, 
    ('KMG', 'HGH'): 2620, ('LHW', 'HGH'): 1930, ('SYX', 'HGH'): 2760, 
    ('SZX', 'HGH'): 1820, ('URC', 'HGH'): 3600, ('XIY', 'HGH'): 1690, 
    ('CAN', 'HRB'): 3130, ('CGO', 'HRB'): 1660, ('CTU', 'HRB'): 2530, 
    ('TFU', 'HRB'): 3050, ('FOC', 'HRB'): 2580, ('HAK', 'HRB'): 3660, 
    ('HGH', 'HRB'): 2030, ('KMG', 'HRB'): 3730, ('NKG', 'HRB'): 1910, 
    ('SHA', 'HRB'): 2880, ('PVG', 'HRB'): 2390, ('SYX', 'HRB'): 4200, 
    ('SZX', 'HRB'): 2790, ('TAO', 'HRB'): 1420, ('TSN', 'HRB'): 1500, 
    ('WUH', 'HRB'): 2250, ('XIY', 'HRB'): 2170, ('CAN', 'JJN'): 1100, 
    ('CKG', 'JJN'): 1660, ('CTU', 'JJN'): 1920, ('TFU', 'JJN'): 1750, 
    ('CAN', 'KMG'): 1640, ('HAK', 'KMG'): 1310, ('JHG', 'KMG'): 1670, 
    ('LHW', 'KMG'): 2250, ('LXA', 'KMG'): 2260, ('SYX', 'KMG'): 1500, 
    ('SZX', 'KMG'): 2020, ('WUH', 'KMG'): 1820, ('XIY', 'KMG'): 1710, 
    ('CAN', 'LHW'): 2430, ('SZX', 'LHW'): 2310, ('CAN', 'NKG'): 1900, 
    ('CKG', 'NKG'): 1480, ('CTU', 'NKG'): 2590, ('TFU', 'NKG'): 2590, 
    ('FOC', 'NKG'): 840, ('HAK', 'NKG'): 2130, ('JJN', 'NKG'): 930, 
    ('KMG', 'NKG'): 2370, ('LHW', 'NKG'): 1810, ('SYX', 'NKG'): 2590, 
    ('SZX', 'NKG'): 2450, ('URC', 'NKG'): 3080, ('XIY', 'NKG'): 1290, 
    ('XMN', 'NKG'): 1010, ('CAN', 'SHA'): 2140, ('CAN', 'PVG'): 2140, 
    ('CKG', 'SHA'): 2050, ('CKG', 'PVG'): 1870, ('CTU', 'SHA'): 2330, 
    ('TFU', 'SHA'): 2330, ('CTU', 'PVG'): 2330, ('TFU', 'PVG'): 2330, 
    ('FOC', 'SHA'): 1490, ('FOC', 'PVG'): 1360, ('HAK', 'SHA'): 1920, 
    ('HAK', 'PVG'): 2320, ('JHG', 'PVG'): 2350, ('JJN', 'SHA'): 1230, 
    ('JJN', 'PVG'): 1230, ('LHW', 'SHA'): 2240, ('LHW', 'PVG'): 2030, 
    ('SWA', 'SHA'): 1470, ('SWA', 'PVG'): 1340, ('SYX', 'SHA'): 2880, 
    ('SYX', 'PVG'): 3160, ('SZX', 'SHA'): 1690, ('SZX', 'PVG'): 2030, 
    ('TAO', 'SHA'): 1260, ('TAO', 'PVG'): 1050, ('URC', 'SHA'): 3600, 
    ('URC', 'PVG'): 3280, ('WUH', 'SHA'): 1710, ('WUH', 'PVG'): 2060, 
    ('XIY', 'SHA'): 2010, ('XIY', 'PVG'): 1390, ('XMN', 'SHA'): 1510, 
    ('XMN', 'PVG'): 1510, ('ZHA', 'PVG'): 1760, ('HAK', 'SZX'): 1470, 
    ('CAN', 'TAO'): 2430, ('CKG', 'TAO'): 1740, ('CTU', 'TAO'): 2030, 
    ('TFU', 'TAO'): 2450, ('HGH', 'TAO'): 1410, ('KMG', 'TAO'): 2920, 
    ('NKG', 'TAO'): 1100, ('SYX', 'TAO'): 2610, ('SZX', 'TAO'): 2610, 
    ('WUH', 'TAO'): 1170, ('XIY', 'TAO'): 1380, ('CAN', 'TSN'): 1880, 
    ('CKG', 'TSN'): 1870, ('CTU', 'TSN'): 1970, ('TFU', 'TSN'): 2380, 
    ('HAK', 'TSN'): 2250, ('HGH', 'TSN'): 1610, ('KMG', 'TSN'): 2500, 
    ('SHA', 'TSN'): 2330, ('PVG', 'TSN'): 2330, ('SZX', 'TSN'): 2150, 
    ('WUH', 'TSN'): 1260, ('XIY', 'TSN'): 1180, ('XMN', 'TSN'): 1730, 
    ('LHW', 'URC'): 1750, ('SZX', 'URC'): 3800, ('WUH', 'URC'): 3080, 
    ('XIY', 'URC'): 2420, ('CAN', 'WUH'): 1940, ('HAK', 'WUH'): 1700, 
    ('SYX', 'WUH'): 2230, ('SZX', 'WUH'): 1900, ('CAN', 'WUX'): 1690, 
    ('CTU', 'WUX'): 1900, ('TFU', 'WUX'): 1900, ('KMG', 'WUX'): 2400, 
    ('SZX', 'WUX'): 1400, ('CAN', 'XIY'): 1690, ('HAK', 'XIY'): 2430, 
    ('LXA', 'XIY'): 2280, ('SYX', 'XIY'): 2920, ('SZX', 'XIY'): 2610, 
    ('CAN', 'XMN'): 1520, ('CKG', 'XMN'): 1680, ('CTU', 'XMN'): 1880, 
    ('TFU', 'XMN'): 2060, ('HAK', 'XMN'): 1290, ('KMG', 'XMN'): 1990, 
    ('WUH', 'XMN'): 1080, ('XIY', 'XMN'): 1890, ('CGQ', 'PEK'): 1820, 
    ('CGQ', 'PKX'): 2000, ('CSX', 'PEK'): 1950, ('CSX', 'PKX'): 1780, 
    ('HFE', 'PEK'): 1710, ('HFE', 'PKX'): 1710, ('INC', 'PEK'): 2020, 
    ('INC', 'PKX'): 1410, ('CAN', 'CGQ'): 2740, ('CKG', 'CGQ'): 2330, 
    ('CTU', 'CGQ'): 2460, ('TFU', 'CGQ'): 2460, ('HAK', 'CGQ'): 3100, 
    ('HGH', 'CGQ'): 1950, ('NKG', 'CGQ'): 1700, ('SHA', 'CGQ'): 2230, 
    ('PVG', 'CGQ'): 2030, ('SYX', 'CGQ'): 3640, ('SZX', 'CGQ'): 3650, 
    ('TAO', 'CGQ'): 1240, ('CKG', 'CSX'): 1250, ('CTU', 'CSX'): 1340, 
    ('TFU', 'CSX'): 1470, ('KMG', 'CSX'): 1540, ('TAO', 'CSX'): 1510, 
    ('URC', 'CSX'): 2980, ('XIY', 'CSX'): 1370, ('CAN', 'HFE'): 1180, 
    ('CKG', 'HFE'): 1330, ('CTU', 'HFE'): 1570, ('TFU', 'HFE'): 1570, 
    ('SZX', 'HFE'): 1630, ('CSX', 'HRB'): 2470, ('HFE', 'HRB'): 2020, 
    ('CSX', 'NKG'): 890, ('CSX', 'SHA'): 1820, ('CSX', 'PVG'): 1490, 
    ('INC', 'SHA'): 2170, ('INC', 'PVG'): 1980, ('KMG', 'SHA'): 2820, 
    ('KMG', 'PVG'): 2820, ('CAN', 'SHE'): 2490, ('CKG', 'SHE'): 2050, 
    ('CTU', 'SHE'): 2230, ('TFU', 'SHE'): 2230, ('CZX', 'SHE'): 1360, 
    ('HAK', 'SHE'): 3160, ('HGH', 'SHE'): 1810, ('KMG', 'SHE'): 3520, 
    ('NKG', 'SHE'): 1800, ('PVG', 'SHE'): 2030, ('SYX', 'SHE'): 3100, 
    ('SZX', 'SHE'): 2730, ('TAO', 'SHE'): 800, ('WUH', 'SHE'): 2010, 
    ('WUX', 'SHE'): 1520, ('XIY', 'SHE'): 1680, ('CAN', 'SJW'): 1960, 
    ('SHA', 'SJW'): 1450, ('PVG', 'SJW'): 1200, ('CSX', 'SYX'): 1720, 
    ('CSX', 'TSN'): 1520, ('SJW', 'SHE'): 1210, ('HFE', 'SHE'): 1770, 
    ('FOC', 'SHE'): 2100, ('WUX', 'CGQ'): 1610, ('HFE', 'CGQ'): 1650, 
    ('KMG', 'CGQ'): 2940, ('CGO', 'CGQ'): 1740, ('NKG', 'SJW'): 950, 
    ('HGH', 'SJW'): 1250, ('SYX', 'SJW'): 2880, ('HAK', 'SJW'): 2950, 
    ('CTU', 'SJW'): 2010, ('TFU', 'SJW'): 1670, ('CKG', 'SJW'): 1580, 
    ('KMG', 'SJW'): 2620, ('INC', 'NKG'): 1660, ('CSX', 'HGH'): 1080, 
    ('INC', 'HGH'): 1900, ('CSX', 'WUX'): 1140, ('SYX', 'HFE'): 2310, 
    ('HAK', 'HFE'): 1810, ('XMN', 'HFE'): 860, ('TAO', 'HFE'): 960, 
    ('DLC', 'HFE'): 1110, ('CSX', 'HAK'): 1290, ('LHW', 'CSX'): 1530, 
    ('INC', 'TFU'): 1380, ('INC', 'CKG'): 1480, ('URC', 'INC'): 1900, 
    ('TAO', 'INC'): 1410, ('CGO', 'INC'): 940, ('PEK', 'KWE'): 1980, 
    ('PKX', 'KWE'): 2170, ('SHA', 'KWE'): 2030, ('PVG', 'KWE'): 2030, 
    ('NKG', 'KWE'): 1710, ('HGH', 'KWE'): 1550, ('XIY', 'KWE'): 1460, 
    ('FOC', 'KWE'): 1480, ('URC', 'XNN'): 1760, ('UYN', 'XIY'): 1450, 
    ('PEK', 'XNN'): 2500, ('PKX', 'XNN'): 2280, ('HGH', 'TYN'): 1240, 
    ('TYN', 'SHA'): 1290, ('TYN', 'PVG'): 1700, ('TFU', 'YNT'): 1840, 
    ('CTU', 'LJG'): 1680, ('TFU', 'LJG'): 1280, ('YIH', 'PEK'): 1500, 
    ('YIH', 'PKX'): 1500, ('TFU', 'WEH'): 1900, ('HAK', 'KWE'): 1180
    }

_greatcircle = {
    ('BJS', 'HRB'): 553, ('BJS', 'DLC'): 245, ('BJS', 'SHA'): 575, 
    ('BJS', 'NKG'): 504, ('BJS', 'HGH'): 613, ('BJS', 'WUX'): 541, 
    ('BJS', 'FOC'): 853, ('BJS', 'XMN'): 924, ('BJS', 'JJN'): 912, 
    ('BJS', 'CTU'): 828, ('BJS', 'CKG'): 778, ('BJS', 'XIY'): 492, 
    ('BJS', 'LHW'): 638, ('BJS', 'WUH'): 558, ('BJS', 'SWA'): 980, 
    ('HRB', 'TSN'): 555, ('HRB', 'TAO'): 621, ('HRB', 'CGO'): 876, 
    ('HRB', 'SHA'): 895, ('HRB', 'NKG'): 901, ('HRB', 'HGH'): 963, 
    ('TSN', 'SHA'): 514, ('TSN', 'HGH'): 554, ('TSN', 'FOC'): 798, 
    ('TSN', 'XMN'): 874, ('TSN', 'CTU'): 835, ('TSN', 'CKG'): 773, 
    ('TSN', 'XIY'): 500, ('TSN', 'WUH'): 523, ('TSN', 'CAN'): 964, 
    ('DLC', 'TAO'): 171, ('DLC', 'CGO'): 457, ('DLC', 'SHA'): 466, 
    ('DLC', 'NKG'): 452, ('DLC', 'HGH'): 526, ('DLC', 'FOC'): 786, 
    ('DLC', 'XMN'): 881, ('DLC', 'CKG'): 922, ('DLC', 'WUH'): 609, 
    ('TAO', 'CGO'): 337, ('TAO', 'SHA'): 307, ('TAO', 'NKG'): 281, 
    ('TAO', 'HGH'): 362, ('TAO', 'XMN'): 711, ('TAO', 'CTU'): 891, 
    ('TAO', 'CKG'): 795, ('TAO', 'XIY'): 580, ('TAO', 'LHW'): 811, 
    ('TAO', 'WUH'): 451, ('TAO', 'CAN'): 853, ('TAO', 'SZX'): 884, 
    ('CGO', 'SHA'): 428, ('CGO', 'HGH'): 422, ('CGO', 'FOC'): 596, 
    ('CGO', 'XMN'): 637, ('CGO', 'JJN'): 632, ('CGO', 'CTU'): 554, 
    ('CGO', 'CKG'): 466, ('CGO', 'KMG'): 800, ('CGO', 'LHW'): 514, 
    ('CGO', 'CAN'): 666, ('CGO', 'SZX'): 711, ('CGO', 'HAK'): 891, 
    ('CGO', 'SYX'): 999, ('SHA', 'FOC'): 327, ('SHA', 'XMN'): 433, 
    ('SHA', 'JJN'): 410, ('SHA', 'CTU'): 897, ('SHA', 'CKG'): 767, 
    ('SHA', 'XIY'): 665, ('SHA', 'LHW'): 939, ('SHA', 'WUH'): 368, 
    ('SHA', 'CAN'): 634, ('SHA', 'ZHA'): 840, ('SHA', 'SZX'): 651, 
    ('SHA', 'SWA'): 525, ('SHA', 'HAK'): 894, ('NKG', 'FOC'): 350, 
    ('NKG', 'XMN'): 433, ('NKG', 'JJN'): 416, ('NKG', 'CTU'): 770, 
    ('NKG', 'CKG'): 643, ('NKG', 'KMG'): 930, ('NKG', 'XIY'): 535, 
    ('NKG', 'LHW'): 810, ('NKG', 'CAN'): 581, ('NKG', 'SZX'): 608, 
    ('NKG', 'HAK'): 839, ('NKG', 'SYX'): 954, ('HGH', 'CTU'): 855, 
    ('HGH', 'CKG'): 719, ('HGH', 'KMG'): 980, ('HGH', 'XIY'): 645, 
    ('HGH', 'LHW'): 923, ('HGH', 'CAN'): 560, ('HGH', 'SZX'): 577, 
    ('HGH', 'HAK'): 820, ('HGH', 'SYX'): 934, ('CZX', 'CTU'): 817, 
    ('CZX', 'CAN'): 615, ('CZX', 'SZX'): 640, ('WUX', 'CTU'): 850, 
    ('WUX', 'CKG'): 721, ('WUX', 'CAN'): 616, ('WUX', 'SZX'): 637, 
    ('FOC', 'CTU'): 877, ('FOC', 'CKG'): 728, ('FOC', 'KMG'): 908, 
    ('FOC', 'XIY'): 762, ('FOC', 'WUH'): 409, ('FOC', 'CAN'): 379, 
    ('XMN', 'CTU'): 837, ('XMN', 'CKG'): 688, ('XMN', 'KMG'): 829, 
    ('XMN', 'XIY'): 769, ('XMN', 'WUH'): 427, ('XMN', 'CAN'): 274, 
    ('XMN', 'HAK'): 508, ('JJN', 'CTU'): 852, ('JJN', 'CKG'): 703, 
    ('JJN', 'KMG'): 853, ('JJN', 'CAN'): 302, ('CTU', 'KMG'): 332, 
    ('CTU', 'LHW'): 356, ('CTU', 'LXA'): 684, ('CTU', 'WUH'): 531, 
    ('CTU', 'CAN'): 660, ('CTU', 'SZX'): 711, ('CTU', 'HAK'): 728, 
    ('CTU', 'SYX'): 793, ('CKG', 'KMG'): 339, ('CKG', 'LXA'): 823, 
    ('CKG', 'WUH'): 399, ('CKG', 'CAN'): 521, ('CKG', 'SZX'): 574, 
    ('CKG', 'SWA'): 645, ('CKG', 'HAK'): 621, ('CKG', 'SYX'): 700, 
    ('KMG', 'JHG'): 222, ('KMG', 'XIY'): 636, ('KMG', 'LHW'): 684, 
    ('KMG', 'LXA'): 690, ('KMG', 'WUH'): 688, ('KMG', 'CAN'): 577, 
    ('KMG', 'SZX'): 616, ('KMG', 'SWA'): 749, ('KMG', 'HAK'): 519, 
    ('KMG', 'SYX'): 544, ('URC', 'LHW'): 862, ('XIY', 'LXA'): 960, 
    ('XIY', 'CAN'): 703, ('XIY', 'SZX'): 755, ('XIY', 'HAK'): 873, 
    ('XIY', 'SYX'): 966, ('LHW', 'CAN'): 933, ('LHW', 'SZX'): 986, 
    ('WUH', 'CAN'): 444, ('WUH', 'SZX'): 487, ('WUH', 'HAK'): 680, 
    ('WUH', 'SYX'): 791, ('CAN', 'ZHA'): 210, ('CAN', 'HAK'): 261, 
    ('CAN', 'SYX'): 375, ('SZX', 'HAK'): 248, ('SZX', 'SYX'): 359, 
    ('BJS', 'KMG'): 1117, ('BJS', 'URC'): 1311, ('BJS', 'CAN'): 1002, 
    ('BJS', 'SZX'): 1043, ('BJS', 'HAK'): 1235, ('BJS', 'SYX'): 1344, 
    ('HRB', 'FOC'): 1222, ('HRB', 'XMN'): 1323, ('HRB', 'CTU'): 1380, 
    ('HRB', 'CKG'): 1328, ('HRB', 'KMG'): 1667, ('HRB', 'XIY'): 1045, 
    ('HRB', 'WUH'): 1054, ('HRB', 'CAN'): 1474, ('HRB', 'SZX'): 1506, 
    ('HRB', 'HAK'): 1726, ('HRB', 'SYX'): 1839, ('TSN', 'KMG'): 1112, 
    ('TSN', 'URC'): 1369, ('TSN', 'SZX'): 1003, ('TSN', 'HAK'): 1203, 
    ('DLC', 'CTU'): 1002, ('DLC', 'KMG'): 1256, ('DLC', 'CAN'): 1023, 
    ('DLC', 'SZX'): 1055, ('DLC', 'HAK'): 1276, ('TAO', 'KMG'): 1119, 
    ('TAO', 'HAK'): 1108, ('TAO', 'SYX'): 1222, ('CGO', 'URC'): 1344, 
    ('SHA', 'KMG'): 1040, ('SHA', 'JHG'): 1234, ('SHA', 'URC'): 1770, 
    ('SHA', 'SYX'): 1008, ('NKG', 'URC'): 1647, ('HGH', 'JHG'): 1169, 
    ('HGH', 'URC'): 1766, ('WUX', 'KMG'): 1000, ('FOC', 'LHW'): 1038, 
    ('XMN', 'URC'): 1897, ('CTU', 'URC'): 1119, ('CKG', 'URC'): 1249, 
    ('KMG', 'URC'): 1357, ('URC', 'XIY'): 1138, ('URC', 'WUH'): 1492, 
    ('URC', 'CAN'): 1770, ('URC', 'SZX'): 1823, ('URC', 'HAK'): 1841
    }

skipped_routes = _inactive | _low