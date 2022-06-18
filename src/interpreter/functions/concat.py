def concat(*items):
    if isinstance(items[0], list):
        valid = True
        for it in items:
            if not isinstance(it, list):
                valid = False
                break
        
        if valid:
            return sum(items, []) # Flattens one level deep


    # make sure all items are strings
    converted_items = map(str, items)
    buffer = "".join(converted_items)

    return buffer
