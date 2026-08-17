from datetime import date

from powerball.models import Draw, parse_white


def make_draw(year: int, month: int, day: int, whites, powerball: int, multiplier=None) -> Draw:
    return Draw(date(year, month, day), parse_white(whites), powerball, multiplier)
