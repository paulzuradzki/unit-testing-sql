import psycopg2
from importlib.resources import files
from app.format import format_sql


def pivot_and_sum(conn: psycopg2.connect, verbose: bool = False) -> dict[str, int]:
    """
    Execute pivot query on orders data.
    """
    sql = files("app").joinpath("sql/pivot.sql").read_text()
    if verbose:
        print(format_sql(sql))
    return _pivot_and_sum(conn, sql)


def _pivot_and_sum(conn: psycopg2.connect, sql: str) -> dict[str, int]:
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


def pivot_and_unpivot(conn: psycopg2.connect, verbose: bool = False) -> dict[str, int]:
    """
    Execute pivot and unpivot query on orders data.
    """
    sql = files("app").joinpath("sql/pivot_and_unpivot.sql").read_text()
    if verbose:
        print(format_sql(sql))
    return _pivot_and_unpivot(conn, sql)


def _pivot_and_unpivot(conn: psycopg2.connect, sql: str) -> dict[str, int]:
    """
    Unpivot the pivoted data.
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        data = [dict(zip(cols, row)) for row in rows]

    return data
