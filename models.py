from osgeo import ogr
from itertools import chain


def get_wkt_line(coords: list) -> str:
    """
    transforms list of coordinates list([x, y]) to WKT string (LineString)
    :param coords: list of lists with len==2, e.g. [[x, y], [x, y]...]
    :return: str
    """
    line = ogr.Geometry(ogr.wkbLineString)
    if len(coords) == 1:
        coords = list(chain(*coords))
    for i in coords:
        line.AddPoint(i[0], i[1])
    return line.ExportToWkt()


class Category:
    def __init__(self, _id, checked, parent, name):
        self._id = _id
        self.checked = checked
        self.parent = parent
        self.name = name


class Parking:
    def __init__(self, data: dict):
        self.category = data['category']['_id']
        self._id = data['_id']
        self.street = data['address']['street']['ru']
        self.house = data['address']['house']['ru']
        self.wkt = get_wkt_line(data['location']['coordinates'])
        self.name = data['name']['ru']
        self.space = data['spaces']['total']
        if 'handicapped' in data['spaces'].keys():
            self.handicapped = data['spaces']['handicapped']
        else:
            self.handicapped = 0
        if 'congestion' in data.keys():
            self.congestion = data['congestion']['rawInfo']['occupied']
            self.congestion_time = data['congestion']['updateDate']
        else:
            self.congestion = None
            self.congestion_time = None
        if 'zone' in data.keys():
            self.description = data['zone']['description']['ru']
            if 'prices' in data['zone'].keys():
                self.car_price_min = data['zone']['prices'][0]['price']['min'] / 100
                self.car_price_max = data['zone']['prices'][0]['price']['max'] / 100
        else:
            self.description = None
            self.car_price_max = None
            self.car_price_min = None
