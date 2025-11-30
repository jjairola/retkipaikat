import db

class DestinationError(Exception):
    pass


def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes


def add_destination(name, description, municipality, user_id, classes):
    sql = """INSERT INTO destinations (name, description, municipality, user_id)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [name, description, municipality, user_id])

    destination_id = db.last_insert_id()

    sql = "INSERT INTO destination_classes (destination_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [destination_id, class_title, class_value])


def get_destinations_by_user(user_id):
    sql = """
    SELECT d.id, d.name, d.description, d.municipality, GROUP_CONCAT(dc.title) classes
    FROM destinations d
    LEFT JOIN destination_classes dc ON d.id = dc.destination_id
    WHERE d.user_id = ?
    GROUP BY d.id
    ORDER BY d.id
    """
    return db.query(sql, [user_id])


def get_destinations():
    sql = """
    SELECT d.id, d.name, d.description, d.municipality, 
            GROUP_CONCAT(dc.title || ':' || dc.value, ';') classes,
            SUM(c.rating) / COUNT(c.id) as average_rating
    FROM destinations d
    LEFT JOIN destination_classes dc ON d.id = dc.destination_id
    LEFT JOIN comments c ON d.id = c.destination_id
    GROUP BY d.id
    ORDER BY average_rating DESC
    """

    rows = db.query(sql)

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
    sql = """
    SELECT d.id, d.name, d.description, d.municipality, u.username, u.id as user_id
    FROM destinations d
    JOIN users u ON d.user_id = u.id
    WHERE d.id = ?
    """
    result = db.query(sql, [destination_id])
    return result[0] if result else None


def search_destinations_by_query(query: str):
    sql = """
    SELECT d.id, d.name, d.description, d.municipality
    FROM destinations d
    WHERE (d.name LIKE ? OR d.description LIKE ?)
    """
    return db.query(sql, [f"%{query}%", f"%{query}%"])


def get_destinations_by_class(title, value):
    sql = """
    SELECT d.id, d.name, d.description, d.municipality
    FROM destinations d
    JOIN destination_classes dc ON d.id = dc.destination_id
    WHERE dc.title = ? AND dc.value = ?
    """
    return db.query(sql, [title, value])


def get_destination_classes(destination_id):
    sql = "SELECT title, value FROM destination_classes WHERE destination_id = ?"
    return dict(db.query(sql, [destination_id]))


def get_destination_classifications_ids(destination_id):
    sql = """
    SELECT classification_id
    FROM destination_classifications
    WHERE destination_id = ?
    """
    result = db.query(sql, [destination_id])
    return [row["classification_id"] for row in result]


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
