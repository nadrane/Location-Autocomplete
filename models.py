from collections import namedtuple


class Location(namedtuple('Location', ['line_no', 'zip_code', 'latitude',
                                       'longitude', 'primary_city', 'state',
                                       'estimated_population'])):
    __slots__ = ()

    def __hash__(self):
        return hash((self.primary_city, self.state))


class Alias(namedtuple('Alias', ['line_no', 'zip_code', 'primary_city',
                                 'state', 'estimated_population'])):

    __slots__ = ()

    def __hash__(self):
        return hash((self.primary_city, self.state))
