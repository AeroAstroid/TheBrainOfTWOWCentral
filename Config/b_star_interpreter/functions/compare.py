# TODO: Inspect types further
def compare(v1: float, operator: str, v2: float):
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
