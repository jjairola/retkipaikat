def is_number(value):
    try:
        value = int(value)
        return True
    except:
        return False


validators = {
    "min": [lambda value, param, dto: len(value) >= param, "{} on liian lyhyt."],
    "max": [lambda value, param, dto: len(value) <= param, "{} on liian pitkä."],
    "number": [
        lambda value, param, dto: is_number(value) == param,
        "{} pitää olla numero.",
    ],
    "required": [lambda value, param, dto: len(value) > 0, "{} on pakollinen."],
    "equals": [
        lambda value, param, dto: value == dto.get(param, None),
        "{} eivät ole samoja.",
    ],
    "trim": [True, "For placing only front-end validation purposes. Always trimmed."],
    "word_count": [
        lambda value, param, dto: len(value.split()) == param,
        "{} pitää sisältää tasan {} sanaa.",
    ],
}


def schema_to_input(schema):
    inputs = {}
    for key, rules in schema.items():
        options = []
        for validator, param in rules.items():
            if validator == "required" and param is True:
                options.append("required")
            if validator == "min":
                options.append(f"minlength={param}")
            if validator == "max":
                options.append(f"maxlength={param}")
            if validator == "trim" and param is True:
                options.append('pattern="\S+"')

        inputs[key] = " ".join(options)
    return inputs


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
                errors[key] = validators[validator][1].format(translated_key, param)
                break
            else:
                validated[key] = data[key].strip()

    return validated, errors if len(errors.keys()) else None


# Tests: python3 validator.py
if __name__ == "__main__":
    schema = {
        "username": {
            "min": 6,
            "max": 12,
            "translation": "käyttäjätunnus",
            "required": True,
            "word_count": 1,
        },
        "password": {"min": 8},
        "test": {"number": True},
        "username2": {"equals": "username"},
    }
    validated, errors = validator(
        {"username": "jyrki a", "username2": "sjdg", "password": "", "test": "3"}, schema
    )

    print(errors)
