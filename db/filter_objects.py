import datetime

from tortoise.expressions import Q
from tortoise.queryset import QuerySet
from db.models import Object

from utils.price_buttons import PriceButtons


def filter_objects(sales: bool = False, date: tuple[int, int, int] = None,
                   districts_id: list = None, prices: list[str] = None) -> QuerySet:
    args = [
        Q(active=True)
    ]

    if sales:
        args.append(Q(sale=True))
    if date:
        args.append(Q(date__lte=datetime.datetime(*date).date()))
    if districts_id:
        args.append(Q(district__id__in=districts_id))
    if prices:
        prices_args = []
        for price in prices:
            price_args = []
            price_low, price_up = PriceButtons.buttons[price]
            if price_up:
                price_args.append(Q(price__lte=price_up))

            if price_low:
                price_args.append(Q(price__gte=price_low))
            prices_args.append(Q(*price_args))
        args.append(Q(*prices_args, join_type='OR'))

    queryset: QuerySet = Object.filter(*args).distinct()

    return queryset



