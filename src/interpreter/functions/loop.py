def loop(amount, functions):
    results = []
    for i in range(amount):
        for func in functions:
            # result = Expression(func, codebase)
            if func is not None:  # VOID Function
                results.append(func)

    if len(results) > 0:
        return results
