def div(dividend: float, *divisors: tuple[float]):
    result = dividend

    for divisor in divisors:
        result /= divisor
    return result
