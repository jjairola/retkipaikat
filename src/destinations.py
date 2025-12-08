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
    except Exception as error:
        raise DestinationError(error) from error


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
            d.average_rating,
            di.image IS NOT NULL AS has_image
    FROM destinations d
    JOIN users u ON d.user_id = u.id
    LEFT JOIN destination_classes dc ON d.id = dc.destination_id
    LEFT JOIN comments c ON d.id = c.destination_id
    LEFT JOIN destination_images di ON d.id = di.destination_id
    """

    conditions = []
    params = []
    if user_id is not None:
        conditions.append("d.user_id = ?")
        params.append(user_id)

    if destination_id is not None:
        conditions.append("d.id = ?")
        params.append(destination_id)

    if query_text is not None:
        conditions.append("(d.name LIKE ? OR d.description LIKE ?)")
        params.extend([f"%{query_text}%", f"%{query_text}%"])

    if query_class is not None:
        destination_ids = get_destionation_ids_by_class(
            query_class["title"], query_class["value"]
        )
        if destination_ids is None:
            return []
        conditions.append("d.id IN (" + ",".join(["?" for _ in destination_ids]) + ")")
        params.extend(destination_ids)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += """
    GROUP BY d.id
    ORDER BY average_rating DESC
    """

    if page is not None and page_size is not None:
        limit = page_size
        offset = page_size * (page - 1)

        sql += "LIMIT ? OFFSET ?"
        params.extend([limit, offset])

    rows = db.query(sql, params)

    results = []
    for row in rows:
        result = dict(row)
        if "classes" in row.keys() and row["classes"] is not None:
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


def get_destionation_ids_by_class(title, value):
    sql = """
    SELECT destination_id FROM destination_classes
    WHERE title = ? AND value = ?
    """
    rows = db.query(sql, [title, value])
    dest_ids = [str(row["destination_id"]) for row in rows]
    return dest_ids if len(dest_ids) else None


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
    except Exception as error:
        raise DestinationError(error) from error


def delete_destination(destination_id):
    try:
        sql = "DELETE FROM comments WHERE destination_id = ?"
        db.execute(sql, [destination_id])

        sql = "DELETE FROM destination_classes WHERE destination_id = ?"
        db.execute(sql, [destination_id])

        sql = "DELETE FROM destination_images WHERE destination_id = ?"
        db.execute(sql, [destination_id])

        sql = "DELETE FROM destinations WHERE id = ?"
        db.execute(sql, [destination_id])
    except Exception as error:
        raise DestinationError(error) from error


def get_image(destination_id):
    sql = "SELECT image FROM destination_images WHERE destination_id = ?"
    result = db.query(sql, [destination_id])
    return result[0]["image"] if result else None


def update_image(user_id, destination_id, image):
    sql = """INSERT OR REPLACE INTO destination_images
    (user_id, destination_id, image) VALUES (?, ?, ?)"""
    db.execute(sql, [user_id, destination_id, image])
