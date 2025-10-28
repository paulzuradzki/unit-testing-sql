import sqlparse


def format_sql(sql: str) -> str:
    """
    Format the SQL query.
    """
    return sqlparse.format(
        sql,
        reindent=True,
        keyword_case="upper",
        identifier_case="lower",
        compact=True,
        strip_comments=True,
        strip_whitespace=True,
        wrap_after=80,
    )
