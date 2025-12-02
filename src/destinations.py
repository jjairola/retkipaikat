import db


class DestinationError(Exception):
    pass


def add_destination(name, description, municipality, user_id, classes):
    sql = """INSERT INTO destinations (name, description, municipality, user_id)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [name, description, municipality, user_id])

    destination_id = db.last_insert_id()

    sql = "INSERT INTO destination_classes (destination_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [destination_id, class_title, class_value])


def get_destinations(
    user_id=None, destination_id=None, query_text=None, query_class=None
):
    sql = """
    SELECT d.id, d.name, d.description, d.municipality,
            GROUP_CONCAT(dc.title || ':' || dc.value, ';') classes,
            SUM(c.rating) / COUNT(c.id) as average_rating
    FROM destinations d
    LEFT JOIN destination_classes dc ON d.id = dc.destination_id
    LEFT JOIN comments c ON d.id = c.destination_id
    """

    # where(s)

    params = []
    if user_id is not None:
        sql += "WHERE d.user_id = ? "
        params = [user_id]

    if destination_id is not None:
        sql += "WHERE d.id = ? "
        params = [destination_id]

    if query_text is not None:
        sql += "WHERE (d.name LIKE ? OR d.description LIKE ?) "
        params = [f"%{query_text}%", f"%{query_text}%"]

    if query_class is not None:
        sql += "WHERE dc.title = ? AND dc.value = ? "
        params = [query_class["title"], query_class["value"]]

    sql += """
    GROUP BY d.id
    ORDER BY average_rating DESC
    """

    rows = db.query(sql, params)

    results = []
    for row in rows:
        result = dict(row)
        if row["classes"]:
            classes = row["classes"].split(";")
            class_dict = {}
            for class_item in classes:
                if class_item == "":
                    continue
                title, value = class_item.split(":")
                print(title)
                print(value)
                class_dict[title] = value
            result["classes"] = class_dict
        else:
            result["classes"] = {}
        results.append(result)

    return results


def get_destination(destination_id):
    result = get_destinations(destination_id=destination_id)
    return result[0] if result else None


def search_destinations_by_query(query: str):
    result = get_destinations(query_text=query)
    return result


def search_destionations_by_class(title, value):
    result = get_destinations(query_class={"title": title, "value": value})
    return result


def get_destination_classes(destination_id):
    sql = "SELECT title, value FROM destination_classes WHERE destination_id = ?"
    return dict(db.query(sql, [destination_id]))

def update_destination(destination_id, name, description, municipality, classes):
    sql = """UPDATE destinations SET name = ?, description = ?, municipality = ? WHERE id = ?"""
    db.execute(sql, [name, description, municipality, destination_id])

    sql = "DELETE FROM destination_classes WHERE destination_id = ?"
    db.execute(sql, [destination_id])

    sql = "INSERT INTO destination_classes (destination_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [destination_id, class_title, class_value])


def delete_destination(destination_id):
    sql = "DELETE FROM comments WHERE destination_id = ?"
    db.execute(sql, [destination_id])

    sql = "DELETE FROM destination_classes WHERE destination_id = ?"
    db.execute(sql, [destination_id])

    sql = "DELETE FROM destinations WHERE id = ?"
    db.execute(sql, [destination_id])


def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes
