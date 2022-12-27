def div(dividend, *divisors):
    result = dividend

    for divisor in divisors:
        result /= divisor
    return result
