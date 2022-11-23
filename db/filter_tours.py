import datetime

from tortoise.expressions import Q
from tortoise.query_utils import Prefetch
from tortoise.queryset import QuerySet

from db.models import Tour, Date, Direction


def filter_tours(sales: bool = False, date_from: tuple[int, int, int] = None,
                 date_to: tuple[int, int, int] = None, directions_id: list[int] = None, price: int = None) -> QuerySet:
    dates_args = [Q(dates__places__gt=0), Q(dates__start__gte=datetime.datetime.now().date()), Q(dates__not_isnull=True)]

    if sales:
        dates_args.append(Q(dates__sale__gt=0))
    if date_from:
        dates_args.append(Q(dates__start__gte=datetime.datetime(*date_from).date()))
    if date_to:
        dates_args.append(Q(dates__end__lte=datetime.datetime(*date_to).date()))
    if price:
        dates_args.append(Q(dates__price__lte=price))

    if directions_id:

        queryset: QuerySet = Tour.filter(
            Q(Q(moderate=True), Q(active=True), Q(direction__id__in=directions_id), *dates_args)
        ).distinct()
    else:

        queryset: QuerySet = Tour.filter(
            Q(Q(moderate=True), Q(active=True), *dates_args)
        ).distinct()

    return queryset
