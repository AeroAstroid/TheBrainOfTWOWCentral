def round_func(number):
    # 0.5 gives 0 for some reason, but since B++ was the same we'll keep it
    # in function_deco.py its returning a special formatting for "round", maybe that's the source of the issue?
    return round(number)
    #inferno, 11/27/21: no, it's just how rounding works in Python.