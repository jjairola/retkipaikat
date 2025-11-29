
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
    validated = {}
    for key, rules in schema.items():
        for validator, param in rules.items():
            if validator == "translation":
                continue
            is_valid = validators[validator][0](data[key], param, data)
            if not is_valid:
                translated_key = rules.get("translation", key)
                errors[key] = validators[validator][1].format(translated_key)
                break
            else:
                validated[key] = data[key].strip()

    return validated, errors if len(errors.keys()) else None


# Tests: python3 validator.py
if __name__ == "__main__":
    schema = {
        "username": {
            "min_length": 6,
            "max_length": 12,
            "translation": "käyttäjätunnus",
        },
        "password": {"min_length": 8},
        "test": {"is_number": True},
        "username2": {"equals": "username"},
    }
    validated, errors = validator(
        {"username": "jyrki", "username2": "sjdg", "password": "", "test": "3"}, schema
    )

    print(errors)
