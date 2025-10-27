import psycopg2
import dotenv
import os
from importlib.resources import files


def main():
    dotenv.load_dotenv()

    conn = psycopg2.connect(os.environ["DATABASE_URL"])

    data = pivot_and_sum(conn)
    return data


def pivot_and_sum(conn: psycopg2.connect, mock_cte: str = "") -> dict[str, int]:
    """
    Execute pivot query on orders data.

    Args:
        conn: Database connection
        mock_cte: SQL CTE to prepend for testing. WARNING: Never pass user input.
                 Must be empty or start with 'with'. Used only for controlled test mocks.

    Returns:
        List of dicts with pivoted sales data by region
    """
    # Validate mock_cte to prevent SQL injection
    if mock_cte and not mock_cte.strip().lower().startswith("with"):
        raise ValueError("mock_cte must be empty or start with 'with'")

    sql = files("app.sql").joinpath("etl.sql").read_text()

    # Prepend mock CTE if provided, replacing "with" in original query with comma
    if mock_cte:
        # Remove trailing newline/whitespace and add comma separator
        mock_cte = mock_cte.rstrip() + ","
        # Replace first occurrence of "with" with the mock CTE
        sql = sql.replace("with ", mock_cte + "\n", 1)
    with conn.cursor() as cur:
        cur.execute(sql)
        cols = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        data = [dict(zip(cols, row)) for row in rows]

    return data


if __name__ == "__main__":
    main()
