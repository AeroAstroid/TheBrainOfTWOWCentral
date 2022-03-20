def compare(v1, operator, v2):
    if operator == ">":
        return v1 > v2
    elif operator == "<":
        return v1 < v2
    elif operator == ">=":
        return v1 >= v2
    elif operator == "<=":
        return v1 <= v2
    elif operator == "=" or "==":
        return v1 == v2
    elif operator == "!=":
        return v1 != v2
