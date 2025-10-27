from pprint import pprint
from app.transform import pivot_and_sum
import dotenv
import os
import psycopg2

dotenv.load_dotenv()
conn = psycopg2.connect(os.environ["DATABASE_URL"])
data = pivot_and_sum(conn)

pprint(data, sort_dicts=False)