import fractions
import sys
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


def move_window_to_center(target_win, center_of_win):
    frame_geo = target_win.frameGeometry()
    center_pos = center_of_win.geometry().center()
    frame_geo.moveCenter(center_pos)
    target_win.move(frame_geo.topLeft())


class _Platform:
    @cached_property
    def is_mac(self):
        return sys.platform == "darwin"

    @cached_property
    def is_linux(self):
        return sys.platform == "linux"

    @cached_property
    def is_windows(self):
        return sys.platform == "win32"


platform = _Platform()
