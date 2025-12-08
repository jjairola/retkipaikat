import db

class RatingsError(Exception):
    pass

def update_average_rating(destination_id):
    try:
        sql = """
        UPDATE destinations
        SET average_rating =
            ROUND(
                    COALESCE((
                    SELECT AVG(rating)
                    FROM comments
                    WHERE comments.destination_id = destinations.id
                ), 0),
            1)
        WHERE destinations.id = ?
        """
        db.execute(sql, [destination_id])
    except Exception as error:
        raise RatingsError(error) from error
