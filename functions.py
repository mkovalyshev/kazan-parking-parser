import datetime
from models import Category, Parking
import sqlalchemy
import requests
import pandas as pd

BASE = "https://parkingkzn.ru"
API = "/api/2.49/"
PARKING_METHOD = "parkings/"
CATEGORY_METHOD = "categories/"
TERMINAL_METHOD = "terminals/"
SCOREBOARD_METHOD = "scoreboards/"
PARKOMAT_METHOD = "parkomats/"


def get_categories(pg_engine: sqlalchemy.engine) -> None:
    """
    gets categories from parkingkzn.ru
    loads into database
    :param pg_engine: sqlalchemy.engine
    :return: None
    """
    response = requests.get(BASE + API + CATEGORY_METHOD)
    categories = []
    ids = []
    categories_json = sorted(response.json()['categories'], key=lambda x: x['_id'])
    categories_json = {body['_id']: body for body in categories_json}
    for key in categories_json.keys():
        del categories_json[key]['_id']
        if key not in ids:
            parent = Category(_id=key,
                              checked=categories_json[key]['checked'],
                              parent=None,
                              name=categories_json[key]['name']['ru'])
            ids.append(key)
            categories.append(parent)
            if 'children' in categories_json[key].keys():
                for child in categories_json[key]['children']:
                    ids.append(child)
                    categories.append(Category(child,
                                               categories_json[child]['checked'],
                                               key,
                                               categories_json[child]['name']['ru']))

    categories_df = pd.DataFrame([category.__dict__ for category in categories])

    categories_df['parent'] = categories_df['parent'].astype(pd.Int64Dtype())
    categories_df.rename(columns={'_id': 'id'}, inplace=True)

    categories_df.to_sql('categories',
                         pg_engine,
                         schema='parking',
                         if_exists='append',
                         index=False)


def get_parking_data(pg_engine):
    """
    gets parking info from parkingkzn.ru
    loads into database
    :param pg_engine: sqlalchemy.engine
    :return: None
    """
    response = requests.get(BASE + API + PARKING_METHOD)
    parkings_json = response.json()['parkings']
    parkings = []
    for parking in parkings_json:
        parkings.append(Parking(parking))

    parkings_df = pd.DataFrame([parking.__dict__ for parking in parkings])

    parkings_df.rename(columns={'_id': 'id',
                                'wkt': 'geometry'}, inplace=True)
    parkings_df['congestion'] = parkings_df['congestion'].astype(pd.Int64Dtype())
    parkings_df['car_price_min'] = parkings_df['car_price_min'].astype(pd.Int64Dtype())
    parkings_df['car_price_max'] = parkings_df['car_price_max'].astype(pd.Int64Dtype())
    parkings_df['upload_date'] = datetime.datetime.today()

    parkings_df['name'] = parkings_df['name'].replace({'': None})

    parkings_df = parkings_df[['id',
                               'category',
                               'street',
                               'house',
                               'name',
                               'space',
                               'handicapped',
                               'congestion',
                               'congestion_time',
                               'description',
                               'car_price_min',
                               'car_price_max',
                               'geometry',
                               'upload_date']]

    parkings_df.to_sql('parking_lots',
                       pg_engine,
                       schema='parking',
                       if_exists='append',
                       index=False)
