import jdatetime
from datetime import datetime, date


def _digits(value):
    return str(value).translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))


def jalali_to_gregorian(value):
    value = _digits(value).strip().replace("-", "/")
    y, m, d = [int(x) for x in value.split("/")[:3]]
    return jdatetime.date(y, m, d).togregorian()


def gregorian_to_jalali(value):
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        return jdatetime.date.fromgregorian(date=value).strftime("%Y/%m/%d")
    return str(value)
