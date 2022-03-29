__all__ = ('Airport', 'Route', 'skipped_routes', 'airport_throughput', 'city_class', 'city_location', 'tourism')

from warnings import warn
from database import _airfare, _city, _greatcircle, _iata, _icao, _multi, _inactive, _low, \
    city_class, city_location, tourism, airport_throughput
skipped_routes = _inactive | _low

class Airport:
    '''
    Support IATA/ICAO Code and airport name input
    Note: `code` is the primary airport of multi airport cities, except `BJS` == `PEK`
    '''
    __slots__ = (
        'icao', 'iata', 'city', 'airport', 'city_eng', 'airport_eng', 
        'latitude', 'longitude', 'type', 'code', 'multi')
    
    iata: str
    icao: str
    code: str
    city: str
    airport: str
    city_eng: str
    airport_eng: str
    type: str
    latitude: float
    longitude: float
    multi: bool
    
    def __new__(cls, __str):
        self = object.__new__(cls)
        if isinstance(__str, str):
            if __str in {'北京', '上海', '成都', '台北'}:
                msg = '\ninput specific airport for multi airport cities, '
                warn(msg + f'setting primary airport: {_city.get(__str, __str)}', Warning, 2)
            if _city.get(__str):
                __str = _city.get(__str)
            elif _icao.get(__str):
                __str = _icao.get(__str)
            __str = __str.upper()
            if __str in _iata.keys():
                self.iata = __str
                self.icao, self.city, self.airport, self.city_eng, self.airport_eng, \
                    self.latitude, self.longitude, self.type = _iata.get(__str)
                self.code = 'BJS' if __str == 'PEK' or __str == 'PKX' \
                    else 'SHA' if __str == 'PVG' else 'CTU' if __str == 'TFU' \
                        else 'TPE' if __str == 'TSA' else __str
                self.multi = self.code in _multi
            else:
                raise ValueError(
                    "No such airport found,", 
                    "add a new one manually using 'add' method.")
            return self
        else:
            raise TypeError(
                "Code string or city name string required,", 
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
            return True if other == 'BJS' and self.iata == 'PEK' else self.icao == other or \
                self.iata == other or (self.city in other and self.airport in other) or \
                (self.city_eng.lower() in other.lower() and self.airport_eng.lower() in other.lower())
        else:
            return False
    
    def __hash__(self):
        return hash(self.iata.encode())
    
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
        return "{0}.{1}('{2}': ('{3}', '{4}{5}', ...))".format(
            self.__class__.__module__, 
            self.__class__.__qualname__, 
            self.iata, self.icao, self.city, self.airport)
    
    def __str__(self):
        return self.city + self.airport if self.city in _multi else self.city
    
    @classmethod
    def add(cls, iata: str, city: str, **kwargs):
        '''
        Add an aiport by iata code and city (least required)
        `**kwargs`: icao, airport, city_eng, airport_eng, latitude, longitude, type
        '''
        self = object.__new__(cls)
        self.iata, self.city = iata, city
        self.icao, self.airport = kwargs.get('icao', ''), kwargs.get('airport', '')
        self.city_eng, self.airport_eng = kwargs.get('city_eng', ''), kwargs.get('airport_eng', '')
        self.latitude, self.longitude = kwargs.get('latitude', -1), kwargs.get('longitude', -1)
        self.type = kwargs.get('type', '')
        self.code = 'BJS' if iata == 'PEK' or iata == 'PKX' else 'SHA' \
            if iata == 'PVG' else 'CTU' if iata == 'TFU' else iata
        self.multi = self.city in _city.keys()
        return self
    
    @property
    def separates(self) -> tuple:
        'iata, icao, city, airport name, city, airport name, latitude, longitude, type, code'
        return self.iata, self.icao, self.city, self.airport, self.city_eng, self.airport_eng, \
            self.latitude, self.longitude, self.type, self.code


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
    def fromformat(cls, __str, /, *, sep: str = '-'):
        return cls(*(__str.split(sep, 1)))
    
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
            if __oneway:
                return cmp
            else:
                return cmp or (self.arr.citycmp(__other.dep) and self.dep.citycmp(__other.arr))
        elif isinstance(__other, str):
            return self.citycmp(Route(__other, __oneway))
        else:
            return False
    
    def __repr__(self):
        return "{0}.{1}('{2}-{3}': {4}, {5})".format(
            self.__class__.__module__, self.__class__.__qualname__, 
            self.dep, self.arr, self.airfare, self.greatcircle)
    
    def __str__(self):
        return f"{self.dep}-{self.arr}"
    
    def __hash__(self):
        return hash(self.format('iata').encode())
    
    def format(self, key: str = 'code', sep: str = '-'):
        if key == 'airport':
            return f"{self.dep.city}{self.dep.airport}{sep}{self.arr.city}{self.arr.airport}"
        elif key == 'airport_eng':
            _d, _a = self.dep.airport_eng, self.arr.airport_eng
            return f"{self.dep.city_eng} {_d}" if len(_d) else self.dep.city_eng + \
                sep + f"{self.arr.city_eng} {_a}" if len(_a) else self.arr.city_eng 
        else:
            return f"{eval(f'self.dep.{key}')}{sep}{eval(f'self.arr.{key}')}"
    
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

