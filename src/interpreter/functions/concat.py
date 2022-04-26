def concat(*items):
    if isinstance(items[0], list):
        if not isinstance(items, tuple):
            raise TypeError("Cannot CONCAT with mixed types")

        flatitems = map(str, [item for sublist in items for item in sublist])
        buffer = "".join(flatitems)
    else:
        # make sure all items are strings
        converted_items = map(str, items)
        buffer = "".join(converted_items)

    return buffer
