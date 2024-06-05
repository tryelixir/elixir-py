def camel_to_snake(s):
    def camel_to_snake_helper(camel_string: str) -> str:
        if not camel_string:
            return ""
        elif camel_string[0].isupper():
            return (
                f"_{camel_string[0].lower()}{camel_to_snake_helper(camel_string[1:])}"
            )
        else:
            return f"{camel_string[0]}{camel_to_snake_helper(camel_string[1:])}"

    if len(s) <= 1:
        return s.lower()

    return camel_to_snake_helper(s[0].lower() + s[1:])
