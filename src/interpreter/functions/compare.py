def comparevals(v1, operator, v2):
    if operator == ">":
        return v1 > v2
    elif operator == "<":
        return v1 < v2
    elif operator == ">=":
        return v1 >= v2
    elif operator == "<=":
        return v1 <= v2
    elif operator == "=" or operator == "==":
        return v1 == v2
    elif operator == "!=":
        return v1 != v2

def compare(v1, operator, v2):
    if comparevals(v1, operator, v2):
        return 1
    return 0
