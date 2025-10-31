from pprint import pprint
from app.transform import sum_and_pivot
import dotenv
import os
import psycopg2


def main():
    """Main function to run the pivot and sum transformation."""
    dotenv.load_dotenv()
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    data = sum_and_pivot(conn, verbose=True)

    print("\n--------------------------------\n")
    pprint(data, sort_dicts=False)
    return data


if __name__ == "__main__":
    main()
