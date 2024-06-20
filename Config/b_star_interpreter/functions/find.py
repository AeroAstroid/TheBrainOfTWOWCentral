def find(list_to_find: list[any], value: any):
    if value not in list_to_find:
        return -1
    return list_to_find.index(value)
