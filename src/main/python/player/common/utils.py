import fractions
from functools import lru_cache


def cached_property(getter):
    return property(lru_cache()(getter))


def fraction_string_to_float(string):
    splitted = string.split("/")
    length = len(splitted)
    if length == 1:
        return float(splitted)
    elif length == 2:
        numerator, denominator = (int(n) for n in splitted)
        return float(fractions.Fraction(numerator, denominator))
    elif length != 0:
        raise RuntimeError(f"Error parsing value: {string}")
