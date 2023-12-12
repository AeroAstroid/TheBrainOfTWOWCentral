import typing


def compare(v1: str | int | float | bool, operator: str, v2: str | int | float | bool):
    match operator:
        case ">":
            result = v1 > v2
        case "<":
            result = v1 < v2
        case ">=":
            result = v1 >= v2
        case "<=":
            result = v1 <= v2
        case "=" | "==":
            result = v1 == v2
        case "!=":
            result = v1 != v2
        case _:
            raise NotImplementedError(f"operator '{operator}' not implemented")

    return int(result)
