import db


def get_default_icons():
    sql = """
    SELECT title, value, default_icon FROM classes
    WHERE default_icon IS NOT NULL
    """

    rows = db.query(sql)
    result = {}

    for row in rows:
        if row["title"] not in result:
            result[row["title"]] = {}
        result[row["title"]][row["value"]] = row["default_icon"]

    return result
