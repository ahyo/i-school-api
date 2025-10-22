from math import ceil
from sqlalchemy.orm import Query


def paginate_query(query: Query, page: int, limit: int):
    count_query = query.order_by(None)
    total = count_query.count()
    if total == 0:
        return [], 0, 0
    items = query.offset((page - 1) * limit).limit(limit).all()
    total_pages = ceil(total / limit)
    return items, total, total_pages
