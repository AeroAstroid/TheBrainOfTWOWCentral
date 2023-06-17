import random


def choose(*arr):
    # Check if the first element of arr is a list or tuple
    if len(arr) == 1 and isinstance(arr[0], (list, tuple)):
        # Use the elements of the list or tuple for random selection
        items = arr[0]
    else:
        # Use the elements of arr for random selection
        items = arr

    # Get a random index within the range of the items' length
    rand = random.randint(0, len(items) - 1)
    # Return the randomly selected item
    return items[rand]