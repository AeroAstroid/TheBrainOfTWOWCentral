def try_func(attempt, on_error):
    try:
        return attempt
    except Exception:
        return on_error
