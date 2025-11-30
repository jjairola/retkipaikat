from flask import abort


def is_number(value):
    try:
        value = int(value)
        return True
    except:
        return False


def is_valid_required_classes(value, param):
    required_types = param.get("required_types", [])
    all_classes = param.get("all_classes", {})

    entered_types = []
    for entry in value:
        if len(entry) == 2:
            class_title, class_value = entry
            if class_title not in all_classes:
                return False
            if class_value not in all_classes[class_title]:
                return False

            entered_types.append(class_title)
        else:
            return False

    print("entered types:", entered_types)
    for required_type in required_types:
        if required_type not in entered_types:
            return False

    return True


validators = {
    "min": [lambda value, param, data: len(value) >= param, "{} on liian lyhyt."],
    "max": [lambda value, param, data: len(value) <= param, "{} on liian pitkä."],
    "number": [
        lambda value, param, data: is_number(value) == param,
        "{} pitää olla numero.",
    ],
    "required": [lambda value, param, data: len(value) > 0, "{} on pakollinen."],
    "equals": [
        lambda value, param, data: value == data.get(param, None),
        "{} eivät ole samoja.",
    ],
    "trim": [True, "For placing only front-end validation purposes. Always trimmed."],
    "word_count": [
        lambda value, param, data: len(value.split()) == param,
        "{} pitää sisältää tasan {} sanaa.",
    ],
    "require": [
        lambda value, param, data: is_valid_required_classes(value, param),
        "Luokitukset eivät ole kelvollisia.",
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
        if rules.get("require", None):
            value = [item.split(":") for item in data.getlist(key)]
        else:
            value = data[key].strip()

        for validator, param in rules.items():
            if validator == "translation":
                continue
            is_valid = validators[validator][0](value, param, data)
            if not is_valid:
                translated_key = rules.get("translation", key)
                errors[key] = validators[validator][1].format(translated_key, param)
                break
            else:
                validated[key] = value

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
        {"username": "jyrki a", "username2": "sjdg", "password": "", "test": "3"},
        schema,
    )

    print(errors)
