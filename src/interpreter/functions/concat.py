def concat(item, *items):
    if isinstance(item, list):
        if not isinstance(items, tuple):
            raise TypeError("Cannot CONCAT with mixed types")

        flatitems = [item for sublist in items for item in sublist]
        buffer = item + flatitems
    else:
        buffer = item + "".join(items)

    return buffer
