import jdatetime


def jalali_to_gregorian(value):
    value = value.replace('-', '/').replace('.', '/')
    parts = value.split('/')
    if len(parts) != 3:
        return None
    jy, jm, jd = map(int, parts)
    return jdatetime.date(jy, jm, jd).togregorian()


def gregorian_to_jalali(value):
    if not value:
        return ''
    d = value if hasattr(value, 'year') else value.date()
    j = jdatetime.date.fromgregorian(date=d)
    return f'{j.year:04d}/{j.month:02d}/{j.day:02d}'
