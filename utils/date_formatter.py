import datetime


def date_formatter(date: datetime.date):
    if date.day < 10:
        day = '0' + str(date.day)
    else:
        day = str(date.day)

    if date.month < 10:
        month = '0' + str(date.month)
    else:
        month = str(date.month)

    return f'{day}.{month}.{date.year}'
