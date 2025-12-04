import db


class DestinationError(Exception):
    pass


def add_destination(name, description, user_id, classes):
    try:
        sql = """INSERT INTO destinations (name, description, user_id)
                VALUES (?, ?, ?)"""
        db.execute(sql, [name, description, user_id])

        destination_id = db.last_insert_id()

        sql = "INSERT INTO destination_classes (destination_id, title, value) VALUES (?, ?, ?)"
        for class_title, class_value in classes:
            db.execute(sql, [destination_id, class_title, class_value])
        
        return destination_id
    except Exception as e:
        raise DestinationError(e)


def destination_count():
    sql = """
    SELECT COUNT(d.id) as count from destinations d
    """
    result = db.query(sql)
    return result[0]["count"]


def get_destinations(
    user_id=None,
    destination_id=None,
    query_text=None,
    query_class=None,
    page=None,
    page_size=None,
):
    sql = """
    SELECT d.id, d.name, d.description,
            d.user_id, u.username,
            GROUP_CONCAT(dc.title || ':' || dc.value, ';') classes,
            rc.average_rating,
            di.image IS NOT NULL AS has_image
    FROM destinations d
    JOIN users u ON d.user_id = u.id
    LEFT JOIN ratings_cache rc ON d.id = rc.destination_id
    LEFT JOIN destination_classes dc ON d.id = dc.destination_id
    LEFT JOIN comments c ON d.id = c.destination_id
    LEFT JOIN destination_images di ON d.id = di.destination_id
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

    if page is not None and page_size is not None:
        limit = page_size
        offset = page_size * (page - 1)

        sql += "LIMIT ? OFFSET ?"
        params = [limit, offset]

    rows = db.query(sql, params)

    print(dict(rows[0]))

    results = []
    for row in rows:
        result = dict(row)
        print(">")
        print(dict(row))
        if "classes" in row.keys():
            classes = row["classes"].split(";")
            class_dict = {}
            for class_item in classes:
                if class_item == "":
                    continue
                title, value = class_item.split(":")
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


def search_destinations_by_class(title, value):
    result = get_destinations(query_class={"title": title, "value": value})
    return result


def get_destination_classes(destination_id):
    sql = "SELECT title, value FROM destination_classes WHERE destination_id = ?"
    return dict(db.query(sql, [destination_id]))


def update_destination(destination_id, name, description, classes):
    try:
        sql = """UPDATE destinations SET name = ?, description = ? WHERE id = ?"""
        db.execute(sql, [name, description, destination_id])

        sql = "DELETE FROM destination_classes WHERE destination_id = ?"
        db.execute(sql, [destination_id])

        sql = "INSERT INTO destination_classes (destination_id, title, value) VALUES (?, ?, ?)"
        for class_title, class_value in classes:
            db.execute(sql, [destination_id, class_title, class_value])
    except Exception as e:
        raise DestinationError(e)


def delete_destination(destination_id):
    try:
        sql = "DELETE FROM comments WHERE destination_id = ?"
        db.execute(sql, [destination_id])

        sql = "DELETE FROM destination_classes WHERE destination_id = ?"
        db.execute(sql, [destination_id])

        sql = "DELETE FROM destinations WHERE id = ?"
        db.execute(sql, [destination_id])
    except Exception as e:
        raise DestinationError(e)


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
        classes[title].append({ "value": value, "count": count })

    return classes

def get_image(user_id):
    sql = "SELECT image FROM destination_images WHERE user_id = ?"
    result = db.query(sql, [user_id])
    return result[0]["image"] if result else None

def update_image(user_id, image):
    # Replace changes primary key, but it doesn't matter here.
    # Currently only one image per destination.
    sql = "INSERT OR REPLACE INTO destination_images (destination_id, image) VALUES (?, ?)"
    db.execute(sql, [user_id, image])