from functions import *
import yaml
from sqlalchemy import create_engine

with open('config.yaml') as f:
    CONFIG = yaml.load(f, Loader=yaml.FullLoader)

pg_engine = create_engine(f'postgresql+psycopg2://postgres:{CONFIG["db_pass"]}@localhost/postgres')

if len(pd.read_sql("select * from parking.categories", pg_engine)) == 0:
    get_categories(pg_engine)

get_parking_data(pg_engine)
