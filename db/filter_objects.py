import datetime

from tortoise.expressions import Q
from tortoise.queryset import QuerySet
from db.models import Object

from utils.price_buttons import PriceButtons


def filter_objects(sales: bool = False, date: tuple[int, int, int] = None,
                   districts_id: list = None, price: str = None) -> QuerySet:
    args = [
        Q(active=True)
    ]

    if sales:
        args.append(Q(sale=True))
    if date:
        args.append(Q(date__lte=datetime.datetime(*date).date()))
    if districts_id:
        args.append(Q(district__id__in=districts_id))
    if price:
        price_low, price_up = PriceButtons.buttons[price]
        if price_up:
            args.append(Q(price__lte=price_up))

        if price_low:
            args.append(Q(price__gte=price_low))

    queryset: QuerySet = Object.filter(*args).distinct()

    return queryset


