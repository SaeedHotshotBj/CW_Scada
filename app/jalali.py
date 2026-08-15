import jdatetime
from datetime import date, datetime


def jalali_to_gregorian(value):
    if not value:
        return None

    text = str(value).strip().replace('/', '-')
    parts = text.split('-')
    if len(parts) != 3:
        raise ValueError('Invalid Jalali date. Use YYYY/MM/DD.')

    year, month, day = (int(x) for x in parts)
    return jdatetime.date(year, month, day).togregorian()


def to_jalali(value):
    if not value:
        return ''

    if isinstance(value, datetime):
        return jdatetime.datetime.fromgregorian(datetime=value).strftime('%Y/%m/%d')

    if isinstance(value, date):
        return jdatetime.date.fromgregorian(date=value).strftime('%Y/%m/%d')

    text = str(value).strip()
    if not text:
        return ''

    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%Y/%m/%d'):
        try:
            parsed = datetime.strptime(text, fmt)
            return jdatetime.datetime.fromgregorian(datetime=parsed).strftime('%Y/%m/%d')
        except ValueError:
            continue

    return text
