import db


def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes


def get_all_classes_with_count():
    sql = """
    SELECT c.title, c.value, count(dc.value) as count
    FROM classes c
    LEFT JOIN destination_classes dc
    ON c.title = dc.title AND c.value = dc.value
    GROUP BY c.title, c.value
    ORDER BY c.id
    """

    result = db.query(sql)

    classes = {}
    for title, value, count in result:
        classes[title] = []
    for title, value, count in result:
        classes[title].append({"value": value, "count": count})

    return classes


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
