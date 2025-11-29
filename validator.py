def is_number(value):
    try:
        value = int(value)
        return True
    except:
        return False


validators = {
    "min_length": [lambda value, param, dto: len(value) >= param, "{} on liian lyhyt."],
    "max_length": [lambda value, param, dto: len(value) <= param, "{} on liian pitkä."],
    "is_number": [
        lambda value, param, dto: is_number(value) == param,
        "{} pitää olla numero.",
    ],
    "is_required": [lambda value, param, dto: len(value) > 0, "{} on pakollinen."],
    "equals": [
        lambda value, param, dto: value == dto.get(param, None),
        "{} eivät ole samoja.",
    ],
}


def validator(data, schema):
    errors = {}
    for key, schemas in schema.items():
        for validator, param in schemas.items():
            if validator == "translation":
                continue
            valid = validators[validator][0](data[key], param, data)
            if not valid:
                translated_key = schemas.get("translation", key)
                errors[key] = validators[validator][1].format(translated_key)
                break

    return errors if len(errors.keys()) else None


# Tests: python3 validator.py
if __name__ == "__main__":
    schema = {
        "username": {"min_length": 6, "translation": "salasana"},
        "password": {"min_length": 8},
        "test": {"is_number": True},
        "username2": {"equals": "username"},
    }
    errors = validator(
        {"username": "jyrki", "username2": "sjdg", "password": "", "test": "3"}, schema
    )

    print(errors)

    
