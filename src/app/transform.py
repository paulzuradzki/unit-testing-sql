import psycopg2
import dotenv
import os
from importlib.resources import files


def main():
    dotenv.load_dotenv()

    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    sql = files("app").joinpath("sql/transform.sql").read_text()

    data = pivot_and_sum(conn, sql)
    return data


def pivot_and_sum(conn: psycopg2.connect, sql: str) -> dict[str, int]:
    """
    Execute pivot query on orders data.

    Args:
        conn: Database connection
        sql: SQL query to execute

    Returns:
        List of dicts with pivoted sales data by region
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        data = [dict(zip(cols, row)) for row in rows]

    return data


if __name__ == "__main__":
    main()
